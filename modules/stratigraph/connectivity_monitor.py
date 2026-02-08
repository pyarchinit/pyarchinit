# -*- coding: utf-8 -*-
"""
Connectivity monitor for StratiGraph sync.

Periodically checks a configurable health-check endpoint and emits
Qt signals when connectivity changes. Uses debouncing to avoid
flapping on unstable networks.
"""
from qgis.PyQt.QtCore import QObject, QTimer, QUrl, QEventLoop, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.core import QgsNetworkAccessManager, QgsSettings, QgsMessageLog, Qgis

SETTINGS_PREFIX = "pyArchInit/stratigraph/"
DEFAULT_HEALTH_URL = "http://localhost:8080/health"
DEFAULT_INTERVAL_MS = 30000
DEFAULT_DEBOUNCE = 2
REQUEST_TIMEOUT_MS = 5000
TAG = "StratiGraph"


class ConnectivityMonitor(QObject):
    """Monitors network connectivity to the StratiGraph server.

    Emits signals when connectivity status changes.  Uses a debounce
    counter so that N consecutive identical results are required
    before the reported state actually flips.
    """

    connection_available = pyqtSignal()
    connection_lost = pyqtSignal()
    connectivity_changed = pyqtSignal(bool)

    def __init__(self, parent=None, check_interval_ms: int = None,
                 debounce_count: int = None):
        super().__init__(parent)
        settings = QgsSettings()

        self._check_interval = (
            check_interval_ms
            if check_interval_ms is not None
            else settings.value(
                SETTINGS_PREFIX + "check_interval_ms",
                DEFAULT_INTERVAL_MS, type=int))
        self._debounce_count = (
            debounce_count
            if debounce_count is not None
            else settings.value(
                SETTINGS_PREFIX + "debounce_count",
                DEFAULT_DEBOUNCE, type=int))
        self._health_url = settings.value(
            SETTINGS_PREFIX + "health_check_url",
            DEFAULT_HEALTH_URL, type=str)

        self._is_online = False
        self._consecutive_same = 0
        self._last_probe_result = None

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._do_check)

    # -- public API ----------------------------------------------------------

    @property
    def is_online(self) -> bool:
        return self._is_online

    def start(self):
        """Start periodic connectivity checks."""
        self._timer.start(self._check_interval)
        # Run an immediate check
        QTimer.singleShot(0, self._do_check)

    def stop(self):
        """Stop periodic checks."""
        self._timer.stop()

    def check_now(self):
        """Force an immediate connectivity check."""
        self._do_check()

    def set_check_interval(self, ms: int):
        """Update the check interval (milliseconds)."""
        self._check_interval = ms
        if self._timer.isActive():
            self._timer.setInterval(ms)

    # -- internal ------------------------------------------------------------

    def _do_check(self):
        """Perform a single health-check probe."""
        reachable = self._probe()
        self._update_state(reachable)

    def _probe(self) -> bool:
        """HTTP GET to health endpoint. Returns True on 2xx."""
        try:
            nam = QgsNetworkAccessManager.instance()
            req = QNetworkRequest(QUrl(self._health_url))

            reply = nam.get(req)

            # Wait with timeout
            loop = QEventLoop()
            reply.finished.connect(loop.quit)

            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(loop.quit)
            timer.start(REQUEST_TIMEOUT_MS)

            loop.exec(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

            timer.stop()

            if reply.isRunning():
                reply.abort()
                reply.deleteLater()
                return False

            status = reply.attribute(
                QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            err = reply.error()
            reply.deleteLater()

            if err != QNetworkReply.NetworkError.NoError:
                return False
            return status is not None and 200 <= status < 300

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Connectivity probe error: {e}",
                TAG, Qgis.MessageLevel.Warning)
            return False

    def _update_state(self, probe_result: bool):
        """Apply debounce logic and emit signals if state changes."""
        if probe_result == self._last_probe_result:
            self._consecutive_same += 1
        else:
            self._consecutive_same = 1
            self._last_probe_result = probe_result

        if self._consecutive_same < self._debounce_count:
            return

        if probe_result == self._is_online:
            return  # no change

        self._is_online = probe_result
        self.connectivity_changed.emit(self._is_online)

        if self._is_online:
            QgsMessageLog.logMessage(
                "Connectivity restored", TAG, Qgis.MessageLevel.Info)
            self.connection_available.emit()
        else:
            QgsMessageLog.logMessage(
                "Connectivity lost", TAG, Qgis.MessageLevel.Warning)
            self.connection_lost.emit()
