"""Il filo verso la stanza, provato con un nodo FINTO iniettabile (C, piano
2026-10-07). Le regole: configurazione per ambiente; identità esatta dal
preflight /v1/health; pagine ≤1000 senza retry; refused-in-200 non è un
errore; mai graph_id."""
from __future__ import annotations

import sys
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


class FakeNode:
    """Un nodo finto: registra le chiamate, risponde come quello vero."""

    def __init__(self, auth="dev-no-auth", applied_all=True):
        self.calls = []
        self.auth = auth
        self.applied_all = applied_all

    def __call__(self, method, url, payload, token):
        self.calls.append((method, url, payload, token))
        if url.endswith("/v1/health"):
            return 200, {"ok": True, "auth": self.auth}
        if "/ops" in url:
            ops = payload["ops"]
            if self.applied_all:
                return 200, {"applied": len(ops), "refused": [], "kept": None}
            return 200, {"applied": 0,
                         "refused": [{"id": o["id"], "reason": "idempotent"}
                                     for o in ops], "kept": None}
        raise AssertionError(url)


def _settings(monkeypatch, url="http://127.0.0.1:9", room="r1", token=""):
    monkeypatch.setenv("STRATIGRAPH_SERVER_URL", url)
    monkeypatch.setenv("STRATIGRAPH_ROOM_ID", room)
    if token:
        monkeypatch.setenv("STRATIGRAPH_TOKEN", token)
    else:
        monkeypatch.delenv("STRATIGRAPH_TOKEN", raising=False)
    from modules.s3dgraphy.room.room_client import NodeSettings
    return NodeSettings()


def test_no_settings_no_delivery_and_no_network(monkeypatch, tmp_path):
    monkeypatch.delenv("STRATIGRAPH_SERVER_URL", raising=False)
    monkeypatch.delenv("STRATIGRAPH_ROOM_ID", raising=False)
    from modules.s3dgraphy.room import room_client
    # il fallback QSettings legge le preferenze REALI dell'utente: un uso
    # manuale precedente del dialogo non deve rendere flaky questo test
    monkeypatch.setattr(room_client, "_qsetting", lambda key: "")
    node = FakeNode()
    with pytest.raises(room_client.RoomRefusal) as err:
        room_client.deliver_site("sqlite:///nowhere", "S",
                                 settings=room_client.NodeSettings(),
                                 http=node)
    assert "STRATIGRAPH_SERVER_URL" in str(err.value)
    assert node.calls == [], "niente configurazione → niente rete"


def test_enforcing_auth_without_token_refuses_before_any_ops(monkeypatch):
    from modules.s3dgraphy.room import room_client
    st = _settings(monkeypatch)                       # nessun token
    node = FakeNode(auth="keycloak")
    with pytest.raises(room_client.RoomRefusal) as err:
        room_client._require_identity(st, node)
    assert "STRATIGRAPH_TOKEN" in str(err.value)
    assert [c for c in node.calls if "/ops" in c[1]] == []


def test_batches_are_capped_at_1000_and_all_arrive(monkeypatch):
    from modules.s3dgraphy.room import room_client
    st = _settings(monkeypatch)
    node = FakeNode()
    ops = [{"op": "add_node", "id": "n%d" % i, "node": {}}
           for i in range(2300)]
    out = room_client._deliver_ops(ops, st, node)
    posts = [c for c in node.calls if "/ops" in c[1]]
    assert [len(c[2]["ops"]) for c in posts] == [1000, 1000, 300]
    assert out.sent == 2300 and out.applied == 2300 and out.batches == 3
    assert all("graph_id" not in c[2] for c in posts), \
        "una stanza, un grafo vivo: mai graph_id"


def test_a_repeat_reads_as_already_delivered(monkeypatch):
    from modules.s3dgraphy.room import room_client
    st = _settings(monkeypatch)
    node = FakeNode(applied_all=False)                # tutto idempotent
    ops = [{"op": "add_edge", "id": "e%d" % i} for i in range(4)]
    out = room_client._deliver_ops(ops, st, node)
    assert out.idempotent == 4 and out.a_repeat
    assert "già presenti" in out.summary()


def test_a_network_error_is_a_sentence_not_a_traceback(monkeypatch):
    from modules.s3dgraphy.room import room_client
    st = _settings(monkeypatch)

    def dead(method, url, payload, token):
        raise OSError("connection refused")

    with pytest.raises(room_client.RoomRefusal) as err:
        room_client._deliver_ops([{"op": "add_node", "id": "n1"}], st, dead)
    assert "riprova" in str(err.value) or "raggiung" in str(err.value)


def test_rooms_door_prefers_the_caddy_path(monkeypatch):
    from modules.s3dgraphy.room import room_client

    def node(method, url, payload, token):
        return (200, {}) if url.endswith("/em/rooms/") else (404, {})

    assert room_client.rooms_door("http://x", http=node).endswith("/em/rooms/")

    def bare(method, url, payload, token):
        return (200, {}) if url.endswith("/rooms/") and "/em/" not in url \
            else (404, {})

    assert room_client.rooms_door("http://x", http=bare).endswith("/rooms/")
