#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concurrency Manager for PyArchInit
Handles concurrent modifications and version conflicts

Created by: Assistant
Date: 2024
"""

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt

class ConcurrencyManager:
    """Manager for handling concurrent database modifications"""

    def __init__(self, parent=None):
        self.parent = parent
        # Try to get database username first, then OS username
        self.current_user = None
        self.db_username = None  # Will be set when connecting to DB

    def check_version_conflict(self, table_name, record_id, current_version, db_manager, id_field=None):
        """
        Check if there's a version conflict for a record

        Args:
            table_name: Name of the table
            record_id: ID of the record
            current_version: Version number currently in the form
            db_manager: Database manager instance
            id_field: Name of the ID field (optional, will be guessed if not provided)

        Returns:
            dict with conflict info or None
        """
        try:
            # Determine ID field name
            if not id_field:
                # Common patterns for ID fields in PyArchInit
                id_field_mappings = {
                    'us_table': 'id_us',
                    'tma_materiali_archeologici': 'id',
                    'inventario_materiali_table': 'id_invmat',
                    'site_table': 'id_sito',
                    'tomba_table': 'id_tomba',
                    'struttura_table': 'id_struttura',
                    'periodizzazione_table': 'id_perfass',
                    'individui_table': 'id_scheda_ind',
                    'campioni_table': 'id_campione',
                    'documentazione_table': 'id_documentazione',
                    'detsesso_table': 'id_det_sesso',
                    'deteta_table': 'id_det_eta',
                    'archeozoology_table': 'id_archzoo',
                    'pottery_table': 'id_rep'
                }
                id_field = id_field_mappings.get(table_name, f"id_{table_name.replace('_table', '')}")

            # Get current version from database
            query = f"""
                SELECT version_number, last_modified_by, last_modified_timestamp
                FROM {table_name}
                WHERE {id_field} = {record_id}
            """

            result = db_manager.query_sql(query)
            if result:
                db_version = result[0][0]
                last_modified_by = result[0][1]
                last_modified_timestamp = result[0][2]

                has_conflict = (db_version != current_version) if db_version else False

                return has_conflict, db_version, last_modified_by, last_modified_timestamp
        except Exception as e:
            print(f"Error checking version conflict: {str(e)}")

        return False, None, None, None

    def handle_conflict(self, table_name, record_data, conflict_info):
        """
        Handle a version conflict

        Args:
            table_name: Name of the table
            record_data: Current form data
            conflict_info: Information about the conflict

        Returns:
            User's choice ('overwrite', 'reload', 'cancel')
        """
        db_version, last_modified_by, last_modified_timestamp = conflict_info

        dialog = ConflictResolutionDialog(
            self.parent,
            table_name,
            record_data,
            last_modified_by,
            last_modified_timestamp
        )

        result = dialog.exec_()

        if result == QDialog.Accepted:
            return dialog.get_choice()

        return 'cancel'

    def _get_id_field(self, table_name):
        """Get the correct ID field name for a table"""
        id_field_mappings = {
            'us_table': 'id_us',
            'tma_materiali_archeologici': 'id',
            'inventario_materiali_table': 'id_invmat',
            'site_table': 'id_sito',
            'tomba_table': 'id_tomba',
            'struttura_table': 'id_struttura',
            'periodizzazione_table': 'id_perfass',
            'individui_table': 'id_scheda_ind',
            'campioni_table': 'id_campione',
            'documentazione_table': 'id_documentazione',
            'detsesso_table': 'id_det_sesso',
            'deteta_table': 'id_det_eta',
            'archeozoology_table': 'id_archzoo',
            'pottery_table': 'id_rep'
        }
        return id_field_mappings.get(table_name, f"id_{table_name.replace('_table', '')}")

    def lock_record(self, table_name, record_id, db_manager):
        """
        Create a soft lock on a record (informational only)

        Args:
            table_name: Name of the table
            record_id: ID of the record
            db_manager: Database manager instance
        """
        try:
            if not self.current_user:
                print(f"ConcurrencyManager: No username set, cannot lock record")
                return False

            id_field = self._get_id_field(table_name)
            query = f"""
                UPDATE {table_name}
                SET editing_by = '{self.current_user}',
                    editing_since = CURRENT_TIMESTAMP
                WHERE {id_field} = {record_id}
            """
            db_manager.execute_sql(query)
            print(f"ConcurrencyManager: Locked {table_name} record {record_id} for user {self.current_user}")
            return True
        except Exception as e:
            print(f"ConcurrencyManager: Error locking record - {e}")
            return False

    def unlock_record(self, table_name, record_id, db_manager):
        """
        Remove soft lock from a record

        Args:
            table_name: Name of the table
            record_id: ID of the record
            db_manager: Database manager instance
        """
        try:
            id_field = self._get_id_field(table_name)
            query = f"""
                UPDATE {table_name}
                SET editing_by = NULL,
                    editing_since = NULL
                WHERE {id_field} = {record_id}
            """
            db_manager.execute_sql(query)
            print(f"ConcurrencyManager: Unlocked {table_name} record {record_id}")
            return True
        except Exception as e:
            print(f"ConcurrencyManager: Error unlocking record - {e}")
            return False

    def get_active_editors(self, table_name, record_id, db_manager):
        """
        Get list of users currently editing a record

        Args:
            table_name: Name of the table
            record_id: ID of the record
            db_manager: Database manager instance

        Returns:
            List of tuples (username, editing_since)
        """
        try:
            query = f"""
                SELECT editing_by, editing_since
                FROM {table_name}
                WHERE id_{table_name.replace('_table', '')} = {record_id}
                AND editing_by IS NOT NULL
                AND editing_since > CURRENT_TIMESTAMP - INTERVAL '30 minutes'
            """

            result = db_manager.query_sql(query)
            return result if result else []
        except Exception as e:
            return []

    def set_username(self, username):
        """Set the current username for the session"""
        self.current_user = username
        self.db_username = username

    def get_username(self):
        """Get the current username, preferring database username over OS username"""
        if self.db_username:
            return self.db_username
        elif self.current_user:
            return self.current_user
        else:
            # Fallback to OS username
            return os.environ.get('USER', 'unknown')


class ConflictResolutionDialog(QDialog):
    """Dialog for resolving version conflicts"""

    def __init__(self, parent, table_name, record_data, last_modified_by, last_modified_timestamp):
        super().__init__(parent)
        self.choice = 'cancel'
        self.init_ui(table_name, record_data, last_modified_by, last_modified_timestamp)

    def init_ui(self, table_name, record_data, last_modified_by, last_modified_timestamp):
        """Initialize the UI"""
        self.setWindowTitle("Conflitto di Versione / Version Conflict")
        self.setModal(True)
        self.resize(600, 400)

        layout = QVBoxLayout()

        # Warning message
        warning_label = QLabel()
        warning_text = (
            f"<b>ATTENZIONE: Conflitto di modifica rilevato!</b><br><br>"
            f"Il record è stato modificato da <b>{last_modified_by}</b> "
            f"alle <b>{last_modified_timestamp}</b>.<br><br>"
            f"Le tue modifiche potrebbero sovrascrivere quelle dell'altro utente."
        )
        warning_label.setText(warning_text)
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)

        # Show current data (could be expanded to show differences)
        data_text = QTextEdit()
        data_text.setReadOnly(True)
        data_text.setPlainText(f"Tabella: {table_name}\n\nDati attuali nel form:\n{str(record_data)[:500]}...")
        layout.addWidget(data_text)

        # Buttons
        button_layout = QHBoxLayout()

        reload_btn = QPushButton("Ricarica dal Database")
        reload_btn.setToolTip("Scarta le tue modifiche e ricarica i dati aggiornati dal database")
        reload_btn.clicked.connect(self.reload_choice)
        button_layout.addWidget(reload_btn)

        overwrite_btn = QPushButton("Sovrascrivi")
        overwrite_btn.setToolTip("Salva comunque le tue modifiche (sovrascrive i cambiamenti dell'altro utente)")
        overwrite_btn.setStyleSheet("background-color: #ff6b6b;")
        overwrite_btn.clicked.connect(self.overwrite_choice)
        button_layout.addWidget(overwrite_btn)

        cancel_btn = QPushButton("Annulla")
        cancel_btn.setToolTip("Non fare nulla, torna al form")
        cancel_btn.clicked.connect(self.cancel_choice)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def reload_choice(self):
        """User chose to reload from database"""
        self.choice = 'reload'
        self.accept()

    def overwrite_choice(self):
        """User chose to overwrite"""
        self.choice = 'overwrite'
        self.accept()

    def cancel_choice(self):
        """User chose to cancel"""
        self.choice = 'cancel'
        self.reject()

    def get_choice(self):
        """Get the user's choice"""
        return self.choice


class RecordLockIndicator:
    """Visual indicator for record locks"""

    def __init__(self, parent_widget):
        """
        Initialize lock indicator

        Args:
            parent_widget: The form widget to attach the indicator to
        """
        self.parent = parent_widget
        self.lock_label = None

    def show_lock_status(self, editors):
        """
        Show who's currently editing the record

        Args:
            editors: List of (username, editing_since) tuples
        """
        if not self.lock_label:
            from PyQt5.QtWidgets import QLabel
            self.lock_label = QLabel(self.parent)
            self.lock_label.setStyleSheet("""
                QLabel {
                    background-color: #fff3cd;
                    border: 1px solid #ffc107;
                    padding: 5px;
                    border-radius: 3px;
                }
            """)

        if editors:
            editor_list = ", ".join([f"{user} (da {since})" for user, since in editors])
            self.lock_label.setText(f"⚠️ In modifica da: {editor_list}")
            self.lock_label.show()
        else:
            self.lock_label.hide()

    def clear_lock_status(self):
        """Clear the lock status indicator"""
        if self.lock_label:
            self.lock_label.hide()