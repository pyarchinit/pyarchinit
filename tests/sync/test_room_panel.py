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


def test_the_panel_falls_back_to_webkit_when_webengine_is_missing():
    """Su un profilo senza Qt WebEngine il pannello usa QtWebKit, che
    QGIS 3 spedisce ancora (misurato su questo Mac: Qt 5.15.2, WebEngine
    assente, WebKit presente, e la pagina della stanza si carica). Il
    browser resta l'ultimo ripiego, non il primo."""
    import inspect

    from modules.s3dgraphy.room import room_panel

    assert hasattr(room_panel, "web_view_class")
    src = inspect.getsource(room_panel)
    assert "QtWebKitWidgets" in src
    assert src.index("def _webengine") < src.index("def _webkit")


def test_the_engine_name_travels_with_the_class(monkeypatch):
    from modules.s3dgraphy.room import room_panel

    class _Finta:
        pass

    monkeypatch.setattr(room_panel, "_webengine", lambda: None)
    monkeypatch.setattr(room_panel, "_webkit", lambda: _Finta)
    assert room_panel.web_view_class() == (_Finta, "webkit")

    monkeypatch.setattr(room_panel, "_webengine", lambda: _Finta)
    assert room_panel.web_view_class() == (_Finta, "webengine")

    monkeypatch.setattr(room_panel, "_webengine", lambda: None)
    monkeypatch.setattr(room_panel, "_webkit", lambda: None)
    assert room_panel.web_view_class() == (None, "")


def test_the_panel_only_speaks_the_api_both_engines_have():
    """QWebEngineView e QWebView condividono load()/title(); tutto il
    resto (page().profile(), setUrl su un profilo persistente…) è di uno
    solo dei due e il pannello non lo deve chiamare."""
    import inspect

    from modules.s3dgraphy.room import room_panel

    src = inspect.getsource(room_panel.open_in_panel)
    for solo_webengine in (".profile(", "setZoomFactor", "QWebEngineProfile"):
        assert solo_webengine not in src, solo_webengine
