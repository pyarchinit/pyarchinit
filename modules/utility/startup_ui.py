"""Startup windows that must never end up behind other windows.

At the first start of pyArchInit 5, above all on Windows, the plugin asks
whether to copy the data of the previous installation and installs the
missing Python packages while QGIS, or its Plugin Manager, is in front and
the loading splash (frameless, always on top) covers the middle of the
screen. A parentless dialog then opens behind them: the user does not see
it and startup waits for a click that never comes. The package
installation runs pip once per package, minutes in all, with nothing in
front saying so.

These helpers keep questions in front and stop Windows from opening a
console window for every command. qgis.PyQt only: Qt5 and Qt6.
"""
import os
import subprocess

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QApplication, QMessageBox


def italian() -> bool:
    """True when QGIS runs in Italian (startup texts are IT/EN only)."""
    try:
        from qgis.core import QgsSettings
        return QgsSettings().value("locale/userLocale", "it", type=str)[:2] == "it"
    except Exception:
        return True


def bring_to_front(widget) -> None:
    """Show ``widget`` above every window (QGIS, Plugin Manager, splash) and
    give it the focus. Call it before ``exec()``."""
    # modality first: QMessageBox.setWindowModality() re-parents the box with
    # plain Qt.Dialog flags, which would drop the stay-on-top hint
    widget.setWindowModality(Qt.WindowModality.ApplicationModal)
    widget.setWindowFlags(widget.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
    widget.show()
    widget.raise_()
    widget.activateWindow()
    QApplication.processEvents()


def exec_on_top(box, splash=None):
    """``exec()`` a QMessageBox in front of everything. The splash, always
    on top too, steps aside while the box is open. Returns the standard
    button clicked (NoButton when the box was closed without a click)."""
    hidden = splash is not None and splash.isVisible()
    if hidden:
        splash.hide()
    try:
        bring_to_front(box)
        box.exec()
        clicked = box.clickedButton()
        return box.standardButton(clicked) if clicked is not None else QMessageBox.StandardButton.NoButton
    finally:
        if hidden:
            splash.show()
            splash.raise_()
            QApplication.processEvents()


def ask_yes_no(title, text, splash=None, default_yes=True) -> bool:
    """Yes/No question kept in front of everything (see ``exec_on_top``)."""
    yes, no = QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No
    box = QMessageBox(QMessageBox.Icon.Question, title, text, yes | no)
    box.setDefaultButton(yes if default_yes else no)
    return exec_on_top(box, splash) == yes


def no_console_window() -> dict:
    """subprocess keyword arguments that stop Windows from opening a console
    window for every pip / pg_dump / dot run started from QGIS: it pops up
    over the splash and steals the focus. Empty on the other systems."""
    if os.name == "nt":
        return {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)}
    return {}
