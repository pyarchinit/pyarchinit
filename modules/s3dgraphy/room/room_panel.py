"""La stanza dentro pyArchInit: un dock col web del nodo (B2).

Il pannello CARICA una pagina servita dal nodo via HTTP — nessun codice di
EMStudio o del server entra nel plugin (GPL-2 qui, GPL-3 là: aggregazione).
La sola-lettura è del SERVER (ruolo viewer): qui non si finge nulla.
Qt WebEngine può mancare in un profilo QGIS: allora si risponde False e il
chiamante apre il browser — mai un'eccezione per una finestra.
"""
from __future__ import annotations

PANEL_OBJECT_NAME = "pyarchinitRoomPanel"


def _webengine():
    try:
        try:
            from tabs.DemPlotDialogs import _import_qt_webengine
        except ImportError:
            # plugin importato come pacchetto: room/ → s3dgraphy → modules
            # → root = quattro livelli
            from ....tabs.DemPlotDialogs import _import_qt_webengine  # noqa
        return _import_qt_webengine()
    except Exception:
        return None


def _existing(iface):
    try:
        main = iface.mainWindow()
        from qgis.PyQt.QtWidgets import QDockWidget
        return main.findChild(QDockWidget, PANEL_OBJECT_NAME)
    except Exception:
        return None


def open_in_panel(iface, url, title):
    """Apri (o riusa) il pannello sul `url`. False = niente WebEngine."""
    view_class = _webengine()
    if view_class is None:
        return False
    try:
        from qgis.PyQt.QtCore import Qt, QUrl
        from qgis.PyQt.QtWidgets import QDockWidget

        dock = _existing(iface)
        if dock is None:
            dock = QDockWidget(title, iface.mainWindow())
            dock.setObjectName(PANEL_OBJECT_NAME)
            view = view_class(dock)
            dock.setWidget(view)
            iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        else:
            dock.setWindowTitle(title)
            view = dock.widget()
        view.load(QUrl(url))
        dock.show()
        dock.raise_()
        return True
    except Exception:
        # una finestra che non si apre non è un motivo per un traceback
        return False


def close_panel(iface):
    """Per unload(): il dock non deve sopravvivere al plugin (lezione
    della 5.13.29 — le voci duplicate al reload)."""
    dock = _existing(iface)
    if dock is not None:
        try:
            iface.removeDockWidget(dock)
            dock.deleteLater()
        except Exception:
            pass
