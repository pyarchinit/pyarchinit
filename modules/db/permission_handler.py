#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Centralized permission and error handler for PyArchInit
Provides user-friendly error messages without exposing SQL details
"""

from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsMessageLog, Qgis


class PermissionHandler:
    """
    Handles permission errors and provides user-friendly messages
    """

    def __init__(self, parent_form, language='it'):
        self.form = parent_form
        self.L = language
        self.db_manager = None

    def set_db_manager(self, db_manager):
        """Set the database manager"""
        self.db_manager = db_manager

    def has_permission(self, table_name, permission_type):
        """
        Check if user has specific permission on table
        Returns True if permission exists, False otherwise
        """
        if not self.db_manager:
            return True  # Assume permission if no db_manager

        # For SQLite, always return True
        if hasattr(self.db_manager, 'engine') and 'sqlite' in str(self.db_manager.engine.url):
            return True

        try:
            # Check permission using PostgreSQL has_table_privilege function
            check_sql = f"""
            SELECT has_table_privilege(current_user, '{table_name}', '{permission_type}')
            """
            result = self.db_manager.execute_sql(check_sql)
            if result and len(result) > 0:
                # Handle both tuple and dict results
                if isinstance(result[0], tuple):
                    return result[0][0] if len(result[0]) > 0 else False
                elif isinstance(result[0], dict):
                    return list(result[0].values())[0] if result[0] else False
                else:
                    return bool(result[0])
        except:
            # If check fails, assume permission exists
            return True

        return False

    def handle_permission_error(self, error, operation='operation', show_message=True):
        """
        Handle permission errors with user-friendly messages
        Returns True if error was handled, False otherwise
        """
        error_str = str(error)
        error_type = str(type(error))

        # Check if it's a permission error
        if not ('InsufficientPrivilege' in error_type or
                'permission denied' in error_str.lower() or
                'insufficient privilege' in error_str.lower()):
            return False

        # Log technical details for debugging
        QgsMessageLog.logMessage(
            f"Permission error in {self.form.__class__.__name__}: {error_str}",
            "PyArchInit", Qgis.Info
        )

        if show_message:
            # Show user-friendly message
            if self.L == 'it':
                msg = self._get_italian_message(operation)
                title = "Permessi Insufficienti"
            elif self.L == 'de':
                msg = self._get_german_message(operation)
                title = "Unzureichende Berechtigungen"
            else:
                msg = self._get_english_message(operation)
                title = "Insufficient Permissions"

            QMessageBox.warning(self.form, title, msg, QMessageBox.Ok)

        return True

    def handle_database_error(self, error, context='', show_message=True):
        """
        Handle database errors with user-friendly messages
        Returns True if error was handled, False otherwise
        """
        # First check if it's a permission error
        if self.handle_permission_error(error, context, show_message):
            return True

        error_str = str(error)

        # Log technical details
        QgsMessageLog.logMessage(
            f"Database error in {self.form.__class__.__name__}: {error_str}",
            "PyArchInit", Qgis.Warning
        )

        if not show_message:
            return False

        # Determine error type and show appropriate message
        if 'encode' in error_str.lower() or 'decode' in error_str.lower():
            # Encoding error
            if self.L == 'it':
                msg = "Alcuni caratteri nel record non sono supportati. Controllare i dati inseriti."
                title = "Errore Caratteri"
            elif self.L == 'de':
                msg = "Einige Zeichen im Datensatz werden nicht unterstützt. Bitte überprüfen Sie die Eingabe."
                title = "Zeichenfehler"
            else:
                msg = "Some characters in the record are not supported. Please check your input."
                title = "Character Error"

        elif 'connection' in error_str.lower() or 'connect' in error_str.lower():
            # Connection error
            if self.L == 'it':
                msg = "Impossibile connettersi al database. Verificare la connessione."
                title = "Errore Connessione"
            elif self.L == 'de':
                msg = "Verbindung zur Datenbank fehlgeschlagen. Bitte Verbindung überprüfen."
                title = "Verbindungsfehler"
            else:
                msg = "Cannot connect to database. Please check your connection."
                title = "Connection Error"

        elif 'duplicate' in error_str.lower() or 'unique' in error_str.lower():
            # Duplicate key error
            if self.L == 'it':
                msg = "Record duplicato. Esiste già un record con questi valori."
                title = "Record Duplicato"
            elif self.L == 'de':
                msg = "Doppelter Datensatz. Ein Datensatz mit diesen Werten existiert bereits."
                title = "Doppelter Datensatz"
            else:
                msg = "Duplicate record. A record with these values already exists."
                title = "Duplicate Record"

        elif 'foreign key' in error_str.lower():
            # Foreign key error
            if self.L == 'it':
                msg = "Impossibile completare l'operazione: alcuni dati dipendono da altri record."
                title = "Errore Dipendenze"
            elif self.L == 'de':
                msg = "Vorgang kann nicht abgeschlossen werden: Daten hängen von anderen Datensätzen ab."
                title = "Abhängigkeitsfehler"
            else:
                msg = "Cannot complete operation: data depends on other records."
                title = "Dependency Error"

        else:
            # Generic database error
            if self.L == 'it':
                msg = f"Errore durante {self._get_context_it(context)}. Se il problema persiste, contattare l'amministratore."
                title = "Errore Database"
            elif self.L == 'de':
                msg = f"Fehler bei {self._get_context_de(context)}. Bei anhaltenden Problemen wenden Sie sich an den Administrator."
                title = "Datenbankfehler"
            else:
                msg = f"Error during {context if context else 'operation'}. If problem persists, contact administrator."
                title = "Database Error"

        QMessageBox.warning(self.form, title, msg, QMessageBox.Ok)
        return True

    def _get_italian_message(self, operation):
        """Get Italian permission error message"""
        operations = {
            'INSERT': "Non hai i permessi per inserire nuovi record in questa tabella.",
            'UPDATE': "Non hai i permessi per modificare record in questa tabella.",
            'DELETE': "Non hai i permessi per eliminare record da questa tabella.",
            'SELECT': "Non hai i permessi per visualizzare record di questa tabella."
        }
        return operations.get(operation.upper(),
                             "Non hai i permessi necessari per questa operazione.")

    def _get_english_message(self, operation):
        """Get English permission error message"""
        operations = {
            'INSERT': "You don't have permission to insert new records in this table.",
            'UPDATE': "You don't have permission to modify records in this table.",
            'DELETE': "You don't have permission to delete records from this table.",
            'SELECT': "You don't have permission to view records from this table."
        }
        return operations.get(operation.upper(),
                             "You don't have the necessary permissions for this operation.")

    def _get_german_message(self, operation):
        """Get German permission error message"""
        operations = {
            'INSERT': "Sie haben keine Berechtigung, neue Datensätze in diese Tabelle einzufügen.",
            'UPDATE': "Sie haben keine Berechtigung, Datensätze in dieser Tabelle zu ändern.",
            'DELETE': "Sie haben keine Berechtigung, Datensätze aus dieser Tabelle zu löschen.",
            'SELECT': "Sie haben keine Berechtigung, Datensätze aus dieser Tabelle anzuzeigen."
        }
        return operations.get(operation.upper(),
                             "Sie haben nicht die erforderlichen Berechtigungen für diesen Vorgang.")

    def _get_context_it(self, context):
        """Get Italian context translation"""
        contexts = {
            'save': 'il salvataggio',
            'delete': 'l\'eliminazione',
            'update': 'l\'aggiornamento',
            'insert': 'l\'inserimento',
            'search': 'la ricerca'
        }
        return contexts.get(context.lower(), 'l\'operazione')

    def _get_context_de(self, context):
        """Get German context translation"""
        contexts = {
            'save': 'Speichern',
            'delete': 'Löschen',
            'update': 'Aktualisierung',
            'insert': 'Einfügen',
            'search': 'Suche'
        }
        return contexts.get(context.lower(), 'Vorgang')
