"""Startup windows kept in front, install progress on the splash (2026-09-11).

First start of pyArchInit 5, above all on Windows: the question "copy the
data of the previous installation?" opened behind the always-on-top splash
and QGIS / the Plugin Manager, and startup waited for a click nobody could
see; the package installation ran for minutes with no progress in front.

Needs Qt (run with the QGIS python); skipped where qgis.PyQt is missing.
"""
from __future__ import annotations

import importlib
import importlib.util
import os
import re
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("qgis.PyQt.QtWidgets")

from qgis.PyQt.QtCore import Qt  # noqa: E402
from qgis.PyQt.QtWidgets import QApplication, QDialog, QMessageBox  # noqa: E402

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility import startup_ui  # noqa: E402

YES, NO = QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _on_top(widget):
    return bool(widget.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)


def _fake_exec(seen, answer, splash=None):
    def fake(box):
        seen.update(on_top=_on_top(box), visible=box.isVisible(),
                    modal=box.windowModality() == Qt.WindowModality.ApplicationModal,
                    splash_visible=None if splash is None else splash.isVisible())
        box.button(answer).click()
        return 0
    return fake


def test_the_question_is_in_front_and_the_splash_steps_aside(app, monkeypatch):
    splash = QDialog()
    splash.show()
    seen = {}
    monkeypatch.setattr(QMessageBox, "exec", _fake_exec(seen, YES, splash))

    assert startup_ui.ask_yes_no("pyArchInit", "Copiare i dati?", splash) is True

    assert seen == {"on_top": True, "visible": True, "modal": True, "splash_visible": False}
    assert splash.isVisible()                      # back after the answer
    splash.close()


def test_answering_no(app, monkeypatch):
    monkeypatch.setattr(QMessageBox, "exec", _fake_exec({}, NO))
    assert startup_ui.ask_yes_no("pyArchInit", "Copiare i dati?") is False


def test_bring_to_front(app):
    dialog = QDialog()
    startup_ui.bring_to_front(dialog)
    assert _on_top(dialog) and dialog.isVisible()
    assert dialog.windowModality() == Qt.WindowModality.ApplicationModal
    dialog.close()


def test_no_console_window_only_on_windows(monkeypatch):
    assert startup_ui.no_console_window() == ({} if os.name != "nt" else startup_ui.no_console_window())
    monkeypatch.setattr(startup_ui.os, "name", "nt")
    assert startup_ui.no_console_window() == {"creationflags": 0x08000000}


def test_startup_never_opens_a_parentless_message_box():
    src = (_ROOT / "__init__.py").read_text(encoding="utf-8")
    assert not re.search(r"QMessageBox\.(question|warning|information|critical)\(\s*None", src)


def _splash_module():
    spec = importlib.util.spec_from_file_location("_pyarchinit_splash", _ROOT / "gui" / "pyarchinit_splash.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_splash_shows_the_install_progress(app):
    splash = _splash_module().PyArchInitSplash(message="Installazione pacchetti 1/2")
    assert splash.splash_widget.progress is None     # the loading splash has no bar
    splash.set_progress(40, "40% · 1:05")
    assert splash.splash_widget.progress == 40
    assert splash.splash_widget.progress_caption == "40% · 1:05"
    splash.show()
    app.processEvents()
    assert not splash.grab().isNull()                # paints the bar without errors
    splash.set_progress(None)
    assert splash.splash_widget.progress is None
    splash.close()


def _plugin(monkeypatch, tmp_path):
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))
    if str(_ROOT.parent) not in sys.path:
        sys.path.insert(0, str(_ROOT.parent))
    return importlib.import_module(_ROOT.name)


def test_the_worker_reports_progress_around_each_package(app, monkeypatch, tmp_path):
    plugin = _plugin(monkeypatch, tmp_path)
    installed = []
    monkeypatch.setattr(plugin.PackageManager, "install", staticmethod(installed.append))
    worker = plugin.Worker()
    progress, status = [], []
    worker.progress.connect(progress.append)
    worker.package_status.connect(status.append)

    worker.install_packages(["reportlab", "graphviz"])

    assert installed == ["reportlab", "graphviz"]
    assert progress == [0, 50, 50, 100]              # not 100% while the last one installs
    assert "1/2" in status[0] and "reportlab" in status[0]
    assert "2/2" in status[1] and "graphviz" in status[1]


def test_the_install_dialog_opens_in_front(app, monkeypatch, tmp_path):
    plugin = _plugin(monkeypatch, tmp_path)
    seen = {}
    monkeypatch.setattr(plugin.InstallDialog, "exec",
                        lambda dialog: seen.update(on_top=_on_top(dialog), visible=dialog.isVisible()) or 0)
    plugin.show_install_dialog(["reportlab"])
    assert seen == {"on_top": True, "visible": True}
