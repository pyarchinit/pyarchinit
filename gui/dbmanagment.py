#!/usr/bin/python
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
import subprocess

import sys
import time
import shutil

from builtins import range
from builtins import str
from ..modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility
from ..modules.utility.settings import Settings
from ..modules.db.pyarchinit_conn_strings import Connection
from qgis.core import *
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QRectF, pyqtSignal, QObject, pyqtSlot, Qt, QThread, QTimer, QDate
from qgis.PyQt.QtWidgets import QApplication, QDialog, QMessageBox, QProgressDialog, QProgressBar, QWidget, QLabel, QVBoxLayout, QFileDialog, QListWidgetItem, QInputDialog, QRadioButton, QButtonGroup, QDialogButtonBox, QGroupBox, QLineEdit
from qgis.PyQt.QtGui import QTextCharFormat, QColor, QFont
from qgis.PyQt.uic import loadUiType
from datetime import datetime

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'dbmanagment.ui'))


class BackupThread(QThread):
    """Thread for running backup operations with progress tracking"""
    progress_update = pyqtSignal(int)
    message_update = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, command, env, file_path):
        super().__init__()
        self.command = command
        self.env = env
        self.file_path = file_path
        self.process = None

    def run(self):
        """Run the backup command"""
        try:
            self.message_update.emit("Avvio backup...")

            # Start the backup process
            self.process = subprocess.Popen(
                self.command,
                env=self.env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Monitor file size growth for progress
            start_time = time.time()
            max_time = 300  # Max 5 minutes

            while self.process.poll() is None:
                # Check file size
                if os.path.exists(self.file_path):
                    file_size = os.path.getsize(self.file_path) / (1024 * 1024)  # MB
                    self.message_update.emit(f"Backup in corso... {file_size:.1f} MB")

                # Calculate progress based on time (since pg_dump doesn't provide progress)
                elapsed = time.time() - start_time
                progress = min(int((elapsed / 60) * 90), 90)  # Max 90% during backup
                self.progress_update.emit(progress)

                time.sleep(1)

                if elapsed > max_time:
                    self.process.terminate()
                    self.finished_signal.emit(False, "Timeout backup (>5 minuti)")
                    return

            # Get result
            stdout, stderr = self.process.communicate()

            if self.process.returncode == 0:
                self.progress_update.emit(100)
                file_size = os.path.getsize(self.file_path) / (1024 * 1024)
                self.finished_signal.emit(True, f"Backup completato: {file_size:.2f} MB")
            else:
                error = stderr.decode('utf-8') if stderr else "Errore sconosciuto"
                self.finished_signal.emit(False, error)

        except Exception as e:
            self.finished_signal.emit(False, str(e))


class pyarchinit_dbmanagment(QDialog, MAIN_DIALOG_CLASS):
    
    MSG_BOX_TITLE = \
        'PyArchInit - pyarchinit_version 0.4 - Scheda gestione DB'
    HOME = os.environ['PYARCHINIT_HOME']
    BK = '{}{}{}'.format(HOME, os.sep, "pyarchinit_db_backup")
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setupUi(self)

        # Initialize database configuration
        self.load_db_config()

        # Connect buttons
        self.backup.clicked.connect(self.on_backup_pressed)
        self.backupsqlite.clicked.connect(self.on_backupsqlite_pressed)
        self.upload.clicked.connect(self.on_upload_pressed)
        self.restore.clicked.connect(self.on_restore_pressed)

        # Connect calendar and list
        if hasattr(self, 'calendarWidget'):
            self.calendarWidget.clicked.connect(self.on_calendar_date_selected)
        if hasattr(self, 'listWidget_backups'):
            self.listWidget_backups.itemClicked.connect(self.on_backup_selected)

        # Setup GUI based on database type
        self.setup_gui_by_db_type()

        # Load backup list and update calendar
        self.update_backup_list()
        self.update_calendar()

        self.currentLayerId = None
        
    def load_db_config(self):
        """Load database configuration from config file"""
        try:
            cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
            file_path = '{}{}'.format(self.HOME, cfg_rel_path)

            if os.path.exists(file_path):
                with open(file_path, "r") as conf:
                    data = conf.read()
                    settings = Settings(data)
                    settings.set_configuration()

                    self.db_type = settings.SERVER
                    self.db_name = settings.DATABASE
                    self.db_user = settings.USER
                    self.db_host = settings.HOST
                    self.db_port = settings.PORT
                    self.db_password = settings.PASSWORD
            else:
                # Default to postgres if no config
                self.db_type = 'postgres'

        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Errore caricamento configurazione: {str(e)}")
            self.db_type = 'postgres'

    def setup_gui_by_db_type(self):
        """Setup GUI elements based on database type"""
        if self.db_type == 'sqlite':
            # SQLite configuration
            self.backup.setEnabled(False)  # Disable PostgreSQL backup
            self.backupsqlite.setEnabled(True)  # Enable SQLite backup
            self.restore.setEnabled(False)  # Disable restore for SQLite
            self.upload.setEnabled(False)  # Disable upload for SQLite

            # Update labels
            self.label_17.setText("Database: SQLite")

        else:  # PostgreSQL
            self.backup.setEnabled(True)  # Enable PostgreSQL backup
            self.backupsqlite.setEnabled(False)  # Disable SQLite backup
            self.restore.setEnabled(False)  # Initially disabled until backup is selected
            self.upload.setEnabled(True)  # Enable upload to select backup file

            # Update labels
            self.label_17.setText(f"Database: PostgreSQL ({self.db_name})")

    def enable_button(self, n):
        self.backup.setEnabled(n)

    def enable_button_search(self, n):
        self.backup.setEnabled(n)

    
    
    
    
    def on_backupsqlite_pressed(self):
        conn = Connection()
        conn_str = conn.conn_str()
        
        a = conn_str.lstrip('sqlite:///')
        home = os.environ['PYARCHINIT_HOME']
        # conn_import = '%s%s%s' % (home, os.sep,
                                  # 'pyarchinit_DB_folder/pyarchinit_db.sqlite'
                                  # )
        
        
        
        #conn_export = '%s%s%s' % (home, os.sep,
                                  #'pyarchinit_db_backup/pyarchinit_db_'
                                  #+ time.strftime('%Y%m%d_%H_%M_%S_')
                                  #+ '.sqlite')
       
        
        PDF_path = '%s%s%s' % (home, os.sep, 'pyarchinit_db_backup/')
        
        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(home, cfg_rel_path)
        conf = open(file_path, "r")

        data = conf.read()
        settings = Settings(data)
        settings.set_configuration()
        conf.close()    
        
        dump_dir = PDF_path
        db_username = settings.USER
        host = settings.HOST
        port = settings.PORT
        database_password=settings.PASSWORD
        
        db_names = settings.DATABASE
        bkp_file = 'backup_%s_%s.sqlite' % (db_names, time.strftime('%Y%m%d_%H_%M'))
        conn_export = os.path.join(dump_dir, bkp_file)
                                 
        try:
            # Copy SQLite database
            b = shutil.copy(a, conn_export)

            # Update progress bar
            self.progressBar_db.setMinimum(0)
            self.progressBar_db.setMaximum(100)
            self.progressBar_db.setValue(100)

            # Show success message
            file_size = os.path.getsize(conn_export) / (1024 * 1024)
            QMessageBox.information(self, "Successo",
                f"Backup SQLite completato!\n\n"
                f"File: {os.path.basename(conn_export)}\n"
                f"Dimensione: {file_size:.2f} MB",
                QMessageBox.Ok)

            # Update backup list and calendar
            self.update_backup_list()
            self.update_calendar()

        except Exception as e:
            QMessageBox.critical(self, "Errore",
                f"Backup SQLite fallito!\n{str(e)}",
                QMessageBox.Ok)
            
    def on_backup_pressed(self):

        home = os.environ['PYARCHINIT_HOME']

        PDF_path = '%s%s%s' % (home, os.sep, 'pyarchinit_db_backup/')

        # Create backup directory if not exists
        os.makedirs(PDF_path, exist_ok=True)

        cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
        file_path = '{}{}'.format(home, cfg_rel_path)
        conf = open(file_path, "r")

        data = conf.read()
        settings = Settings(data)
        settings.set_configuration()
        conf.close()

        dump_dir = PDF_path
        db_username = settings.USER
        host = settings.HOST
        port = settings.PORT
        database_password=settings.PASSWORD

        db_names = settings.DATABASE

        bkp_file = '%s_%s.backup' % (db_names,
                                  time.strftime('%Y%m%d_%H_%M'))

        file_path = os.path.join(dump_dir, bkp_file)

        # Build command as list for subprocess
        command = [
            'pg_dump',
            '-U', db_username,
            '-h', host,
            '-p', port,
            '-Z', '9',  # Compression level
            '-f', file_path,
            '-Fc',  # Custom format
            db_names
        ]

        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = database_password

        try:
            p = subprocess.Popen(command, env=env, shell=False,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            QMessageBox.warning(self, "ERRORE",
                "pg_dump non trovato. Assicurati che PostgreSQL sia installato e nel PATH.",
                QMessageBox.Ok)
            return
        except Exception as e:
            QMessageBox.warning(self, "ERRORE", str(e), QMessageBox.Ok)
            return
        # Create and start backup thread
        self.backup_thread = BackupThread(command, env, file_path)
        self.backup_thread.progress_update.connect(self.update_progress)
        self.backup_thread.message_update.connect(self.update_message)
        self.backup_thread.finished_signal.connect(self.backup_finished)

        # Setup progress bar
        self.progressBar_db.setMinimum(0)
        self.progressBar_db.setMaximum(100)
        self.progressBar_db.setValue(0)

        # Disable backup button during operation
        self.backup.setEnabled(False)

        # Start backup
        self.backup_thread.start()

    def update_progress(self, value):
        """Update progress bar"""
        self.progressBar_db.setValue(value)

        # Update format string if file exists
        if hasattr(self, 'backup_thread') and self.backup_thread and os.path.exists(self.backup_thread.file_path):
            file_size = os.path.getsize(self.backup_thread.file_path) / (1024 * 1024)
            self.progressBar_db.setFormat(f"%p% - {file_size:.1f} MB")

    def update_message(self, message):
        """Update status message"""
        if hasattr(self, 'label_status'):
            self.label_status.setText(message)

    def backup_finished(self, success, message):
        """Handle backup completion"""
        self.backup.setEnabled(True)

        if success:
            # Extract file info
            file_path = self.backup_thread.file_path
            file_name = os.path.basename(file_path)

            QMessageBox.information(self, "Successo",
                f"Backup completato con successo!\n\n"
                f"File: {file_name}\n"
                f"{message}",
                QMessageBox.Ok)

            # Update backup list and calendar after successful backup
            self.update_backup_list()
            self.update_calendar()
        else:
            self.progressBar_db.setValue(0)
            QMessageBox.critical(self, "Errore Backup",
                f"Backup fallito!\n\n{message}",
                QMessageBox.Ok)

    def update_backup_list(self):
        """Update the list of available backups"""
        if not hasattr(self, 'listWidget_backups'):
            return

        self.listWidget_backups.clear()

        # Create backup directory if not exists
        os.makedirs(self.BK, exist_ok=True)

        # Get all backup files
        backup_files = []
        for filename in os.listdir(self.BK):
            if filename.endswith('.backup') or filename.endswith('.sqlite'):
                file_path = os.path.join(self.BK, filename)
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                file_time = os.path.getmtime(file_path)

                backup_files.append({
                    'name': filename,
                    'path': file_path,
                    'size': file_size,
                    'time': file_time
                })

        # Sort by time (newest first)
        backup_files.sort(key=lambda x: x['time'], reverse=True)

        # Add to list widget
        for backup in backup_files:
            dt = datetime.fromtimestamp(backup['time'])
            item_text = f"{backup['name']}\n  📦 {backup['size']:.1f} MB - 📅 {dt.strftime('%Y-%m-%d %H:%M')}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, backup)
            self.listWidget_backups.addItem(item)

    def update_calendar(self):
        """Update calendar to show backup dates"""
        if not hasattr(self, 'calendarWidget'):
            return

        # Reset all date formats
        self.calendarWidget.setDateTextFormat(QDate(), QTextCharFormat())

        # Mark today's date
        today_format = QTextCharFormat()
        today_format.setBackground(QColor(200, 200, 255))
        today_format.setFontWeight(QFont.Bold)
        self.calendarWidget.setDateTextFormat(QDate.currentDate(), today_format)

        # Mark dates with backups
        for filename in os.listdir(self.BK):
            if filename.endswith('.backup') or filename.endswith('.sqlite'):
                # Extract date from filename (format: dbname_YYYYMMDD_HH_MM.backup)
                try:
                    # Remove extension
                    name_without_ext = filename.rsplit('.', 1)[0]
                    parts = name_without_ext.split('_')

                    # Try to find YYYYMMDD pattern in parts
                    for part in parts:
                        if len(part) == 8 and part.isdigit():
                            date = QDate.fromString(part, "yyyyMMdd")

                            if date.isValid():
                                # Create format for backup date
                                backup_format = QTextCharFormat()
                                backup_format.setBackground(QColor(200, 255, 200))
                                backup_format.setToolTip(f"Backup: {filename}")

                                # Apply format to date
                                self.calendarWidget.setDateTextFormat(date, backup_format)
                                break
                except Exception as e:
                    print(f"Error parsing date from {filename}: {e}")

    def on_calendar_date_selected(self, date):
        """Handle calendar date selection"""
        if not hasattr(self, 'listWidget_backups'):
            return

        # Find backups for selected date
        date_str = date.toString("yyyyMMdd")

        for i in range(self.listWidget_backups.count()):
            item = self.listWidget_backups.item(i)
            backup = item.data(Qt.UserRole)

            if date_str in backup['name']:
                # Select this item
                self.listWidget_backups.setCurrentItem(item)
                self.on_backup_selected(item)
                break

    def on_backup_selected(self, item):
        """Handle backup selection from list"""
        if not item:
            return

        backup = item.data(Qt.UserRole)

        # Show backup info
        if hasattr(self, 'textEdit_info'):
            dt = datetime.fromtimestamp(backup['time'])
            info = f"📁 File: {backup['name']}\n"
            info += f"📦 Dimensione: {backup['size']:.2f} MB\n"
            info += f"📅 Data creazione: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            info += f"📂 Percorso: {backup['path']}"

            self.textEdit_info.setText(info)

        # Set path for restore
        self.lineEdit_bk_path.setText(backup['path'])
        self.restore.setEnabled(True)
    # def on_backup_total_pressed(self):

        # home = os.environ['PYARCHINIT_HOME']
        # PDF_path = '%s%s%s' % (home, os.sep, 'pyarchinit_db_backup/')
        # filename = '%s%s%s' % (PDF_path, os.sep, 'semivariogramma.png')

        # username = 'postgres'

        # defaultdb = 'postgres'

        # port = '5432'

        # backupdir = PDF_path

        # date = time.strftime('%Y-%m-%d-%H-%M-%S')

        # GET DB NAMES

        # get_db_names = \
            # "psql -U%s -d%s -p%s --tuples-only -c '\l' | awk -F\| '{ print $1 }' | grep -E -v '(template0|template1|^$)'" \
            # % (username, defaultdb, port)

        # MAKE BACKUP OF SYSTEMGRANTS

        # os.popen('pg_dumpall -p%s -g|gzip -9 -c > %s/system.%s.gz'
                 # % (port, backupdir, date))

        # MAKING DB BACKUP

        # for base in os.popen(get_db_names).readlines():
            # try:

                # app = QtGui.QApplication(sys.argv)

                # barra = QProgressBar(self)
                # barra.show()
                # barra.setMinimum(0)
                # barra.setMaximum(9)
                # for a in range(10):
                    # time.sleep(1)
                    # barra.setValue(a)

                # app.exec_()....

                # base = base.strip()
                # fulldir = backupdir + base
                # if not os.path.exists(fulldir):
                    # os.mkdir(fulldir)
                # filename = '%s/%s-%s.sql' % (fulldir, base, date)
                # os.popen('nice -n 19 pg_dump -C -F c -U%s -p%s %s > %s'
                         # % (username, port, base, filename))
                # QMessageBox.warning(self, 'Messaggio',
                                    # 'Backup completato', QMessageBox.Ok)
            # except Exception as e:
                # QMessageBox.warning(self, 'Messaggio',
                                    # 'Backup fallito!!' + str(e),
                                    # QMessageBox.Ok)

    
    def on_upload_pressed(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Seleziona file backup",
            self.BK,
            "Backup files (*.backup *.sql)"
        )[0]

        if dbpath:
            self.lineEdit_bk_path.setText(dbpath)
            s.setValue('pyArchInit/last_backup_path', dbpath)

            # Enable restore button when a backup is selected
            self.restore.setEnabled(True)

            # Show file info
            file_size = os.path.getsize(dbpath) / (1024 * 1024)  # MB
            file_name = os.path.basename(dbpath)
            QMessageBox.information(self, "File selezionato",
                f"Backup: {file_name}\nDimensione: {file_size:.2f} MB")
        
    def show_restore_options_dialog(self, current_db_name):
        """Show dialog to choose restore options"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Opzioni Ripristino")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        # Info label
        info_label = QLabel("Scegli come ripristinare il backup:")
        info_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # Radio buttons group
        group_box = QGroupBox("Opzioni:")
        group_layout = QVBoxLayout()

        # Radio buttons
        radio_overwrite = QRadioButton(f"Sovrascrivi database esistente ({current_db_name})")
        radio_overwrite.setChecked(True)
        radio_new = QRadioButton("Crea nuovo database")

        button_group = QButtonGroup(dialog)
        button_group.addButton(radio_overwrite, 0)
        button_group.addButton(radio_new, 1)

        group_layout.addWidget(radio_overwrite)
        group_layout.addWidget(radio_new)

        # New database name input
        new_db_layout = QVBoxLayout()
        new_db_label = QLabel("Nome nuovo database:")
        new_db_input = QLineEdit()
        new_db_input.setPlaceholderText("es: pyarchinit_restored")
        new_db_input.setText(f"{current_db_name}_restored")
        new_db_input.setEnabled(False)

        new_db_layout.addWidget(new_db_label)
        new_db_layout.addWidget(new_db_input)
        group_layout.addLayout(new_db_layout)

        group_box.setLayout(group_layout)
        layout.addWidget(group_box)

        # Warning label
        warning_label = QLabel("⚠️ ATTENZIONE: Sovrascrivere eliminerà tutti i dati attuali!")
        warning_label.setStyleSheet("color: red; margin-top: 10px;")
        layout.addWidget(warning_label)

        # Enable/disable new db input based on selection
        def on_radio_changed():
            new_db_input.setEnabled(radio_new.isChecked())
            if radio_new.isChecked():
                warning_label.setText("ℹ️ Verrà creato un nuovo database con i dati del backup")
                warning_label.setStyleSheet("color: blue; margin-top: 10px;")
            else:
                warning_label.setText("⚠️ ATTENZIONE: Sovrascrivere eliminerà tutti i dati attuali!")
                warning_label.setStyleSheet("color: red; margin-top: 10px;")

        radio_overwrite.toggled.connect(on_radio_changed)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QDialog.Accepted:
            if radio_new.isChecked():
                new_name = new_db_input.text().strip()
                if not new_name:
                    QMessageBox.warning(self, "Errore", "Inserisci un nome per il nuovo database")
                    return None
                return ('new', new_name)
            else:
                return ('overwrite', current_db_name)

        return None

    def on_restore_pressed(self):
        try:
            path = self.lineEdit_bk_path.text()

            if not path or not os.path.exists(path):
                QMessageBox.warning(self, 'Errore',
                    'Seleziona un file di backup valido', QMessageBox.Ok)
                return

            home = os.environ['PYARCHINIT_HOME']

            cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
            file_path = '{}{}'.format(home, cfg_rel_path)
            conf = open(file_path, "r")

            data = conf.read()
            settings = Settings(data)
            settings.set_configuration()
            conf.close()

            # Get database parameters
            db_username = self.lineEdit_username_wt.text() or settings.USER
            host = self.lineEdit_host_wt.text() or settings.HOST
            port = self.lineEdit_port_wt.text() or settings.PORT
            database_password = self.lineEdit_pass_wt.text() or settings.PASSWORD
            current_db_name = self.lineEdit_database_wt.text() or settings.DATABASE

            # Show restore options dialog
            restore_option = self.show_restore_options_dialog(current_db_name)

            if not restore_option:
                return

            mode, db_names = restore_option

            # Final confirmation
            if mode == 'overwrite':
                reply = QMessageBox.question(self, 'Conferma',
                    f'ATTENZIONE: Stai per SOVRASCRIVERE il database "{db_names}"!\n'
                    'Tutti i dati attuali verranno ELIMINATI!\n\n'
                    'Sei sicuro di voler continuare?',
                    QMessageBox.Yes | QMessageBox.No)
            else:
                reply = QMessageBox.question(self, 'Conferma',
                    f'Verrà creato un nuovo database "{db_names}" con i dati del backup.\n\n'
                    'Vuoi continuare?',
                    QMessageBox.Yes | QMessageBox.No)

            if reply != QMessageBox.Yes:
                return

            # Set PGPASSWORD environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = database_password

            # Setup progress bar
            self.progress = self.progressBar_db
            self.progress.setMinimum(0)
            self.progress.setMaximum(0)  # Indeterminate
            self.progress.show()

            # Update status
            if hasattr(self, 'label_status'):
                self.label_status.setText("Preparazione database...")

            if mode == 'overwrite':
                # Step 1: Drop existing database
                drop_cmd = ['dropdb', '-h', host, '-p', port, '-U', db_username, '--if-exists', db_names]
                subprocess.run(drop_cmd, env=env, capture_output=True)
            else:
                # Check if new database already exists
                check_cmd = ['psql', '-h', host, '-p', port, '-U', db_username, '-lqt']
                result = subprocess.run(check_cmd, env=env, capture_output=True, text=True)

                if db_names in result.stdout:
                    self.progress.setMaximum(100)
                    self.progress.setValue(0)
                    QMessageBox.warning(self, 'Errore',
                        f'Il database "{db_names}" esiste già!\n'
                        'Scegli un nome diverso o seleziona sovrascrittura.',
                        QMessageBox.Ok)
                    return

            # Step 2: Create database
            create_cmd = ['createdb', '-h', host, '-p', port, '-U', db_username,
                         '-E', 'UTF8', '-T', 'template_postgis', db_names]
            result = subprocess.run(create_cmd, env=env, capture_output=True, text=True)

            if result.returncode != 0 and 'template_postgis' in result.stderr:
                # Try without template_postgis and add extensions manually
                create_cmd = ['createdb', '-h', host, '-p', port, '-U', db_username,
                             '-E', 'UTF8', db_names]
                create_result = subprocess.run(create_cmd, env=env, capture_output=True, text=True)

                # If database created successfully, add PostGIS extension
                if create_result.returncode == 0:
                    # Update status
                    if hasattr(self, 'label_status'):
                        self.label_status.setText("Installazione PostGIS...")

                    # Add PostGIS extension
                    add_postgis_cmd = ['psql', '-h', host, '-p', port, '-U', db_username, '-d', db_names,
                                     '-c', 'CREATE EXTENSION IF NOT EXISTS postgis;']
                    subprocess.run(add_postgis_cmd, env=env, capture_output=True)

                    # Add PostGIS topology extension (optional but useful)
                    add_topology_cmd = ['psql', '-h', host, '-p', port, '-U', db_username, '-d', db_names,
                                      '-c', 'CREATE EXTENSION IF NOT EXISTS postgis_topology;']
                    subprocess.run(add_topology_cmd, env=env, capture_output=True)

            # Step 3: Restore database
            if hasattr(self, 'label_status'):
                self.label_status.setText("Ripristino dati in corso...")

            restore_cmd = ['pg_restore', '--host', host, '--port', port,
                          '--username', db_username, '--dbname', db_names,
                          '--no-owner', '--no-acl', '--if-exists', '--clean', path]

            result = subprocess.run(restore_cmd, env=env, capture_output=True, text=True)

            self.progress.setMaximum(100)
            self.progress.setValue(100)

            # Check and create user tables if missing
            if hasattr(self, 'label_status'):
                self.label_status.setText("Verifica tabelle utenti e sequenze...")

            # Fix duplicate triggers and sequences after restore
            fix_sequences_sql = """
            -- Remove duplicate audit triggers first
            DO $$
            DECLARE
                r RECORD;
            BEGIN
                FOR r IN
                    SELECT DISTINCT tgrelid::regclass::text as table_name
                    FROM pg_trigger
                    WHERE tgname = 'audit_trigger'
                    AND EXISTS (
                        SELECT 1 FROM pg_trigger t2
                        WHERE t2.tgrelid = pg_trigger.tgrelid
                        AND t2.tgname LIKE 'audit_%'
                        AND t2.tgname != 'audit_trigger'
                    )
                LOOP
                    EXECUTE format('DROP TRIGGER IF EXISTS audit_trigger ON %I', r.table_name);
                END LOOP;
            END $$;
            -- Fix audit_log sequence
            DO $$
            DECLARE
                max_id INTEGER;
            BEGIN
                SELECT COALESCE(MAX(id), 0) INTO max_id FROM audit_log;
                PERFORM setval('audit_log_id_seq', max_id + 1, false);
            EXCEPTION WHEN undefined_table THEN
                -- Table doesn't exist, ignore
            END $$;

            -- Fix pyarchinit_users sequence
            DO $$
            DECLARE
                max_id INTEGER;
            BEGIN
                SELECT COALESCE(MAX(id), 0) INTO max_id FROM pyarchinit_users;
                PERFORM setval('pyarchinit_users_id_seq', max_id + 1, false);
            EXCEPTION WHEN undefined_table THEN
                -- Table doesn't exist, ignore
            END $$;

            -- Fix pyarchinit_activity_log sequence
            DO $$
            DECLARE
                max_id INTEGER;
            BEGIN
                SELECT COALESCE(MAX(id), 0) INTO max_id FROM pyarchinit_activity_log;
                PERFORM setval('pyarchinit_activity_log_id_seq', max_id + 1, false);
            EXCEPTION WHEN undefined_table THEN
                -- Table doesn't exist, ignore
            END $$;

            -- Fix pyarchinit_user_permissions sequence
            DO $$
            DECLARE
                max_id INTEGER;
            BEGIN
                SELECT COALESCE(MAX(id), 0) INTO max_id FROM pyarchinit_user_permissions;
                PERFORM setval('pyarchinit_user_permissions_id_seq', max_id + 1, false);
            EXCEPTION WHEN undefined_table THEN
                -- Table doesn't exist, ignore
            END $$;
            """

            fix_seq_cmd = ['psql', '-h', host, '-p', port, '-U', db_username, '-d', db_names,
                          '-c', fix_sequences_sql]
            subprocess.run(fix_seq_cmd, env=env, capture_output=True)

            # Create user management tables if they don't exist
            check_tables_sql = """
            CREATE TABLE IF NOT EXISTS pyarchinit_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL,
                active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS pyarchinit_user_permissions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES pyarchinit_users(id) ON DELETE CASCADE,
                table_name VARCHAR(100) NOT NULL,
                can_insert BOOLEAN DEFAULT false,
                can_update BOOLEAN DEFAULT false,
                can_delete BOOLEAN DEFAULT false,
                can_view BOOLEAN DEFAULT true,
                UNIQUE(user_id, table_name)
            );

            CREATE TABLE IF NOT EXISTS pyarchinit_activity_log (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES pyarchinit_users(id),
                action VARCHAR(50) NOT NULL,
                table_name VARCHAR(100),
                record_id INTEGER,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Create admin user if no users exist
            INSERT INTO pyarchinit_users (username, password, role)
            SELECT 'admin', 'pbkdf2:sha256:600000$IqSk5QXQNygjH6AS$88f93e88643e64d3efdfd74bc9cf57c99e35e4e36797fb8de7e3a685c90c4f8f', 'admin'
            WHERE NOT EXISTS (SELECT 1 FROM pyarchinit_users WHERE username = 'admin');
            """

            check_tables_cmd = ['psql', '-h', host, '-p', port, '-U', db_username, '-d', db_names,
                              '-c', check_tables_sql]
            subprocess.run(check_tables_cmd, env=env, capture_output=True)

            # Analyze restore output
            critical_errors = []
            warnings = []

            if result.stderr:
                for line in result.stderr.split('\n'):
                    if 'ERROR' in line:
                        # Ignore non-critical errors
                        if any(ignore in line for ignore in [
                            'already exists',
                            'must be owner',
                            'does not exist',
                            'duplicate key'
                        ]):
                            warnings.append(line)
                        else:
                            critical_errors.append(line)

            if critical_errors:
                # Show only first 5 critical errors
                error_msg = "Ripristino fallito con errori critici:\n\n"
                error_msg += "\n".join(critical_errors[:5])
                if len(critical_errors) > 5:
                    error_msg += f"\n... e altri {len(critical_errors)-5} errori"
                QMessageBox.critical(self, 'Errore', error_msg, QMessageBox.Ok)
            else:
                # Restore successful or with only warnings
                message = f'Ripristino completato con successo!\n\n'
                if mode == 'new':
                    message += f'Nuovo database creato: {db_names}\n\n'
                    message += f'Per utilizzarlo, aggiorna la configurazione in PyArchInit.'

                if warnings:
                    message += f'\n\nNota: Alcuni oggetti esistevano già e sono stati ignorati.'

                QMessageBox.information(self, 'Successo', message, QMessageBox.Ok)

        except Exception as e:
            self.progress.setMaximum(100)
            self.progress.setValue(0)
            QMessageBox.critical(self, 'Errore',
                f'Ripristino fallito!\n{str(e)}', QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = pyarchinit_dbmanagment()
    ui.show()
    sys.exit(app.exec_())
