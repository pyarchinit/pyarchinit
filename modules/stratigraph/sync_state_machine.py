# -*- coding: utf-8 -*-
"""
Sync State Machine for StratiGraph offline-first architecture.

Manages the 6-state lifecycle of bundle synchronization:
OFFLINE_EDITING -> LOCAL_EXPORT -> LOCAL_VALIDATION ->
QUEUED_FOR_SYNC -> SYNC_SUCCESS/SYNC_FAILED -> OFFLINE_EDITING
"""
import json
from datetime import datetime, timezone
from enum import Enum

from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.core import QgsSettings, QgsMessageLog, Qgis


class SyncState(Enum):
    """Possible states in the sync lifecycle."""
    OFFLINE_EDITING = "OFFLINE_EDITING"
    LOCAL_EXPORT = "LOCAL_EXPORT"
    LOCAL_VALIDATION = "LOCAL_VALIDATION"
    QUEUED_FOR_SYNC = "QUEUED_FOR_SYNC"
    SYNC_SUCCESS = "SYNC_SUCCESS"
    SYNC_FAILED = "SYNC_FAILED"


# Valid state transitions
VALID_TRANSITIONS = {
    SyncState.OFFLINE_EDITING: [SyncState.LOCAL_EXPORT],
    SyncState.LOCAL_EXPORT: [SyncState.LOCAL_VALIDATION],
    SyncState.LOCAL_VALIDATION: [SyncState.QUEUED_FOR_SYNC, SyncState.OFFLINE_EDITING],
    SyncState.QUEUED_FOR_SYNC: [SyncState.SYNC_SUCCESS, SyncState.SYNC_FAILED],
    SyncState.SYNC_FAILED: [SyncState.QUEUED_FOR_SYNC],
    SyncState.SYNC_SUCCESS: [SyncState.OFFLINE_EDITING],
}

MAX_HISTORY = 50
SETTINGS_PREFIX = "pyArchInit/stratigraph/"
TAG = "StratiGraph"


class SyncStateMachine(QObject):
    """State machine governing the sync lifecycle.

    Persists current state and transition history via QgsSettings.
    Emits Qt signals on every transition for UI reactivity.
    """

    state_changed = pyqtSignal(str, str)        # old_state, new_state
    transition_failed = pyqtSignal(str, str, str)  # current, attempted, reason

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = QgsSettings()
        self._state = self._load_state()

    # -- public API ----------------------------------------------------------

    @property
    def current_state(self) -> SyncState:
        return self._state

    def transition(self, new_state: SyncState, context: dict = None) -> bool:
        """Attempt a state transition.

        Args:
            new_state: Target state.
            context: Optional metadata stored in transition history.

        Returns:
            True if the transition succeeded, False otherwise.
        """
        old = self._state
        allowed = VALID_TRANSITIONS.get(old, [])

        if new_state not in allowed:
            reason = (f"Transition {old.value} -> {new_state.value} not allowed. "
                      f"Valid targets: {[s.value for s in allowed]}")
            QgsMessageLog.logMessage(reason, TAG, Qgis.MessageLevel.Warning)
            self.transition_failed.emit(old.value, new_state.value, reason)
            return False

        self._state = new_state
        self._save_state()
        self._append_history(old, new_state, context)

        QgsMessageLog.logMessage(
            f"State transition: {old.value} -> {new_state.value}",
            TAG, Qgis.MessageLevel.Info)
        self.state_changed.emit(old.value, new_state.value)
        return True

    def get_transition_history(self, limit: int = 10) -> list:
        """Return the most recent *limit* transition entries (newest first)."""
        history = self._load_history()
        return history[-limit:][::-1]

    def reset(self):
        """Reset to OFFLINE_EDITING and clear history."""
        old = self._state
        self._state = SyncState.OFFLINE_EDITING
        self._save_state()
        self._settings.remove(SETTINGS_PREFIX + "sync_history")
        if old != self._state:
            self.state_changed.emit(old.value, self._state.value)

    # -- persistence helpers -------------------------------------------------

    def _load_state(self) -> SyncState:
        raw = self._settings.value(
            SETTINGS_PREFIX + "sync_state",
            SyncState.OFFLINE_EDITING.value,
            type=str)
        try:
            return SyncState(raw)
        except (ValueError, KeyError):
            return SyncState.OFFLINE_EDITING

    def _save_state(self):
        self._settings.setValue(
            SETTINGS_PREFIX + "sync_state",
            self._state.value)

    def _load_history(self) -> list:
        raw = self._settings.value(
            SETTINGS_PREFIX + "sync_history", "[]", type=str)
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []

    def _append_history(self, old: SyncState, new: SyncState,
                        context: dict = None):
        history = self._load_history()
        entry = {
            "from": old.value,
            "to": new.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if context:
            entry["context"] = context
        history.append(entry)
        # Trim to MAX_HISTORY
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]
        self._settings.setValue(
            SETTINGS_PREFIX + "sync_history",
            json.dumps(history))
