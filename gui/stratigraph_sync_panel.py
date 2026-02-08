# -*- coding: utf-8 -*-
"""
StratiGraph Sync Panel — dock widget showing sync state, connectivity,
queue stats and recent activity.
"""
from datetime import datetime, timezone

from qgis.PyQt.QtCore import Qt, QTimer
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QGroupBox, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDialogButtonBox)


# ── small icon helpers (unicode fallback when no icon theme) ────────────

_ICON_ONLINE = "\u2705"   # green check
_ICON_OFFLINE = "\u274C"  # red cross
_STATE_ICONS = {
    "OFFLINE_EDITING": "\U0001F4DD",    # memo
    "LOCAL_EXPORT": "\U0001F4E6",       # package
    "LOCAL_VALIDATION": "\U0001F50D",   # magnifying glass
    "QUEUED_FOR_SYNC": "\u23F3",        # hourglass
    "SYNC_SUCCESS": "\u2705",           # check
    "SYNC_FAILED": "\u26A0\uFE0F",     # warning
}


class QueueDialog(QDialog):
    """Modal dialog listing all queue entries."""

    def __init__(self, queue, parent=None):
        super().__init__(parent)
        self.setWindowTitle("StratiGraph — Sync Queue")
        self.resize(700, 400)
        self._queue = queue
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Status", "Attempts", "Created", "Last Error", "Bundle"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)
        layout.addWidget(self.table)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_refresh = QPushButton("Refresh")
        btn_box.addButton(btn_refresh,
                          QDialogButtonBox.ButtonRole.ActionRole)
        btn_refresh.clicked.connect(self._refresh)
        btn_box.rejected.connect(self.close)
        layout.addWidget(btn_box)

    def _refresh(self):
        entries = self._queue.get_all()
        self.table.setRowCount(len(entries))
        for row, e in enumerate(entries):
            self.table.setItem(row, 0, QTableWidgetItem(str(e.id)))
            self.table.setItem(row, 1, QTableWidgetItem(e.status))
            self.table.setItem(row, 2, QTableWidgetItem(str(e.attempts)))
            self.table.setItem(row, 3, QTableWidgetItem(e.created_at or ""))
            self.table.setItem(row, 4, QTableWidgetItem(e.last_error or ""))
            self.table.setItem(row, 5,
                               QTableWidgetItem(e.bundle_path or ""))


class StratiGraphSyncPanel(QDockWidget):
    """Dock widget providing a quick overview and controls for
    the StratiGraph sync system."""

    def __init__(self, orchestrator, parent=None):
        super().__init__("StratiGraph Sync", parent)
        self.setObjectName("StratiGraphSyncPanel")
        self._orch = orchestrator

        self._last_sync_msg = ""

        self._build_ui()
        self._connect_signals()

        # Periodic stats refresh
        self._stats_timer = QTimer(self)
        self._stats_timer.timeout.connect(self._refresh_stats)
        self._stats_timer.start(5000)

        # Initial state
        self._refresh_all()

    # -- UI construction -----------------------------------------------------

    def _build_ui(self):
        container = QWidget()
        root = QVBoxLayout(container)
        root.setContentsMargins(6, 6, 6, 6)

        # ── Status section ──────────────────────────────────
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)

        self._lbl_state = QLabel("State: —")
        self._lbl_conn = QLabel("Connection: —")
        self._lbl_queue = QLabel("Queue: —")
        self._lbl_last_sync = QLabel("Last sync: —")

        for lbl in (self._lbl_state, self._lbl_conn,
                    self._lbl_queue, self._lbl_last_sync):
            status_layout.addWidget(lbl)
        root.addWidget(status_group)

        # ── Action buttons ──────────────────────────────────
        btn_layout = QHBoxLayout()
        self._btn_export = QPushButton("Export Bundle")
        self._btn_sync = QPushButton("Sync Now")
        self._btn_queue = QPushButton("Queue...")

        btn_layout.addWidget(self._btn_export)
        btn_layout.addWidget(self._btn_sync)
        btn_layout.addWidget(self._btn_queue)
        root.addLayout(btn_layout)

        # ── Activity log ────────────────────────────────────
        log_group = QGroupBox("Recent Activity")
        log_layout = QVBoxLayout(log_group)
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(150)
        log_layout.addWidget(self._log)
        root.addWidget(log_group)

        root.addStretch()
        self.setWidget(container)

    def _connect_signals(self):
        # Buttons
        self._btn_export.clicked.connect(self._on_export)
        self._btn_sync.clicked.connect(self._on_sync)
        self._btn_queue.clicked.connect(self._on_show_queue)

        # Orchestrator signals
        sm = self._orch.state_machine
        sm.state_changed.connect(self._on_state_changed)

        cm = self._orch.connectivity
        cm.connectivity_changed.connect(self._on_connectivity_changed)

        self._orch.sync_completed.connect(self._on_sync_completed)
        self._orch.bundle_exported.connect(self._on_bundle_exported)

    # -- slots ---------------------------------------------------------------

    def _on_export(self):
        self._btn_export.setEnabled(False)
        self._log_activity("Exporting bundle...")
        result = self._orch.export_bundle()
        self._btn_export.setEnabled(True)
        if result.get("success"):
            self._log_activity(
                f"Bundle exported: {result.get('bundle_path', '?')}")
        else:
            errors = ", ".join(result.get("errors", ["unknown error"]))
            self._log_activity(f"Export failed: {errors}")

    def _on_sync(self):
        self._log_activity("Sync requested...")
        self._orch.sync_now()

    def _on_show_queue(self):
        dlg = QueueDialog(self._orch.queue, self)
        dlg.exec()

    def _on_state_changed(self, old_state: str, new_state: str):
        icon = _STATE_ICONS.get(new_state, "")
        self._lbl_state.setText(f"State: {icon} {new_state}")
        self._log_activity(f"State: {old_state} \u2192 {new_state}")

    def _on_connectivity_changed(self, is_online: bool):
        if is_online:
            self._lbl_conn.setText(f"Connection: {_ICON_ONLINE} Online")
        else:
            self._lbl_conn.setText(f"Connection: {_ICON_OFFLINE} Offline")
        self._log_activity(
            f"Connectivity: {'Online' if is_online else 'Offline'}")

    def _on_sync_completed(self, entry_id: int, success: bool, message: str):
        ts = datetime.now(timezone.utc).strftime("%H:%M")
        status = "OK" if success else "FAILED"
        self._last_sync_msg = f"{ts} {status}"
        self._lbl_last_sync.setText(f"Last sync: {self._last_sync_msg}")
        self._log_activity(
            f"Sync #{entry_id}: {status} — {message}")

    def _on_bundle_exported(self, bundle_path: str):
        self._refresh_stats()

    # -- helpers -------------------------------------------------------------

    def _refresh_stats(self):
        stats = self._orch.queue.get_stats()
        pending = stats.get("pending", 0)
        uploading = stats.get("uploading", 0)
        failed = stats.get("failed", 0)
        total_waiting = pending + uploading
        parts = [f"{total_waiting} pending"]
        if failed:
            parts.append(f"{failed} failed")
        self._lbl_queue.setText(f"Queue: {', '.join(parts)}")

    def _refresh_all(self):
        state = self._orch.state_machine.current_state.value
        icon = _STATE_ICONS.get(state, "")
        self._lbl_state.setText(f"State: {icon} {state}")

        online = self._orch.connectivity.is_online
        conn_icon = _ICON_ONLINE if online else _ICON_OFFLINE
        conn_text = "Online" if online else "Offline"
        self._lbl_conn.setText(f"Connection: {conn_icon} {conn_text}")

        self._refresh_stats()

        if self._last_sync_msg:
            self._lbl_last_sync.setText(
                f"Last sync: {self._last_sync_msg}")
        else:
            self._lbl_last_sync.setText("Last sync: —")

    def _log_activity(self, message: str):
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        self._log.append(f"[{ts}] {message}")
