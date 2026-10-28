"""Un QWebView di ripiego quando QGIS non ha QtWebKit.

Alcune build di QGIS per macOS (la 3.44.9, issue #667) non hanno
``PyQt5.QtWebKitWidgets``: i file .ui del plugin che contengono un QWebView
(configurazione, Sito, US, Thesaurus, pannello principale) non si caricavano
e il plugin intero non partiva. Il ripiego è un QTextBrowser con ``load`` e
``setHtml``: mostra le pagine locali e, per un indirizzo web, il link.

Vale solo mentre si importa pyArchInit (``only_for_pyarchinit``): i suoi .ui
si compilano lì e tengono il riferimento al modulo; tolto subito dopo, gli
altri plugin che controllano QtWebKit con un import vedono ancora che manca e
usano il loro ripiego.
"""
import contextlib
import sys
import types

_MODULE = None


def fallback_module():
    global _MODULE
    if _MODULE is not None:
        return _MODULE
    from qgis.PyQt.QtCore import QUrl
    from qgis.PyQt.QtWidgets import QTextBrowser

    class QWebView(QTextBrowser):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setOpenExternalLinks(True)

        def setHtml(self, html, baseUrl=None):
            if baseUrl is not None:
                self.document().setBaseUrl(baseUrl)
            super().setHtml(html)

        def showEvent(self, event):
            # la proprietà «url» dei .ui (uic la scrive con setProperty)
            url = self.property("url")
            if isinstance(url, QUrl) and url.isValid() and not self.toPlainText().strip():
                self.load(url)
            super().showEvent(event)

        def load(self, url):
            if url.isLocalFile():
                try:
                    with open(url.toLocalFile(), encoding="utf-8", errors="replace") as f:
                        html = f.read()
                except OSError:
                    html = ""
                self.setHtml(html, url)             # immagini relative alla pagina
            else:
                testo = url.toString()
                self.setHtml('<p><a href="%s">%s</a></p>' % (testo, testo))

        def setUrl(self, url):
            self.load(url)

    _MODULE = types.ModuleType("PyQt5.QtWebKitWidgets")
    _MODULE.QWebView = QWebView
    _MODULE.__pyarchinit_fallback__ = True
    return _MODULE


def _has_webkit():
    try:
        from PyQt5 import QtWebKitWidgets  # noqa: F401
        return True
    except ImportError:
        return False


@contextlib.contextmanager
def only_for_pyarchinit(probe=_has_webkit):
    """Il ripiego al posto di ``PyQt5.QtWebKitWidgets`` se manca, solo per
    la durata del blocco; con QtWebKit vero non tocca niente."""
    messo = False
    try:
        if not probe():
            import PyQt5
            mod = fallback_module()
            sys.modules["PyQt5.QtWebKitWidgets"] = mod
            PyQt5.QtWebKitWidgets = mod
            messo = True
    except Exception as e:                                  # noqa: BLE001
        print("pyArchInit: QtWebKit fallback not installed: %s" % e)
    try:
        yield
    finally:
        if messo:
            import PyQt5
            if getattr(sys.modules.get("PyQt5.QtWebKitWidgets"), "__pyarchinit_fallback__", False):
                del sys.modules["PyQt5.QtWebKitWidgets"]
            if getattr(getattr(PyQt5, "QtWebKitWidgets", None), "__pyarchinit_fallback__", False):
                del PyQt5.QtWebKitWidgets
