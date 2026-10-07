"""Il pannello della stanza: guardie sul sorgente, mai istanze WebEngine
(i due smoke ignorati della suite sono crash Qt noti — Global Constraints).
"""
from __future__ import annotations

from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SRC = (PLUGIN_ROOT / "modules" / "s3dgraphy" / "room"
       / "room_panel.py")


def test_the_panel_module_exists_and_exposes_the_contract():
    src = SRC.read_text(encoding="utf-8")
    for name in ("def open_in_panel", "def close_panel",
                 "PANEL_OBJECT_NAME"):
        assert name in src, name


def test_webengine_comes_from_the_house_pattern_and_may_be_absent():
    """Qt WebEngine può mancare: si usa _import_qt_webengine (Qt5/Qt6,
    None se assente) e open_in_panel risponde False, mai un raise."""
    src = SRC.read_text(encoding="utf-8")
    assert "_import_qt_webengine" in src
    assert "return False" in src


def test_one_panel_per_session():
    """Review Focus 4: riaprire RIUSA il dock (objectName fisso), mai due."""
    src = SRC.read_text(encoding="utf-8")
    assert "findChild" in src or "findChildren" in src
    assert "raise_" in src


def test_the_menu_opens_the_room_in_the_panel_with_a_browser_fallback():
    src = (PLUGIN_ROOT / "pyarchinitPlugin.py").read_text(encoding="utf-8")
    body = src.split("def _open_rooms_door", 1)[1].split("\n    def ", 1)[0]
    assert "room_work_url" in body, "con una stanza configurata si apre LA stanza"
    assert "open_in_panel" in body
    assert "webbrowser" in body, "niente WebEngine → browser"
    assert "messageBar" in body


def test_unload_closes_the_panel():
    import re
    src = (PLUGIN_ROOT / "pyarchinitPlugin.py").read_text(encoding="utf-8")
    unload = re.search(r"def unload\(self\):(.*?)\n    def ", src, re.S)
    assert unload and "close_panel" in unload.group(1)
