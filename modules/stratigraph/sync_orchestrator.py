# -*- coding: utf-8 -*-
"""
Sync Orchestrator for StratiGraph offline-first architecture.

Coordinates the state machine, sync queue and connectivity monitor
to drive the export -> validate -> enqueue -> upload lifecycle.
"""
import os
from datetime import datetime, timezone

from qgis.PyQt.QtCore import QObject, QTimer, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.core import (QgsNetworkAccessManager, QgsSettings,
                        QgsMessageLog, Qgis)
from qgis.PyQt.QtCore import QUrl, QEventLoop, QByteArray

from .sync_state_machine import SyncStateMachine, SyncState
from .sync_queue import SyncQueue
from .connectivity_monitor import ConnectivityMonitor
from .bundle_creator import BundleCreator
from .bundle_validator import validate_bundle

TAG = "StratiGraph"
SETTINGS_PREFIX = "pyArchInit/stratigraph/"

# Exponential backoff delays (seconds)
BACKOFF_SCHEDULE = [30, 60, 120, 300, 900]


class SyncOrchestrator(QObject):
    """Ties together state machine, queue and connectivity.

    Automatically processes the queue when connectivity is available
    and retries failed uploads with exponential backoff.
    """

    sync_started = pyqtSignal(int)              # entry_id
    sync_progress = pyqtSignal(int, int, str)   # entry_id, percent, message
    sync_completed = pyqtSignal(int, bool, str)  # entry_id, success, message
    bundle_exported = pyqtSignal(str)            # bundle_path

    def __init__(self, parent=None):
        super().__init__(parent)

        self.state_machine = SyncStateMachine(self)
        self.queue = SyncQueue()
        self.connectivity = ConnectivityMonitor(self)

        self._running = False
        self._processing = False  # guard against concurrent queue runs

        settings = QgsSettings()
        self._upload_endpoint = settings.value(
            SETTINGS_PREFIX + "upload_endpoint",
            "http://localhost:8080/api/v1/bundles",
            type=str)

        # Auto-process queue when connectivity returns
        self.connectivity.connection_available.connect(self._process_queue)

    # -- lifecycle -----------------------------------------------------------

    def start(self):
        """Start the orchestrator and connectivity monitor."""
        self._running = True
        self.connectivity.start()
        # Cleanup old completed entries on startup
        self.queue.cleanup_completed(older_than_days=7)
        QgsMessageLog.logMessage(
            "SyncOrchestrator started", TAG, Qgis.MessageLevel.Info)

    def stop(self):
        """Stop the orchestrator and connectivity monitor."""
        self._running = False
        self.connectivity.stop()
        QgsMessageLog.logMessage(
            "SyncOrchestrator stopped", TAG, Qgis.MessageLevel.Info)

    # -- public API ----------------------------------------------------------

    def export_bundle(self, site_name: str = None) -> dict:
        """Run the full export -> validate -> enqueue pipeline.

        Returns a result dict with keys: success, bundle_path, errors.
        """
        result = {"success": False, "bundle_path": None, "errors": []}

        # OFFLINE_EDITING -> LOCAL_EXPORT
        if not self.state_machine.transition(SyncState.LOCAL_EXPORT,
                                             {"site": site_name}):
            result["errors"].append("Cannot start export from current state: "
                                    f"{self.state_machine.current_state.value}")
            return result

        home = os.environ.get("PYARCHINIT_HOME", "")
        output_dir = os.path.join(home, "stratigraph_bundles")

        try:
            creator = BundleCreator(
                output_dir=output_dir,
                site_name=site_name,
            )
            # Add the default pyarchinit DB folder as data source
            db_folder = os.path.join(home, "pyarchinit_DB_folder")
            if os.path.isdir(db_folder):
                creator.add_directory(db_folder, "data",
                                      extensions=[".sqlite", ".gpkg"])

            build_result = creator.build()
        except Exception as e:
            self.state_machine.transition(SyncState.LOCAL_VALIDATION)
            self.state_machine.transition(SyncState.OFFLINE_EDITING,
                                          {"error": str(e)})
            result["errors"].append(f"Bundle creation failed: {e}")
            return result

        if not build_result.get("success"):
            self.state_machine.transition(SyncState.LOCAL_VALIDATION)
            self.state_machine.transition(SyncState.OFFLINE_EDITING,
                                          {"errors": build_result.get("errors")})
            result["errors"] = build_result.get("errors", [])
            return result

        bundle_path = build_result["bundle_path"]

        # LOCAL_EXPORT -> LOCAL_VALIDATION
        if not self.state_machine.transition(SyncState.LOCAL_VALIDATION):
            result["errors"].append("Transition to LOCAL_VALIDATION failed")
            return result

        # Validate
        validation = validate_bundle(bundle_path)
        if not validation.get("valid"):
            # Validation failed -> back to OFFLINE_EDITING
            self.state_machine.transition(SyncState.OFFLINE_EDITING,
                                          {"validation_errors": validation.get("errors")})
            result["errors"] = [e.get("message", str(e))
                                for e in validation.get("errors", [])]
            return result

        # LOCAL_VALIDATION -> QUEUED_FOR_SYNC
        if not self.state_machine.transition(SyncState.QUEUED_FOR_SYNC):
            result["errors"].append("Transition to QUEUED_FOR_SYNC failed")
            return result

        entry_id = self.queue.enqueue(
            bundle_path,
            build_result.get("manifest_hash", ""),
            metadata={"site": site_name,
                       "timestamp": build_result.get("timestamp")})

        result["success"] = True
        result["bundle_path"] = bundle_path
        result["entry_id"] = entry_id

        self.bundle_exported.emit(bundle_path)

        # Kick off upload if online
        if self.connectivity.is_online:
            QTimer.singleShot(0, self._process_queue)

        return result

    def sync_now(self):
        """Force an immediate sync attempt if online."""
        if self.connectivity.is_online:
            self._process_queue()
        else:
            QgsMessageLog.logMessage(
                "sync_now called but offline", TAG, Qgis.MessageLevel.Warning)

    def get_status(self) -> dict:
        """Return a snapshot of the orchestrator's status."""
        return {
            "state": self.state_machine.current_state.value,
            "online": self.connectivity.is_online,
            "queue_stats": self.queue.get_stats(),
            "running": self._running,
        }

    # -- internal queue processing -------------------------------------------

    def _process_queue(self):
        """Process pending entries one at a time."""
        if self._processing or not self._running:
            return
        self._processing = True

        try:
            while True:
                entry = self.queue.dequeue()
                if entry is None:
                    break

                self.sync_started.emit(entry.id)
                self.sync_progress.emit(entry.id, 0, "Uploading bundle...")

                success = self._upload_bundle(entry.bundle_path,
                                              self._upload_endpoint)
                if success:
                    self.queue.mark_completed(entry.id)
                    self.sync_progress.emit(entry.id, 100, "Upload complete")
                    self.sync_completed.emit(entry.id, True, "Sync successful")
                    # Transition state machine if it was in QUEUED_FOR_SYNC
                    if (self.state_machine.current_state ==
                            SyncState.QUEUED_FOR_SYNC):
                        self.state_machine.transition(SyncState.SYNC_SUCCESS)
                        self.state_machine.transition(SyncState.OFFLINE_EDITING)
                else:
                    error_msg = "Upload failed"
                    self.queue.mark_failed(entry.id, error_msg)
                    self.sync_completed.emit(entry.id, False, error_msg)
                    if (self.state_machine.current_state ==
                            SyncState.QUEUED_FOR_SYNC):
                        self.state_machine.transition(SyncState.SYNC_FAILED)

                    # Schedule retry with backoff
                    delay_idx = min(entry.attempts,
                                    len(BACKOFF_SCHEDULE) - 1)
                    delay_s = BACKOFF_SCHEDULE[delay_idx]
                    QTimer.singleShot(delay_s * 1000, self._process_queue)
                    break  # stop processing, wait for retry
        finally:
            self._processing = False

    def _upload_bundle(self, bundle_path: str, endpoint: str) -> bool:
        """Upload a bundle ZIP via HTTP POST.

        This is a temporary wrapper until WP4 API specs are finalised.
        """
        if not os.path.isfile(bundle_path):
            QgsMessageLog.logMessage(
                f"Bundle file not found: {bundle_path}",
                TAG, Qgis.MessageLevel.Warning)
            return False

        try:
            with open(bundle_path, "rb") as f:
                data = f.read()

            nam = QgsNetworkAccessManager.instance()
            req = QNetworkRequest(QUrl(endpoint))
            req.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader,
                          "application/zip")

            reply = nam.post(req, QByteArray(data))

            loop = QEventLoop()
            reply.finished.connect(loop.quit)

            timeout = QTimer()
            timeout.setSingleShot(True)
            timeout.timeout.connect(loop.quit)
            timeout.start(60000)  # 60 second upload timeout

            loop.exec(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
            timeout.stop()

            if reply.isRunning():
                reply.abort()
                reply.deleteLater()
                return False

            status = reply.attribute(
                QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            err = reply.error()
            reply.deleteLater()

            if err != QNetworkReply.NetworkError.NoError:
                QgsMessageLog.logMessage(
                    f"Upload error: {err}", TAG, Qgis.MessageLevel.Warning)
                return False
            return status is not None and 200 <= status < 300

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Upload exception: {e}", TAG, Qgis.MessageLevel.Warning)
            return False
