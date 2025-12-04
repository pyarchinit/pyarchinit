#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
User Management Dialog for PyArchInit Admin
"""

from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                            QTableWidget, QTableWidgetItem, QPushButton,
                            QLineEdit, QComboBox, QCheckBox, QLabel,
                            QGroupBox, QMessageBox, QHeaderView, QFormLayout,
                            QTextEdit, QSplitter, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont
from qgis.core import QgsSettings
import hashlib
import getpass
from datetime import datetime

class UserManagementDialog(QDialog):
    """Dialog per gestione utenti e permessi - Solo per Admin"""

    user_changed = pyqtSignal()  # Segnale quando cambiano utenti/permessi

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        # Get database username from QGIS settings, fallback to OS username
        s = QgsSettings()
        self.current_user = s.value('pyArchInit/current_user', '', type=str)
        if not self.current_user:
            # Fallback: try to get from database connection
            self.current_user = getpass.getuser()
        # Also store the database connection username
        self.db_username = self._get_db_username()

        # Verifica se l'utente è admin
        if not self.check_admin_access():
            QMessageBox.critical(self, "Accesso Negato",
                               "Solo gli amministratori possono accedere a questa funzione")
            self.close()
            return

        self.init_ui()
        self.load_data()

    def _get_db_username(self):
        """Get the database connection username"""
        # First try from settings (saved by pyarchinitConfigDialog)
        try:
            s = QgsSettings()
            db_username = s.value('pyArchInit/db_username', '', type=str)
            if db_username:
                return db_username
        except:
            pass

        # Fallback: query database directly
        try:
            query = "SELECT current_user"
            result = self.db_manager.execute_sql(query)
            if result and result[0][0]:
                return result[0][0]
        except:
            pass
        return ''

    def check_admin_access(self):
        """Verifica se l'utente corrente è admin"""
        # Debug info
        print(f"Admin access check - current_user: {self.current_user}, db_username: {self.db_username}")

        # Prima verifica: se siamo collegati come 'postgres' (superuser database)
        if self.db_username:
            db_user_lower = self.db_username.lower()
            if db_user_lower == 'postgres' or db_user_lower.startswith('postgres.'):
                print(f"Admin access granted - database superuser: {self.db_username}")
                return True

        # Seconda verifica: controlla nella tabella pyarchinit_users
        try:
            # Check if table exists first
            check_table = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'pyarchinit_users'
                )
            """
            table_exists = self.db_manager.execute_sql(check_table)

            if not table_exists or not table_exists[0][0]:
                # Table doesn't exist - allow admin for initial setup
                print("Admin access granted - pyarchinit_users table doesn't exist")
                return True

            # Query per verificare ruolo admin - check both current_user and db_username
            usernames_to_check = [self.current_user, self.db_username]
            usernames_to_check = [u for u in usernames_to_check if u]  # Remove empty strings

            for username in usernames_to_check:
                query = """
                    SELECT role FROM pyarchinit_users
                    WHERE LOWER(username) = LOWER(:username) AND is_active = TRUE
                """
                result = self.db_manager.execute_sql(query, {'username': username})
                if result and len(result) > 0:
                    if result[0][0] == 'admin':
                        print(f"Admin access granted - user '{username}' has admin role")
                        return True
                    else:
                        print(f"Admin access denied - user '{username}' has role: {result[0][0]}")
                        return False

            # User not found in table
            print(f"Admin access denied - user not found in pyarchinit_users")
            return False

        except Exception as e:
            # If query fails, allow admin for backward compatibility
            print(f"Admin check query failed ({e}), defaulting to admin")
            return True

    def init_ui(self):
        """Inizializza interfaccia"""
        self.setWindowTitle("🛡️ Gestione Utenti e Permessi - PyArchInit")
        self.setMinimumSize(1200, 700)

        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("👤 GESTIONE UTENTI E PERMESSI")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3;")
        header_layout.addWidget(title)

        # Show both PyArchInit user and database user for clarity
        user_display = self.current_user if self.current_user else self.db_username
        db_display = f" [DB: {self.db_username}]" if self.db_username and self.db_username != user_display else ""
        self.status_label = QLabel(f"Connesso come: {user_display}{db_display} (Admin)")
        self.status_label.setStyleSheet("color: green;")
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)

        layout.addLayout(header_layout)

        # Tab widget
        self.tabs = QTabWidget()

        # Tab 1: Gestione Utenti
        self.users_tab = self.create_users_tab()
        self.tabs.addTab(self.users_tab, "👥 Utenti")

        # Tab 2: Gestione Permessi
        self.permissions_tab = self.create_permissions_tab()
        self.tabs.addTab(self.permissions_tab, "🔐 Permessi")

        # Tab 3: Monitor Attività
        self.monitor_tab = self.create_monitor_tab()
        self.tabs.addTab(self.monitor_tab, "📊 Monitor")

        # Tab 4: Ruoli
        self.roles_tab = self.create_roles_tab()
        self.tabs.addTab(self.roles_tab, "👔 Ruoli")

        layout.addWidget(self.tabs)

        # Footer buttons
        footer_layout = QHBoxLayout()

        self.init_db_btn = QPushButton("🔧 Inizializza Database Utenti")
        self.init_db_btn.clicked.connect(self.initialize_user_tables)
        self.init_db_btn.setStyleSheet("background-color: #FF9800; color: white;")

        self.refresh_btn = QPushButton("🔄 Aggiorna")
        self.refresh_btn.clicked.connect(self.load_data)

        self.close_btn = QPushButton("❌ Chiudi")
        self.close_btn.clicked.connect(self.close)

        footer_layout.addWidget(self.init_db_btn)
        footer_layout.addWidget(self.refresh_btn)
        footer_layout.addStretch()
        footer_layout.addWidget(self.close_btn)

        layout.addLayout(footer_layout)
        self.setLayout(layout)

    def create_users_tab(self):
        """Crea tab gestione utenti"""
        widget = QWidget()
        layout = QHBoxLayout()

        # Left: User list
        left_panel = QGroupBox("Lista Utenti")
        left_layout = QVBoxLayout()

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels(["Username", "Nome", "Ruolo", "Email", "Attivo"])
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.itemSelectionChanged.connect(self.on_user_selected)

        left_layout.addWidget(self.users_table)

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_user_btn = QPushButton("➕ Nuovo Utente")
        self.add_user_btn.clicked.connect(self.add_new_user)
        self.delete_user_btn = QPushButton("🗑️ Elimina")
        self.delete_user_btn.clicked.connect(self.delete_user)
        self.refresh_btn = QPushButton("🔄 Aggiorna")
        self.refresh_btn.clicked.connect(self.load_data)

        btn_layout.addWidget(self.add_user_btn)
        btn_layout.addWidget(self.delete_user_btn)
        btn_layout.addWidget(self.refresh_btn)
        left_layout.addLayout(btn_layout)

        left_panel.setLayout(left_layout)

        # Right: User details
        right_panel = QGroupBox("Dettagli Utente")
        right_layout = QFormLayout()

        self.username_edit = QLineEdit()
        self.fullname_edit = QLineEdit()
        self.email_edit = QLineEdit()

        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "responsabile", "archeologo", "studente", "guest"])

        self.active_check = QCheckBox("Utente Attivo")

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Lascia vuoto per non cambiare")

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)

        right_layout.addRow("Username:", self.username_edit)
        right_layout.addRow("Password:", self.password_edit)
        right_layout.addRow("Nome Completo:", self.fullname_edit)
        right_layout.addRow("Email:", self.email_edit)
        right_layout.addRow("Ruolo:", self.role_combo)
        right_layout.addRow("Stato:", self.active_check)
        right_layout.addRow("Note:", self.notes_edit)

        # Last login info
        self.last_login_label = QLabel("-")
        right_layout.addRow("Ultimo Accesso:", self.last_login_label)

        # Add save button for user
        self.save_user_btn = QPushButton("💾 Salva Utente")
        self.save_user_btn.clicked.connect(self.save_changes)
        self.save_user_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        right_layout.addRow("", self.save_user_btn)

        right_panel.setLayout(right_layout)

        # Add to main layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)
        widget.setLayout(layout)

        return widget

    def create_permissions_tab(self):
        """Crea tab gestione permessi"""
        widget = QWidget()
        layout = QVBoxLayout()

        # User selector
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Utente:"))

        self.perm_user_combo = QComboBox()
        self.perm_user_combo.currentTextChanged.connect(self.load_user_permissions)
        top_layout.addWidget(self.perm_user_combo)

        self.perm_role_label = QLabel()
        self.perm_role_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        top_layout.addWidget(self.perm_role_label)

        top_layout.addStretch()

        self.apply_to_all_btn = QPushButton("📋 Applica a Tutte le Tabelle")
        self.apply_to_all_btn.clicked.connect(self.apply_permissions_to_all)
        top_layout.addWidget(self.apply_to_all_btn)

        # Add save button for permissions
        self.save_permissions_btn = QPushButton("💾 Salva Permessi")
        self.save_permissions_btn.clicked.connect(self.save_permissions)
        self.save_permissions_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        top_layout.addWidget(self.save_permissions_btn)

        layout.addLayout(top_layout)

        # Permissions table
        self.permissions_table = QTableWidget()
        self.permissions_table.setColumnCount(6)
        self.permissions_table.setHorizontalHeaderLabels([
            "Tabella", "Visualizza", "Inserisci", "Modifica", "Elimina", "Tipo"
        ])

        header = self.permissions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        layout.addWidget(self.permissions_table)

        # Quick permissions
        quick_layout = QHBoxLayout()
        quick_layout.addWidget(QLabel("Permessi Rapidi:"))

        self.quick_view = QCheckBox("Visualizza")
        self.quick_insert = QCheckBox("Inserisci")
        self.quick_update = QCheckBox("Modifica")
        self.quick_delete = QCheckBox("Elimina")

        quick_layout.addWidget(self.quick_view)
        quick_layout.addWidget(self.quick_insert)
        quick_layout.addWidget(self.quick_update)
        quick_layout.addWidget(self.quick_delete)

        quick_layout.addStretch()
        layout.addLayout(quick_layout)

        widget.setLayout(layout)
        return widget

    def create_monitor_tab(self):
        """Crea tab monitor attività"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Real-time monitor
        monitor_group = QGroupBox("🔴 Monitor Real-Time")
        monitor_layout = QVBoxLayout()

        self.monitor_table = QTableWidget()
        self.monitor_table.setColumnCount(7)
        self.monitor_table.setHorizontalHeaderLabels([
            "Utente", "Tabella", "Record", "Azione", "Da Minuti", "IP", "Stato"
        ])

        monitor_layout.addWidget(self.monitor_table)

        # Auto-refresh
        refresh_layout = QHBoxLayout()
        self.auto_refresh_check = QCheckBox("Auto-refresh ogni 10 secondi")
        self.auto_refresh_check.stateChanged.connect(self.toggle_auto_refresh)
        refresh_layout.addWidget(self.auto_refresh_check)

        self.force_unlock_btn = QPushButton("🔓 Sblocca Record Selezionato")
        self.force_unlock_btn.clicked.connect(self.force_unlock_record)
        refresh_layout.addStretch()
        refresh_layout.addWidget(self.force_unlock_btn)

        monitor_layout.addLayout(refresh_layout)
        monitor_group.setLayout(monitor_layout)
        layout.addWidget(monitor_group)

        # Access log
        log_group = QGroupBox("📜 Log Accessi (ultime 24 ore)")
        log_layout = QVBoxLayout()

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(6)
        self.log_table.setHorizontalHeaderLabels([
            "Timestamp", "Utente", "Azione", "Tabella", "Successo", "Errore"
        ])

        log_layout.addWidget(self.log_table)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        widget.setLayout(layout)
        return widget

    def create_roles_tab(self):
        """Crea tab gestione ruoli"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Roles table
        self.roles_table = QTableWidget()
        self.roles_table.setColumnCount(7)
        self.roles_table.setHorizontalHeaderLabels([
            "Ruolo", "Descrizione", "Visualizza", "Inserisci", "Modifica", "Elimina", "Sistema"
        ])

        layout.addWidget(self.roles_table)

        # Info
        info_label = QLabel(
            "ℹ️ I ruoli di sistema (admin) non possono essere modificati.\n"
            "I permessi dei ruoli sono i default applicati agli utenti con quel ruolo."
        )
        info_label.setStyleSheet("background-color: #E3F2FD; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)

        widget.setLayout(layout)
        return widget

    def load_data(self):
        """Carica tutti i dati"""
        self.load_users()
        self.load_roles()
        self.load_monitor()
        self.load_access_log()

    def load_users(self):
        """Carica lista utenti"""
        try:
            # Prima verifica se la tabella esiste
            check_table = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'pyarchinit_users'
                )
            """
            exists = self.db_manager.execute_sql(check_table)

            if not exists or not exists[0][0]:
                # Tabella non esiste, mostra messaggio
                self.users_table.setRowCount(1)
                self.users_table.setItem(0, 0, QTableWidgetItem("Tabella utenti non trovata"))
                self.users_table.setItem(0, 1, QTableWidgetItem("Esegui prima lo script di aggiornamento database"))
                return

            query = """
                SELECT username, full_name, role, email, is_active, last_login, notes
                FROM pyarchinit_users
                ORDER BY username
            """
            users = self.db_manager.execute_sql(query)

            if not users:
                users = []  # Lista vuota se non ci sono utenti

            self.users_table.setRowCount(len(users) if users else 0)

            # Clear and repopulate combo boxes if they exist
            if hasattr(self, 'perm_user_combo'):
                self.perm_user_combo.clear()

            for i, user in enumerate(users if users else []):
                self.users_table.setItem(i, 0, QTableWidgetItem(user[0]))
                self.users_table.setItem(i, 1, QTableWidgetItem(user[1] or ""))
                self.users_table.setItem(i, 2, QTableWidgetItem(user[2]))
                self.users_table.setItem(i, 3, QTableWidgetItem(user[3] or ""))

                active_item = QTableWidgetItem("✓" if user[4] else "✗")
                active_item.setTextAlignment(Qt.AlignCenter)
                if not user[4]:
                    active_item.setBackground(QBrush(QColor(255, 200, 200)))
                self.users_table.setItem(i, 4, active_item)

                # Add to combo box if it exists
                if hasattr(self, 'perm_user_combo'):
                    self.perm_user_combo.addItem(user[0])

        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Errore caricamento utenti: {e}")

    def load_user_permissions(self):
        """Carica permessi utente selezionato"""
        username = self.perm_user_combo.currentText()
        if not username:
            return

        try:
            # Get user role
            query = "SELECT role FROM pyarchinit_users WHERE username = :username"
            result = self.db_manager.execute_sql(query, {'username': username})
            if result:
                self.perm_role_label.setText(f"Ruolo: {result[0][0]}")

            # First check if user has any custom permissions
            query = """
                SELECT table_name, can_view, can_insert, can_update, can_delete
                FROM pyarchinit_permissions p
                JOIN pyarchinit_users u ON p.user_id = u.id
                WHERE u.username = :username
                ORDER BY table_name
            """
            permissions = self.db_manager.execute_sql(query, {'username': username})

            # If no custom permissions, create default based on role
            if not permissions:
                # Get user role to determine default permissions
                role_query = "SELECT role FROM pyarchinit_users WHERE username = :username"
                role_result = self.db_manager.execute_sql(role_query, {'username': username})

                if role_result and len(role_result) > 0:
                    role = role_result[0][0]

                    # Define default tables (including geometric tables)
                    tables = [
                        'us_table', 'tma_materiali_archeologici', 'inventario_materiali_table',
                        'site_table', 'periodizzazione_table', 'struttura_table', 'tomba_table',
                        'individui_table', 'campioni_table', 'documentazione_table',
                        'detsesso_table', 'deteta_table', 'archeozoology_table', 'pottery_table',
                        'pyarchinit_quote_view', 'pyarchinit_us_view', 'pyarchinit_site_view',
                        'pyarchinit_strutture_view', 'pyarchinit_reperti_view', 'pyarchinit_tombe_view',
                        'pyarchinit_pyuscarlinee', 'pyarchinit_pyuscarassoc', 'pyarchinit_pysiti_polygon',
                        'pyarchinit_pyripartizioni', 'pyarchinit_pysiti_point'
                    ]

                    # Create default permissions based on role
                    permissions = []
                    for table in tables:
                        if role == 'admin':
                            permissions.append([table, True, True, True, True, False])
                        elif role == 'responsabile':
                            permissions.append([table, True, True, True, False, False])
                        elif role == 'archeologo':
                            permissions.append([table, True, True, False, False, False])
                        elif role == 'studente':
                            permissions.append([table, True, False, False, False, False])
                        else:  # guest
                            permissions.append([table, True, False, False, False, False])
                else:
                    permissions = []

            self.permissions_table.setRowCount(len(permissions))

            for i, perm in enumerate(permissions):
                # Table name
                self.permissions_table.setItem(i, 0, QTableWidgetItem(perm[0]))

                # Checkboxes for permissions
                for j, value in enumerate(perm[1:5], 1):
                    checkbox = QCheckBox()
                    checkbox.setChecked(value)
                    self.permissions_table.setCellWidget(i, j, checkbox)

                # Permission type (custom if from DB, default if generated)
                is_custom = len(perm) > 5 and perm[5]
                type_item = QTableWidgetItem("Personalizzato" if is_custom else "Default")
                if is_custom:
                    type_item.setBackground(QBrush(QColor(255, 255, 200)))
                self.permissions_table.setItem(i, 5, type_item)

        except Exception as e:
            QMessageBox.warning(self, "Errore", f"Errore caricamento permessi: {e}")

    def load_monitor(self):
        """Carica monitor attività real-time"""
        try:
            # First check if the view exists
            check_view = """
                SELECT EXISTS (
                    SELECT FROM pg_views
                    WHERE viewname = 'active_editing_sessions'
                )
            """
            view_exists = self.db_manager.execute_sql(check_view)

            if not view_exists or not view_exists[0][0]:
                # View doesn't exist - show info message
                self.monitor_table.setRowCount(1)
                item = QTableWidgetItem("La vista active_editing_sessions non esiste. "
                                       "Eseguire 'Applica Sistema Concorrenza' dalla configurazione.")
                item.setBackground(QBrush(QColor(255, 255, 200)))
                self.monitor_table.setItem(0, 0, item)
                self.monitor_table.setSpan(0, 0, 1, 7)
                print("Monitor: active_editing_sessions view doesn't exist")
                return

            query = """
                SELECT
                    editing_by,
                    table_name,
                    reference,
                    'Editing' as action,
                    ROUND(minutes_editing::numeric, 1) as minutes,
                    '' as ip,
                    CASE
                        WHEN minutes_editing < 5 THEN '🟢 Attivo'
                        WHEN minutes_editing < 30 THEN '🟡 In corso'
                        ELSE '🔴 Stallo'
                    END as status
                FROM active_editing_sessions
                ORDER BY editing_since DESC
            """

            activities = self.db_manager.execute_sql(query)

            if not activities:
                # No active sessions
                self.monitor_table.setRowCount(1)
                item = QTableWidgetItem("Nessuna sessione di editing attiva al momento")
                item.setBackground(QBrush(QColor(200, 255, 200)))
                self.monitor_table.setItem(0, 0, item)
                self.monitor_table.setSpan(0, 0, 1, 7)
                print("Monitor: No active editing sessions")
                return

            self.monitor_table.clearSpans()
            self.monitor_table.setRowCount(len(activities))

            for i, activity in enumerate(activities):
                for j, value in enumerate(activity):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    if j == 6:  # Status column
                        item.setTextAlignment(Qt.AlignCenter)
                        if '🔴' in str(value):
                            item.setBackground(QBrush(QColor(255, 200, 200)))
                    self.monitor_table.setItem(i, j, item)

            print(f"Monitor: Loaded {len(activities)} active sessions")

        except Exception as e:
            print(f"Errore monitor: {e}")
            self.monitor_table.setRowCount(1)
            item = QTableWidgetItem(f"Errore: {str(e)[:50]}...")
            item.setBackground(QBrush(QColor(255, 200, 200)))
            self.monitor_table.setItem(0, 0, item)
            self.monitor_table.setSpan(0, 0, 1, 7)

    def load_access_log(self):
        """Carica log accessi"""
        try:
            # First check if the table exists
            check_table = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'pyarchinit_access_log'
                )
            """
            table_exists = self.db_manager.execute_sql(check_table)

            if not table_exists or not table_exists[0][0]:
                # Table doesn't exist - show info message
                self.log_table.setRowCount(1)
                item = QTableWidgetItem("La tabella pyarchinit_access_log non esiste. "
                                       "Eseguire 'Inizializza Database Utenti' per crearla.")
                item.setBackground(QBrush(QColor(255, 255, 200)))
                self.log_table.setItem(0, 0, item)
                self.log_table.setSpan(0, 0, 1, 6)
                print("Access log: pyarchinit_access_log table doesn't exist")
                return

            query = """
                SELECT
                    timestamp,
                    username,
                    action,
                    table_accessed,
                    success,
                    error_message
                FROM pyarchinit_access_log
                WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'
                ORDER BY timestamp DESC
                LIMIT 100
            """

            logs = self.db_manager.execute_sql(query)

            if not logs:
                # No logs in last 24 hours
                self.log_table.setRowCount(1)
                item = QTableWidgetItem("Nessun log di accesso nelle ultime 24 ore")
                item.setBackground(QBrush(QColor(200, 255, 200)))
                self.log_table.setItem(0, 0, item)
                self.log_table.setSpan(0, 0, 1, 6)
                print("Access log: No logs in last 24 hours")
                return

            self.log_table.clearSpans()
            self.log_table.setRowCount(len(logs))

            for i, log in enumerate(logs):
                for j, value in enumerate(log):
                    if j == 0 and value:  # Timestamp
                        try:
                            item = QTableWidgetItem(value.strftime("%Y-%m-%d %H:%M:%S"))
                        except:
                            item = QTableWidgetItem(str(value))
                    elif j == 4:  # Success
                        item = QTableWidgetItem("✓" if value else "✗")
                        item.setTextAlignment(Qt.AlignCenter)
                        if not value:
                            item.setBackground(QBrush(QColor(255, 200, 200)))
                    else:
                        item = QTableWidgetItem(str(value) if value else "")
                    self.log_table.setItem(i, j, item)

            print(f"Access log: Loaded {len(logs)} entries")

        except Exception as e:
            print(f"Errore log: {e}")
            self.log_table.setRowCount(1)
            item = QTableWidgetItem(f"Errore: {str(e)[:50]}...")
            item.setBackground(QBrush(QColor(255, 200, 200)))
            self.log_table.setItem(0, 0, item)
            self.log_table.setSpan(0, 0, 1, 6)

    def load_roles(self):
        """Carica ruoli"""
        try:
            query = """
                SELECT role_name, description,
                       default_can_view, default_can_insert,
                       default_can_update, default_can_delete,
                       is_system_role
                FROM pyarchinit_roles
                ORDER BY role_name
            """

            roles = self.db_manager.execute_sql(query)

            # If no roles or empty result, set empty table
            if not roles:
                self.roles_table.setRowCount(0)
                return

            self.roles_table.setRowCount(len(roles))

            for i, role in enumerate(roles):
                self.roles_table.setItem(i, 0, QTableWidgetItem(role[0]))
                self.roles_table.setItem(i, 1, QTableWidgetItem(role[1] or ""))

                for j, value in enumerate(role[2:6], 2):
                    item = QTableWidgetItem("✓" if value else "✗")
                    item.setTextAlignment(Qt.AlignCenter)
                    if value:
                        item.setBackground(QBrush(QColor(200, 255, 200)))
                    self.roles_table.setItem(i, j, item)

                system_item = QTableWidgetItem("Sistema" if role[6] else "Custom")
                if role[6]:
                    system_item.setBackground(QBrush(QColor(200, 200, 200)))
                self.roles_table.setItem(i, 6, system_item)

        except Exception as e:
            print(f"Errore ruoli: {e}")

    def on_user_selected(self):
        """Quando viene selezionato un utente"""
        row = self.users_table.currentRow()
        if row < 0:
            return

        username = self.users_table.item(row, 0).text()

        # Load user details
        try:
            query = """
                SELECT username, full_name, email, role, is_active, notes, last_login
                FROM pyarchinit_users
                WHERE username = :username
            """
            result = self.db_manager.execute_sql(query, {'username': username})

            if result:
                user = result[0]
                self.username_edit.setText(user[0])
                self.fullname_edit.setText(user[1] or "")
                self.email_edit.setText(user[2] or "")
                self.role_combo.setCurrentText(user[3])
                self.active_check.setChecked(user[4])
                self.notes_edit.setText(user[5] or "")

                if user[6]:
                    self.last_login_label.setText(user[6].strftime("%Y-%m-%d %H:%M"))
                else:
                    self.last_login_label.setText("Mai effettuato")

        except Exception as e:
            print(f"Errore selezione utente: {e}")

    def add_new_user(self):
        """Aggiunge nuovo utente"""
        # Reset form
        self.username_edit.clear()
        self.password_edit.clear()
        self.fullname_edit.clear()
        self.email_edit.clear()
        self.role_combo.setCurrentIndex(2)  # archeologo
        self.active_check.setChecked(True)
        self.notes_edit.clear()

        self.username_edit.setFocus()

    def delete_user(self):
        """Elimina utente selezionato"""
        row = self.users_table.currentRow()
        if row < 0:
            return

        username = self.users_table.item(row, 0).text()

        if username == 'admin':
            QMessageBox.warning(self, "Errore", "Non puoi eliminare l'utente admin!")
            return

        reply = QMessageBox.question(self, "Conferma",
                                    f"Eliminare l'utente {username}?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                query = "DELETE FROM pyarchinit_users WHERE username = :username"
                self.db_manager.execute_sql(query, {'username': username})
                self.load_data()
                QMessageBox.information(self, "Successo", "Utente eliminato")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore eliminazione: {e}")

    def save_changes(self):
        """Salva modifiche utente"""
        username = self.username_edit.text()
        if not username:
            QMessageBox.warning(self, "Errore", "Username obbligatorio!")
            return

        try:
            # Check if user exists
            query = "SELECT id FROM pyarchinit_users WHERE username = :username"
            result = self.db_manager.execute_sql(query, {'username': username})

            if result and len(result) > 0:
                # Update existing
                if self.password_edit.text():
                    # Update with password
                    password_hash = hashlib.sha256(
                        self.password_edit.text().encode()
                    ).hexdigest()
                    query = """
                        UPDATE pyarchinit_users
                        SET full_name = :full_name, email = :email, role = :role,
                            is_active = :is_active, notes = :notes, password_hash = :password_hash
                        WHERE username = :username
                    """
                    params = {
                        'full_name': self.fullname_edit.text(),
                        'email': self.email_edit.text(),
                        'role': self.role_combo.currentText(),
                        'is_active': self.active_check.isChecked(),
                        'notes': self.notes_edit.toPlainText() if hasattr(self, 'notes_edit') else '',
                        'password_hash': password_hash,
                        'username': username
                    }
                else:
                    # Update without password
                    query = """
                        UPDATE pyarchinit_users
                        SET full_name = :full_name, email = :email, role = :role,
                            is_active = :is_active, notes = :notes
                        WHERE username = :username
                    """
                    params = {
                        'full_name': self.fullname_edit.text(),
                        'email': self.email_edit.text(),
                        'role': self.role_combo.currentText(),
                        'is_active': self.active_check.isChecked(),
                        'notes': self.notes_edit.toPlainText() if hasattr(self, 'notes_edit') else '',
                        'username': username
                    }

            else:
                # Insert new
                if not self.password_edit.text():
                    QMessageBox.warning(self, "Errore", "Password obbligatoria per nuovo utente!")
                    return

                password_hash = hashlib.sha256(
                    self.password_edit.text().encode()
                ).hexdigest()

                query = """
                    INSERT INTO pyarchinit_users
                    (username, password_hash, full_name, email, role, is_active, notes, created_by)
                    VALUES (:username, :password_hash, :full_name, :email, :role, :is_active, :notes, :created_by)
                """
                params = {
                    'username': username,
                    'password_hash': password_hash,
                    'full_name': self.fullname_edit.text(),
                    'email': self.email_edit.text(),
                    'role': self.role_combo.currentText(),
                    'is_active': self.active_check.isChecked(),
                    'notes': self.notes_edit.toPlainText() if hasattr(self, 'notes_edit') else '',
                    'created_by': getattr(self, 'current_user', 'admin')
                }

            # Execute the query
            result = self.db_manager.execute_sql(query, params)

            # Force commit if using PostgreSQL
            try:
                if hasattr(self.db_manager, 'engine'):
                    self.db_manager.engine.dispose()  # Force close connections
            except:
                pass

            # IMPORTANT: Save password and role BEFORE clearing the form!
            password_for_postgres = self.password_edit.text() or username
            role_for_postgres = self.role_combo.currentText()

            # Reload data to show changes
            self.load_data()

            # Also specifically reload the users list
            self.load_users()

            # Clear the form
            self.username_edit.clear()
            self.password_edit.clear()
            self.fullname_edit.clear()
            self.email_edit.clear()
            if hasattr(self, 'notes_edit'):
                self.notes_edit.clear()

            self.user_changed.emit()

            # Crea automaticamente l'utente PostgreSQL (using saved password, not the cleared field!)
            self.create_postgres_user(username, password_for_postgres, role_for_postgres)

            QMessageBox.information(self, "Successo", "Utente salvato correttamente e creato in PostgreSQL!")

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore salvataggio: {e}")

    def save_permissions(self):
        """Salva i permessi modificati per l'utente selezionato"""
        username = self.perm_user_combo.currentText()
        if not username:
            QMessageBox.warning(self, "Errore", "Seleziona un utente")
            return

        try:
            # Get user ID
            query = "SELECT id FROM pyarchinit_users WHERE username = :username"
            result = self.db_manager.execute_sql(query, {'username': username})
            if not result:
                QMessageBox.warning(self, "Errore", "Utente non trovato")
                return

            user_id = result[0][0]

            # First delete existing permissions
            delete_query = "DELETE FROM pyarchinit_permissions WHERE user_id = :user_id"
            self.db_manager.execute_sql(delete_query, {'user_id': user_id})

            # Then insert new permissions from table
            for row in range(self.permissions_table.rowCount()):
                table_name = self.permissions_table.item(row, 0).text()
                can_view = self.permissions_table.cellWidget(row, 1).isChecked()
                can_insert = self.permissions_table.cellWidget(row, 2).isChecked()
                can_update = self.permissions_table.cellWidget(row, 3).isChecked()
                can_delete = self.permissions_table.cellWidget(row, 4).isChecked()

                insert_query = """
                    INSERT INTO pyarchinit_permissions
                    (user_id, table_name, can_view, can_insert, can_update, can_delete)
                    VALUES (:user_id, :table_name, :can_view, :can_insert, :can_update, :can_delete)
                """
                params = {
                    'user_id': user_id,
                    'table_name': table_name,
                    'can_view': can_view,
                    'can_insert': can_insert,
                    'can_update': can_update,
                    'can_delete': can_delete
                }
                self.db_manager.execute_sql(insert_query, params)

            # Reload permissions to show they are now custom
            self.load_user_permissions()

            # Sincronizza i permessi con PostgreSQL
            self.sync_postgres_permissions_for_user(username)

            QMessageBox.information(self, "Successo", "Permessi salvati correttamente e sincronizzati con PostgreSQL!")

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore salvataggio permessi: {e}")

    def create_postgres_user(self, username, password, role):
        """Crea un utente PostgreSQL con i permessi base del ruolo"""
        try:
            # Use the provided password or fallback to username
            actual_password = password if password else username

            # Check if user already exists
            check_query = "SELECT 1 FROM pg_user WHERE usename = :username"
            user_exists = False
            try:
                result = self.db_manager.execute_sql(check_query, {'username': username})
                user_exists = bool(result)
            except:
                pass

            if user_exists:
                # User exists - UPDATE the password
                print(f"Utente PostgreSQL {username} già esistente, aggiorno la password...")
                try:
                    alter_query = f"ALTER USER {username} WITH PASSWORD '{actual_password}'"
                    self.db_manager.execute_sql(alter_query)
                    print(f"Password aggiornata per utente PostgreSQL {username}")
                except Exception as e:
                    print(f"Errore aggiornamento password PostgreSQL: {e}")
            else:
                # Create new user
                create_query = f"CREATE USER {username} WITH PASSWORD '{actual_password}'"
                self.db_manager.execute_sql(create_query)
                print(f"Utente PostgreSQL {username} creato")

            # Grant basic permissions
            db_name = self.db_manager.engine.url.database
            grant_connect = f"GRANT CONNECT ON DATABASE {db_name} TO {username}"
            self.db_manager.execute_sql(grant_connect)

            grant_usage = f"GRANT USAGE ON SCHEMA public TO {username}"
            self.db_manager.execute_sql(grant_usage)

            # Apply role-based permissions
            if role == 'admin' or role == 'administrator':
                # Grant all permissions
                self.db_manager.execute_sql(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {username}")
                self.db_manager.execute_sql(f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {username}")
                self.db_manager.execute_sql(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {username}")
                self.db_manager.execute_sql(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {username}")

            elif role == 'archeologo':
                # Can view, insert, and update most tables
                self.db_manager.execute_sql(f"GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO {username}")
                self.db_manager.execute_sql(f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {username}")
                self.db_manager.execute_sql(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO {username}")
                self.db_manager.execute_sql(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO {username}")

            elif role == 'studente':
                # Limited permissions - mainly view and some insert
                self.db_manager.execute_sql(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {username}")
                self.db_manager.execute_sql(f"GRANT INSERT ON us_table, campioni_table TO {username}")
                self.db_manager.execute_sql(f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {username}")
                self.db_manager.execute_sql(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO {username}")

            elif role == 'guest':
                # Read-only access
                self.db_manager.execute_sql(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {username}")
                self.db_manager.execute_sql(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO {username}")

            # Grant execute on functions
            self.db_manager.execute_sql(f"GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO {username}")

            # Grant permissions on PyArchInit system tables (needed for UI functionality)
            system_tables = [
                'pyarchinit_thesaurus_sigle',
                'pyarchinit_roles',
                'pyarchinit_users',
                'pyarchinit_permissions',
                'pyarchinit_config',
                'pyarchinit_codici_tipologia',
                'pyarchinit_access_log',
                'pyarchinit_activity_log',
                'pyarchinit_audit_log'
            ]

            for table in system_tables:
                try:
                    self.db_manager.execute_sql(f"GRANT SELECT ON {table} TO {username}")
                except:
                    pass  # Table might not exist

            # Grant SELECT on all views and pyarchinit_* tables
            try:
                self.db_manager.execute_sql(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {username}")
            except:
                pass

            print(f"Utente PostgreSQL {username} creato con ruolo {role}")

        except Exception as e:
            print(f"Errore creazione utente PostgreSQL: {e}")
            # Don't raise - just log error

    def sync_postgres_permissions_for_user(self, username):
        """Sincronizza i permessi PyArchInit con PostgreSQL per un utente specifico"""
        try:
            # Get user info
            query = "SELECT id, password_hash, role FROM pyarchinit_users WHERE username = :username"
            result = self.db_manager.execute_sql(query, {'username': username})
            if not result:
                return

            user_id, password_hash, role = result[0]

            # Check if PostgreSQL user exists
            check_query = "SELECT 1 FROM pg_user WHERE usename = :username"
            try:
                pg_result = self.db_manager.execute_sql(check_query, {'username': username})
                user_exists = bool(pg_result)
            except:
                user_exists = False

            if not user_exists:
                # Create PostgreSQL user with temporary password
                create_user_query = f"CREATE USER {username} WITH PASSWORD '{username}123'"
                self.db_manager.execute_sql(create_user_query)

                # Grant basic permissions
                grant_connect = f"GRANT CONNECT ON DATABASE {self.db_manager.engine.url.database} TO {username}"
                self.db_manager.execute_sql(grant_connect)

                grant_usage = f"GRANT USAGE ON SCHEMA public TO {username}"
                self.db_manager.execute_sql(grant_usage)

            # Get permissions for this user
            perm_query = """
                SELECT table_name, can_view, can_insert, can_update, can_delete
                FROM pyarchinit_permissions
                WHERE user_id = :user_id
            """
            permissions = self.db_manager.execute_sql(perm_query, {'user_id': user_id})

            # Apply each permission
            for table_name, can_view, can_insert, can_update, can_delete in permissions:
                # Build permission list
                perms = []
                if can_view:
                    perms.append('SELECT')
                if can_insert:
                    perms.append('INSERT')
                if can_update:
                    perms.append('UPDATE')
                if can_delete:
                    perms.append('DELETE')

                if perms:
                    # Revoke all first
                    try:
                        revoke_query = f"REVOKE ALL PRIVILEGES ON {table_name} FROM {username}"
                        self.db_manager.execute_sql(revoke_query)
                    except:
                        pass

                    # Grant new permissions
                    perm_str = ', '.join(perms)
                    grant_query = f"GRANT {perm_str} ON {table_name} TO {username}"
                    self.db_manager.execute_sql(grant_query)

                    # If INSERT permission, also grant sequence permissions
                    if can_insert:
                        # Try to grant sequence permissions
                        try:
                            # Find table's primary key sequence
                            seq_query = f"""
                                SELECT c.relname
                                FROM pg_class c
                                JOIN pg_depend d ON d.objid = c.oid
                                JOIN pg_class t ON t.oid = d.refobjid
                                WHERE c.relkind = 'S' AND t.relname = '{table_name}'
                            """
                            sequences = self.db_manager.execute_sql(seq_query)
                            for seq in sequences:
                                grant_seq = f"GRANT USAGE, SELECT ON SEQUENCE {seq[0]} TO {username}"
                                self.db_manager.execute_sql(grant_seq)
                        except:
                            pass

            print(f"Permessi PostgreSQL sincronizzati per utente {username}")

        except Exception as e:
            print(f"Errore sincronizzazione permessi PostgreSQL: {e}")
            # Don't raise - just log error

    def apply_permissions_to_all(self):
        """Applica permessi a tutte le tabelle"""
        username = self.perm_user_combo.currentText()
        if not username:
            return

        view = self.quick_view.isChecked()
        insert = self.quick_insert.isChecked()
        update = self.quick_update.isChecked()
        delete = self.quick_delete.isChecked()

        reply = QMessageBox.question(self, "Conferma",
            f"Applicare questi permessi a TUTTE le tabelle per {username}?",
            QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                # Get all tables
                for row in range(self.permissions_table.rowCount()):
                    table_name = self.permissions_table.item(row, 0).text()

                    query = """
                        SELECT set_user_permission(%s, %s, %s, %s, %s, %s, %s)
                    """
                    self.db_manager.execute_sql(query, [
                        username, table_name, insert, update, delete, view, self.current_user
                    ])

                self.load_user_permissions()
                QMessageBox.information(self, "Successo", "Permessi applicati!")

            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore applicazione permessi: {e}")

    def force_unlock_record(self):
        """Forza sblocco record"""
        row = self.monitor_table.currentRow()
        if row < 0:
            return

        table = self.monitor_table.item(row, 1).text()
        record = self.monitor_table.item(row, 2).text()
        user = self.monitor_table.item(row, 0).text()

        reply = QMessageBox.question(self, "Conferma",
            f"Sbloccare forzatamente il record {record} in {table} (bloccato da {user})?",
            QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                query = f"""
                    UPDATE {table}
                    SET editing_by = NULL, editing_since = NULL
                    WHERE reference = :record
                """
                self.db_manager.execute_sql(query, {'record': record})
                self.load_monitor()
                QMessageBox.information(self, "Successo", "Record sbloccato!")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore sblocco: {e}")

    def toggle_auto_refresh(self, state):
        """Attiva/disattiva auto-refresh"""
        if state == Qt.Checked:
            self.refresh_timer = QTimer()
            self.refresh_timer.timeout.connect(self.load_monitor)
            self.refresh_timer.start(10000)  # 10 secondi
        else:
            if hasattr(self, 'refresh_timer'):
                self.refresh_timer.stop()

    def initialize_user_tables(self):
        """Inizializza le tabelle del sistema utenti nel database"""
        reply = QMessageBox.question(self, "Conferma",
                                    "Vuoi creare le tabelle del sistema utenti?\n"
                                    "Questa operazione creerà:\n"
                                    "- pyarchinit_users (utenti)\n"
                                    "- pyarchinit_permissions (permessi)\n"
                                    "- pyarchinit_roles (ruoli)\n"
                                    "- pyarchinit_access_log (log accessi)",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                # Leggi lo script SQL
                import os
                plugin_dir = os.path.dirname(os.path.dirname(__file__))
                sql_file = os.path.join(plugin_dir, 'sql', 'create_user_management_system.sql')

                if not os.path.exists(sql_file):
                    # Se il file non esiste, usa lo script inline
                    sql_script = self.get_user_tables_sql()
                else:
                    with open(sql_file, 'r') as f:
                        sql_script = f.read()

                # Esegui lo script
                queries = sql_script.split(';')
                for query in queries:
                    if query.strip():
                        self.db_manager.execute_sql(query)

                QMessageBox.information(self, "Successo",
                                      "Tabelle create con successo!\n"
                                      "Ora puoi iniziare a gestire gli utenti.")

                # Ricarica i dati
                self.load_data()

            except Exception as e:
                QMessageBox.critical(self, "Errore",
                                   f"Errore durante la creazione delle tabelle:\n{str(e)}")

    def get_user_tables_sql(self):
        """Ritorna lo script SQL per creare le tabelle utenti"""
        return """
-- Tabella utenti
CREATE TABLE IF NOT EXISTS pyarchinit_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'archeologo',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    last_login TIMESTAMP,
    last_ip VARCHAR(50),
    notes TEXT
);

-- Tabella permessi
CREATE TABLE IF NOT EXISTS pyarchinit_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES pyarchinit_users(id) ON DELETE CASCADE,
    table_name VARCHAR(100) NOT NULL,
    can_insert BOOLEAN DEFAULT FALSE,
    can_update BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    can_view BOOLEAN DEFAULT TRUE,
    site_filter VARCHAR(100),
    area_filter VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    UNIQUE(user_id, table_name)
);

-- Tabella ruoli
CREATE TABLE IF NOT EXISTS pyarchinit_roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    default_can_insert BOOLEAN DEFAULT FALSE,
    default_can_update BOOLEAN DEFAULT FALSE,
    default_can_delete BOOLEAN DEFAULT FALSE,
    default_can_view BOOLEAN DEFAULT TRUE,
    is_system_role BOOLEAN DEFAULT FALSE
);

-- Tabella log accessi
CREATE TABLE IF NOT EXISTS pyarchinit_access_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES pyarchinit_users(id),
    username VARCHAR(50),
    action VARCHAR(50),
    table_accessed VARCHAR(100),
    operation VARCHAR(20),
    record_id INTEGER,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN,
    error_message TEXT
);

-- Inserisci ruoli predefiniti
INSERT INTO pyarchinit_roles (role_name, description, default_can_insert, default_can_update, default_can_delete, default_can_view, is_system_role) VALUES
('admin', 'Amministratore - Accesso completo', TRUE, TRUE, TRUE, TRUE, TRUE),
('responsabile', 'Responsabile scavo - Può modificare tutto', TRUE, TRUE, TRUE, TRUE, FALSE),
('archeologo', 'Archeologo - Può inserire e modificare', TRUE, TRUE, FALSE, TRUE, FALSE),
('studente', 'Studente - Solo inserimento', TRUE, FALSE, FALSE, TRUE, FALSE),
('guest', 'Ospite - Solo visualizzazione', FALSE, FALSE, FALSE, TRUE, FALSE)
ON CONFLICT (role_name) DO NOTHING;

-- Crea utente admin predefinito (password: admin123)
INSERT INTO pyarchinit_users (username, password_hash, full_name, role, is_active)
VALUES ('admin', SHA256('admin123'), 'Amministratore Sistema', 'admin', TRUE)
ON CONFLICT (username) DO NOTHING;
"""