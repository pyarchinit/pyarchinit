#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        PyArchInit Plugin - Advanced Backup/Restore Dialog
                             -------------------
        begin                : 2024
        copyright            : (C) 2024 by PyArchInit
        email                : pyarchinit@gmail.com
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

import os
import sys
import time
import subprocess
import shutil
from datetime import datetime, timedelta
import json

from qgis.PyQt.QtCore import Qt, QTimer, pyqtSignal, QThread, QDate, QDateTime
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                 QPushButton, QProgressBar, QTextEdit, QGroupBox,
                                 QCalendarWidget, QListWidget, QListWidgetItem,
                                 QMessageBox, QFileDialog, QComboBox, QCheckBox,
                                 QGridLayout, QWidget, QSplitter)
from qgis.PyQt.QtGui import QTextCharFormat, QColor, QFont, QPalette
from qgis.core import QgsSettings, QgsMessageLog, Qgis

from ..modules.db.pyarchinit_conn_strings import Connection
from ..modules.utility.settings import Settings


class BackupWorker(QThread):
    """Worker thread for backup operations"""
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    size_update = pyqtSignal(int)

    def __init__(self, command, env):
        super().__init__()
        self.command = command
        self.env = env

    def run(self):
        """Execute backup command"""
        try:
            self.message.emit("Avvio backup...")

            # Start process
            process = subprocess.Popen(
                self.command,
                env=self.env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Monitor process
            while process.poll() is None:
                time.sleep(0.5)
                # Simulate progress (real pg_dump doesn't provide progress)
                self.progress.emit(50)

            # Check result
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                self.progress.emit(100)
                self.message.emit("Backup completato con successo!")
                self.finished.emit(True, "Backup completato")
            else:
                self.message.emit(f"Errore backup: {stderr}")
                self.finished.emit(False, stderr)

        except Exception as e:
            self.message.emit(f"Errore: {str(e)}")
            self.finished.emit(False, str(e))


class BackupRestoreDialog(QDialog):
    """Advanced Backup/Restore Dialog with calendar and progress tracking"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestione Backup Database")
        self.resize(900, 600)

        self.HOME = os.environ.get('PYARCHINIT_HOME', os.path.expanduser('~'))
        self.backup_dir = os.path.join(self.HOME, 'pyarchinit_db_backup')

        # Create backup directory if not exists
        os.makedirs(self.backup_dir, exist_ok=True)

        # Store backup info
        self.backup_info = self.load_backup_info()

        self.init_ui()
        self.load_settings()
        self.update_backup_list()
        self.update_calendar()

    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout()

        # Database info section
        info_group = QGroupBox("Informazioni Database")
        info_layout = QGridLayout()

        self.db_type_label = QLabel("Tipo: ")
        self.db_name_label = QLabel("Database: ")
        self.db_host_label = QLabel("Host: ")
        self.db_size_label = QLabel("Dimensione: ")

        info_layout.addWidget(self.db_type_label, 0, 0)
        info_layout.addWidget(self.db_name_label, 0, 1)
        info_layout.addWidget(self.db_host_label, 1, 0)
        info_layout.addWidget(self.db_size_label, 1, 1)

        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # Splitter for calendar and backup list
        splitter = QSplitter(Qt.Horizontal)

        # Calendar section
        calendar_widget = QWidget()
        calendar_layout = QVBoxLayout()
        calendar_layout.addWidget(QLabel("📅 Calendario Backup"))

        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.on_date_selected)
        calendar_layout.addWidget(self.calendar)

        # Legend
        legend_layout = QHBoxLayout()

        backup_label = QLabel("● Backup esistente")
        backup_label.setStyleSheet("color: green;")
        legend_layout.addWidget(backup_label)

        missing_label = QLabel("● Backup rimosso")
        missing_label.setStyleSheet("color: orange;")
        legend_layout.addWidget(missing_label)

        calendar_layout.addLayout(legend_layout)
        calendar_widget.setLayout(calendar_layout)
        splitter.addWidget(calendar_widget)

        # Backup list section
        list_widget = QWidget()
        list_layout = QVBoxLayout()
        list_layout.addWidget(QLabel("📦 Backup Disponibili"))

        self.backup_list = QListWidget()
        self.backup_list.itemClicked.connect(self.on_backup_selected)
        list_layout.addWidget(self.backup_list)

        # Backup info
        self.backup_info_text = QTextEdit()
        self.backup_info_text.setMaximumHeight(100)
        self.backup_info_text.setReadOnly(True)
        list_layout.addWidget(self.backup_info_text)

        list_widget.setLayout(list_layout)
        splitter.addWidget(list_widget)

        main_layout.addWidget(splitter)

        # Progress section
        progress_group = QGroupBox("Progresso Operazione")
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Pronto")
        self.size_label = QLabel("")

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.size_label)

        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)

        # Buttons section
        button_layout = QHBoxLayout()

        self.backup_btn = QPushButton("🔵 Esegui Backup")
        self.backup_btn.clicked.connect(self.perform_backup)
        self.backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)

        self.restore_btn = QPushButton("🟢 Ripristina Backup")
        self.restore_btn.clicked.connect(self.perform_restore)
        self.restore_btn.setEnabled(False)
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)

        self.delete_btn = QPushButton("🗑️ Elimina Backup")
        self.delete_btn.clicked.connect(self.delete_backup)
        self.delete_btn.setEnabled(False)

        button_layout.addWidget(self.backup_btn)
        button_layout.addWidget(self.restore_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def load_settings(self):
        """Load database settings"""
        try:
            conn = Connection()
            conn_dict = conn.conn_str_dict()

            self.db_type = conn_dict.get('server', 'unknown')
            self.db_name = conn_dict.get('database', 'unknown')
            self.db_host = conn_dict.get('host', 'localhost')
            self.db_port = conn_dict.get('port', '5432')
            self.db_user = conn_dict.get('user', 'postgres')
            self.db_password = conn_dict.get('password', '')

            # Update labels
            self.db_type_label.setText(f"Tipo: {self.db_type.upper()}")
            self.db_name_label.setText(f"Database: {self.db_name}")
            self.db_host_label.setText(f"Host: {self.db_host}:{self.db_port}")

            # Enable/disable buttons based on DB type
            if self.db_type == 'sqlite':
                self.backup_btn.setText("📦 Backup SQLite")
                self.restore_btn.setEnabled(False)
            else:
                self.backup_btn.setText("🔵 Backup PostgreSQL")

        except Exception as e:
            QgsMessageLog.logMessage(f"Error loading settings: {str(e)}", "PyArchInit", Qgis.Warning)

    def load_backup_info(self):
        """Load backup information from JSON file"""
        info_file = os.path.join(self.backup_dir, 'backup_info.json')
        if os.path.exists(info_file):
            try:
                with open(info_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_backup_info(self):
        """Save backup information to JSON file"""
        info_file = os.path.join(self.backup_dir, 'backup_info.json')
        try:
            with open(info_file, 'w') as f:
                json.dump(self.backup_info, f, indent=2)
        except Exception as e:
            QgsMessageLog.logMessage(f"Error saving backup info: {str(e)}", "PyArchInit", Qgis.Warning)

    def update_calendar(self):
        """Update calendar to show backup dates"""
        # Reset all dates
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())

        # Scan backup directory
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.backup') or filename.endswith('.sqlite'):
                # Extract date from filename (format: dbname_YYYYMMDD_HH_MM.backup)
                try:
                    parts = filename.split('_')
                    if len(parts) >= 3:
                        date_str = parts[-3]  # YYYYMMDD
                        date = QDate.fromString(date_str, "yyyyMMdd")

                        if date.isValid():
                            format = QTextCharFormat()

                            # Check if file exists
                            file_path = os.path.join(self.backup_dir, filename)
                            if os.path.exists(file_path):
                                format.setBackground(QColor(200, 255, 200))  # Light green
                                format.setToolTip(f"Backup: {filename}")
                            else:
                                format.setBackground(QColor(255, 200, 150))  # Light orange
                                format.setToolTip(f"Backup rimosso: {filename}")

                            self.calendar.setDateTextFormat(date, format)
                except:
                    continue

    def update_backup_list(self):
        """Update the list of available backups"""
        self.backup_list.clear()

        # Get all backup files
        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.backup') or filename.endswith('.sqlite'):
                file_path = os.path.join(self.backup_dir, filename)
                size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
                mtime = os.path.getmtime(file_path)

                backups.append({
                    'filename': filename,
                    'path': file_path,
                    'size': size,
                    'mtime': mtime
                })

        # Sort by modification time (newest first)
        backups.sort(key=lambda x: x['mtime'], reverse=True)

        # Add to list
        for backup in backups:
            dt = datetime.fromtimestamp(backup['mtime'])
            item_text = f"{backup['filename']} ({backup['size']:.1f} MB)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, backup)
            self.backup_list.addItem(item)

    def on_date_selected(self, date):
        """Handle date selection in calendar"""
        # Find backups for this date
        date_str = date.toString("yyyyMMdd")

        for i in range(self.backup_list.count()):
            item = self.backup_list.item(i)
            backup = item.data(Qt.UserRole)
            if date_str in backup['filename']:
                self.backup_list.setCurrentItem(item)
                self.on_backup_selected(item)
                break

    def on_backup_selected(self, item):
        """Handle backup selection from list"""
        if item:
            backup = item.data(Qt.UserRole)

            # Show backup info
            dt = datetime.fromtimestamp(backup['mtime'])
            info = f"File: {backup['filename']}\n"
            info += f"Dimensione: {backup['size']:.2f} MB\n"
            info += f"Data creazione: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"

            self.backup_info_text.setText(info)

            # Enable restore button
            self.restore_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)

    def perform_backup(self):
        """Perform database backup"""
        try:
            if self.db_type == 'sqlite':
                self.backup_sqlite()
            else:
                self.backup_postgresql()

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il backup: {str(e)}")

    def backup_sqlite(self):
        """Backup SQLite database"""
        try:
            # Get source database path
            conn = Connection()
            conn_str = conn.conn_str()
            source_path = conn_str.replace('sqlite:///', '')

            # Create backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H_%M_%S')
            backup_filename = f"{self.db_name}_{timestamp}.sqlite"
            backup_path = os.path.join(self.backup_dir, backup_filename)

            # Copy database
            self.progress_bar.setValue(0)
            self.progress_label.setText("Copia database SQLite...")

            shutil.copy2(source_path, backup_path)

            self.progress_bar.setValue(100)
            self.progress_label.setText("Backup completato!")

            # Update info
            size = os.path.getsize(backup_path) / (1024 * 1024)
            self.size_label.setText(f"Dimensione backup: {size:.2f} MB")

            # Save backup info
            self.backup_info[backup_filename] = {
                'date': timestamp,
                'size': size,
                'type': 'sqlite'
            }
            self.save_backup_info()

            # Update UI
            self.update_backup_list()
            self.update_calendar()

            QMessageBox.information(self, "Successo", f"Backup salvato in:\n{backup_path}")

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore backup SQLite: {str(e)}")

    def backup_postgresql(self):
        """Backup PostgreSQL database"""
        try:
            # Create backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H_%M_%S')
            backup_filename = f"{self.db_name}_{timestamp}.backup"
            backup_path = os.path.join(self.backup_dir, backup_filename)

            # Build pg_dump command
            command = [
                'pg_dump',
                '-U', self.db_user,
                '-h', self.db_host,
                '-p', self.db_port,
                '-d', self.db_name,
                '-Fc',  # Custom format
                '-Z', '9',  # Max compression
                '-f', backup_path
            ]

            # Set environment with password
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_password

            # Create worker thread
            self.worker = BackupWorker(command, env)
            self.worker.progress.connect(self.progress_bar.setValue)
            self.worker.message.connect(self.progress_label.setText)
            self.worker.finished.connect(self.on_backup_finished)

            # Start backup
            self.backup_btn.setEnabled(False)
            self.worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore backup PostgreSQL: {str(e)}")
            self.backup_btn.setEnabled(True)

    def on_backup_finished(self, success, message):
        """Handle backup completion"""
        self.backup_btn.setEnabled(True)

        if success:
            # Update UI
            self.update_backup_list()
            self.update_calendar()

            # Get backup size
            if self.backup_list.count() > 0:
                item = self.backup_list.item(0)
                backup = item.data(Qt.UserRole)
                self.size_label.setText(f"Dimensione backup: {backup['size']:.2f} MB")

            QMessageBox.information(self, "Successo", "Backup completato con successo!")
        else:
            QMessageBox.critical(self, "Errore", f"Backup fallito:\n{message}")

    def perform_restore(self):
        """Perform database restore"""
        item = self.backup_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Attenzione", "Seleziona un backup da ripristinare")
            return

        backup = item.data(Qt.UserRole)

        reply = QMessageBox.question(self, "Conferma",
                                    f"Vuoi ripristinare il backup:\n{backup['filename']}?\n\n"
                                    "ATTENZIONE: Tutti i dati attuali verranno sovrascritti!",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.db_type == 'sqlite':
                self.restore_sqlite(backup['path'])
            else:
                self.restore_postgresql(backup['path'])

    def restore_sqlite(self, backup_path):
        """Restore SQLite database"""
        try:
            conn = Connection()
            conn_str = conn.conn_str()
            target_path = conn_str.replace('sqlite:///', '')

            # Backup current database before restore
            timestamp = datetime.now().strftime('%Y%m%d_%H_%M_%S')
            safety_backup = os.path.join(self.backup_dir, f"pre_restore_{timestamp}.sqlite")
            shutil.copy2(target_path, safety_backup)

            # Restore
            shutil.copy2(backup_path, target_path)

            QMessageBox.information(self, "Successo", "Database ripristinato con successo!")

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore ripristino: {str(e)}")

    def restore_postgresql(self, backup_path):
        """Restore PostgreSQL database"""
        try:
            # Build pg_restore command
            command = [
                'pg_restore',
                '-U', self.db_user,
                '-h', self.db_host,
                '-p', self.db_port,
                '-d', self.db_name,
                '-c',  # Clean before restore
                backup_path
            ]

            # Set environment with password
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_password

            # Execute restore
            self.progress_label.setText("Ripristino in corso...")
            process = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                QMessageBox.information(self, "Successo", "Database ripristinato con successo!")
            else:
                QMessageBox.critical(self, "Errore", f"Errore ripristino:\n{stderr.decode()}")

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore ripristino: {str(e)}")

    def delete_backup(self):
        """Delete selected backup"""
        item = self.backup_list.currentItem()
        if not item:
            return

        backup = item.data(Qt.UserRole)

        reply = QMessageBox.question(self, "Conferma",
                                    f"Eliminare il backup:\n{backup['filename']}?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                os.remove(backup['path'])
                self.update_backup_list()
                self.update_calendar()
                QMessageBox.information(self, "Successo", "Backup eliminato")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore eliminazione: {str(e)}")