"""Collaudo contro il nodo locale VERO. Si salta se il nodo non risponde —
stesso patto dei test *_pg: l'ambiente è una precondizione, non un fallimento.

Avvio del nodo:
    cd ~/stratigraph-node/stratigraph-server && \
    EM_SERVER_ALLOW_ANON=1 ~/stratigraph-node/venv/bin/uvicorn \
        app.main:app --port 8020
"""
from __future__ import annotations

import json
import shutil
import sys
import urllib.request
import uuid
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

NODE = "http://127.0.0.1:8020"


def _node_answers():
    try:
        with urllib.request.urlopen(NODE + "/v1/health", timeout=3) as r:
            return json.loads(r.read().decode()).get("ok") is True
    except Exception:
        return False


if not _node_answers():
    pytest.skip("nessun nodo StratiGraph su %s" % NODE,
                allow_module_level=True)


@pytest.fixture
def mini_volterra(tmp_path):
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(PLUGIN_ROOT / "tests" / "sync" / "fixtures"
                 / "mini_volterra.sqlite", dst)
    return "sqlite:///%s" % dst


@pytest.fixture
def room(monkeypatch):
    room_id = "collaudo-%s" % uuid.uuid4().hex[:8]
    body = json.dumps({"room_id": room_id,
                       "title": "Collaudo pyArchInit"}).encode()
    req = urllib.request.Request(
        NODE + "/v1/rooms", data=body, method="POST",
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        assert r.status == 201
    monkeypatch.setenv("STRATIGRAPH_SERVER_URL", NODE)
    monkeypatch.setenv("STRATIGRAPH_ROOM_ID", room_id)
    monkeypatch.delenv("STRATIGRAPH_TOKEN", raising=False)
    return room_id


def test_a_site_lands_and_a_repeat_is_a_merge(mini_volterra, room):
    import sqlite3
    from modules.s3dgraphy.room import room_client
    sito = sqlite3.connect(mini_volterra.replace("sqlite:///", "")).execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]

    first = room_client.deliver_site(mini_volterra, sito)
    assert first.sent > 0 and first.applied > 0
    assert not first.other_refusals, first.other_refusals

    again = room_client.deliver_site(mini_volterra, sito)
    assert again.a_repeat, again.summary()


def test_the_rooms_door_answers(room):
    from modules.s3dgraphy.room import room_client
    door = room_client.rooms_door(NODE)
    assert door.endswith("/rooms/")
    with urllib.request.urlopen(door, timeout=5) as r:
        assert r.status == 200


def test_the_room_work_page_answers_with_its_assets(room):
    """Non basta un 200 sulla shell: dalla base scelta devono risolvere
    anche gli ASSET relativi della pagina (../rooms/rooms.js) — è il 200
    sulla base sbagliata (/rooms/work/) che ha ingannato la prima stesura."""
    import urllib.parse
    from modules.s3dgraphy.room import room_client
    url = room_client.room_work_url(NODE, room)
    assert "/work/?room=" in url and "/rooms/work/" not in url
    with urllib.request.urlopen(url, timeout=5) as r:
        assert r.status == 200
    asset = urllib.parse.urljoin(url, "../rooms/rooms.js")
    with urllib.request.urlopen(asset, timeout=5) as r:
        assert r.status == 200
