"""La stanza dentro pyArchInit: un dock col web del nodo (B2).

Il pannello CARICA una pagina servita dal nodo via HTTP — nessun codice di
EMStudio o del server entra nel plugin (GPL-2 qui, GPL-3 là: aggregazione).
La sola-lettura è del SERVER (ruolo viewer): qui non si finge nulla.
Il motore si sceglie a scaletta: Qt WebEngine se c'è, altrimenti il
QWebView di Qt WebKit, che QGIS 3 spedisce ancora (misurato il 2026-10-08
su questo Mac: Qt 5.15.2, WebEngine assente, WebKit presente, e la pagina
della stanza si carica, titolo e corpo compresi). Se non c'è nemmeno
quello si risponde False e il chiamante apre il browser — mai
un'eccezione per una finestra. Il pannello parla solo l'API che i due
motori hanno in comune: ``load(QUrl)`` e ``title()``.
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


def _webkit():
    """``QWebView`` di Qt WebKit, o None.

    Motore vecchio (WebKit 602), ma la pagina per-stanza del nodo la
    rende: è il ripiego che tiene il pannello dentro QGIS invece di
    buttare l'utente nel browser.
    """
    for modulo in ("PyQt5.QtWebKitWidgets", "qgis.PyQt.QtWebKitWidgets"):
        try:
            return __import__(modulo, fromlist=["QWebView"]).QWebView
        except Exception:                           # noqa: BLE001
            continue
    return None


def web_view_class():
    """La classe della vista e il nome del motore, dal migliore in giù."""
    engine = _webengine()
    if engine is not None:
        return engine, "webengine"
    webkit = _webkit()
    if webkit is not None:
        return webkit, "webkit"
    return None, ""


def _existing(iface):
    try:
        main = iface.mainWindow()
        from qgis.PyQt.QtWidgets import QDockWidget
        return main.findChild(QDockWidget, PANEL_OBJECT_NAME)
    except Exception:
        return None


def open_in_panel(iface, url, title):
    """Apri (o riusa) il pannello sul `url`. False = nessun motore web."""
    view_class, engine_name = web_view_class()
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
            view.setToolTip("Motore web: %s" % engine_name)
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
