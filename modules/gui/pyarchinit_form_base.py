#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base class for PyArchInit forms with common functionality
Provides centralized error handling and timer management
"""

from qgis.PyQt.QtWidgets import QMessageBox, QDialog
from qgis.PyQt.QtCore import QTimer
from qgis.core import QgsMessageLog, Qgis


class PyArchInitFormMixin:
    """
    Mixin class for PyArchInit forms providing common functionality
    This should be inherited by all PyArchInit forms to ensure consistent behavior
    """

    def setup_refresh_timer(self):
        """
        Setup refresh timer for checking concurrent modifications
        This method should be called during form initialization
        """
        if not hasattr(self, 'refresh_timer'):
            self.refresh_timer = QTimer()
            self.refresh_timer.timeout.connect(self.check_for_updates)
            # Only start timer if we're in browse mode with a valid connection
            if hasattr(self, 'BROWSE_STATUS') and self.BROWSE_STATUS == "b" and hasattr(self, 'DB_MANAGER') and self.DB_MANAGER:
                self.refresh_timer.start(60000)  # Check every 60 seconds

            # Track if form is active
            self._form_active = True

    def stop_refresh_timer(self):
        """
        Stop the refresh timer
        Should be called when form is closed or hidden
        """
        if hasattr(self, 'refresh_timer') and self.refresh_timer:
            self.refresh_timer.stop()

        # Mark form as inactive
        self._form_active = False

    def closeEvent(self, event):
        """
        Handle form close event
        Ensures timer is stopped when form closes
        """
        # Stop refresh timer
        self.stop_refresh_timer()

        # Clear editing state
        if hasattr(self, 'editing_record_id'):
            self.editing_record_id = None

        # Call parent closeEvent if it exists
        if hasattr(super(), 'closeEvent'):
            super().closeEvent(event)
        else:
            event.accept()

    def hideEvent(self, event):
        """
        Handle form hide event
        Stops timer when form is hidden/minimized
        """
        self.stop_refresh_timer()

        # Call parent hideEvent if it exists
        if hasattr(super(), 'hideEvent'):
            super().hideEvent(event)

    def showEvent(self, event):
        """
        Handle form show event
        Restarts timer when form is shown again
        """
        # Restart timer if we're in browse mode
        if hasattr(self, 'BROWSE_STATUS') and self.BROWSE_STATUS == "b" and hasattr(self, 'DB_MANAGER') and self.DB_MANAGER:
            if hasattr(self, 'refresh_timer') and self.refresh_timer:
                self.refresh_timer.start(60000)

        self._form_active = True

        # Call parent showEvent if it exists
        if hasattr(super(), 'showEvent'):
            super().showEvent(event)

    def check_for_updates_safe(self):
        """
        Wrapper around check_for_updates that checks if form is active
        Prevents notifications from appearing when form is closed
        """
        # Only check for updates if form is active and visible
        if not hasattr(self, '_form_active') or not self._form_active:
            return

        # Check if dialog is visible (additional safety check)
        if hasattr(self, 'isVisible') and not self.isVisible():
            return

        # Call original check_for_updates if it exists
        if hasattr(self, 'check_for_updates'):
            self.check_for_updates()

    def handle_permission_error(self, error, operation='operation'):
        """
        Centralized permission error handler
        Returns True if error was handled, False otherwise
        """
        error_str = str(error)
        error_type = str(type(error))

        # Check if it's a permission error
        if 'InsufficientPrivilege' in error_type or 'permission denied' in error_str.lower():
            # Determine language
            L = 'it'
            if hasattr(self, 'L'):
                L = self.L

            # Show user-friendly permission error
            if L == 'it':
                msg = f"Non hai i permessi per {self.get_operation_name_it(operation)}."
                title = "Errore Permessi"
            else:
                msg = f"You don't have permission to {operation} this record."
                title = "Permission Error"

            QMessageBox.warning(self, title, msg, QMessageBox.Ok)

            # Log technical details for debugging
            QgsMessageLog.logMessage(f"Permission error in {self.__class__.__name__}: {error_str}",
                                    "PyArchInit", Qgis.Info)
            return True

        return False

    def get_operation_name_it(self, operation):
        """Get Italian translation for operations"""
        translations = {
            'INSERT': 'inserire',
            'UPDATE': 'modificare',
            'DELETE': 'eliminare',
            'SELECT': 'visualizzare'
        }
        return translations.get(operation.upper(), 'eseguire questa operazione')

    def handle_database_error(self, error, context=''):
        """
        Centralized database error handler
        Shows user-friendly messages without SQL details
        """
        error_str = str(error)

        # Check if permission handler already handled it
        if self.handle_permission_error(error, context):
            return

        # Check for encoding errors
        if 'encode' in error_str.lower() or 'decode' in error_str.lower():
            L = getattr(self, 'L', 'it')
            if L == 'it':
                msg = "Errore di codifica: alcuni caratteri nel record non sono supportati."
                title = "Errore Codifica"
            else:
                msg = "Encoding error: some characters in the record are not supported."
                title = "Encoding Error"
        # Check for connection errors
        elif 'connection' in error_str.lower() or 'connect' in error_str.lower():
            L = getattr(self, 'L', 'it')
            if L == 'it':
                msg = "Errore di connessione al database. Verificare la connessione."
                title = "Errore Connessione"
            else:
                msg = "Database connection error. Please check your connection."
                title = "Connection Error"
        # Generic database error
        else:
            L = getattr(self, 'L', 'it')
            if L == 'it':
                msg = f"Errore database durante {context}. Contattare l'amministratore se il problema persiste."
                title = "Errore Database"
            else:
                msg = f"Database error during {context}. Contact administrator if the problem persists."
                title = "Database Error"

        QMessageBox.warning(self, title, msg, QMessageBox.Ok)

        # Log full error for debugging
        QgsMessageLog.logMessage(f"Database error in {self.__class__.__name__}: {error_str}",
                                "PyArchInit", Qgis.Warning)


class FormStateManager:
    """
    Manages form state to prevent false modification notifications
    """

    def __init__(self, form):
        self.form = form
        self.initial_state = {}
        self.is_loading = False

    def capture_state(self):
        """Capture current form state"""
        if self.is_loading:
            return

        state = {}
        # Capture all widget values (simplified example)
        for widget_name in dir(self.form):
            widget = getattr(self.form, widget_name, None)
            if widget and hasattr(widget, 'text'):
                try:
                    state[widget_name] = widget.text()
                except:
                    pass
            elif widget and hasattr(widget, 'currentText'):
                try:
                    state[widget_name] = widget.currentText()
                except:
                    pass

        self.initial_state = state

    def has_changes(self):
        """Check if form has changes"""
        if self.is_loading:
            return False

        current_state = {}
        for widget_name in self.initial_state:
            widget = getattr(self.form, widget_name, None)
            if widget and hasattr(widget, 'text'):
                try:
                    current_state[widget_name] = widget.text()
                except:
                    pass
            elif widget and hasattr(widget, 'currentText'):
                try:
                    current_state[widget_name] = widget.currentText()
                except:
                    pass

        return current_state != self.initial_state

    def set_loading(self, loading):
        """Set loading state"""
        self.is_loading = loading