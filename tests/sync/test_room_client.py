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
    assert all("author" not in op for c in posts for op in c[2]["ops"]), \
        "l'autore lo scrive il server: mai nel payload (spec §6)"


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


def test_the_menu_offers_delivery_and_the_node_door():
    import re
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    src = (root / "pyarchinitPlugin.py").read_text(encoding="utf-8")
    assert "Consegna sito alla stanza" in src
    assert "deliver_site" in src and "rooms_door" in src
    unload = re.search(r"def unload\(self\):(.*?)\n    def ", src, re.S)
    assert unload and "actionRoomDelivery" in unload.group(1)
    assert "actionRoomOpen" in unload.group(1)


def test_a_db_failure_is_a_sentence_not_a_traceback(monkeypatch, tmp_path):
    """I5 review: un DB senza us_table (o PG giù) non deve arrivare
    all'utente come dialogo d'errore Python."""
    import sqlite3
    from modules.s3dgraphy.room import room_client
    db = tmp_path / "bare.sqlite"
    sqlite3.connect(db).close()
    st = _settings(monkeypatch)
    node = FakeNode()
    with pytest.raises(room_client.RoomRefusal) as err:
        room_client.deliver_site("sqlite:///%s" % db, "S",
                                 settings=st, http=node)
    assert "us_table" in str(err.value) or "database" in str(err.value)


def test_a_node_behind_caddy_is_found_at_slash_em(monkeypatch):
    """I3 review: dietro Caddy l'API vive su /em/v1/… — un utente che
    scrive la radice dell'host deve essere capito, non respinto con un 404
    travestito da nodo irraggiungibile."""
    from modules.s3dgraphy.room import room_client

    class CaddyNode(FakeNode):
        def __call__(self, method, url, payload, token):
            if url.endswith("/v1/health") and "/em/" not in url:
                raise OSError("HTTP Error 404: Not Found")
            return super().__call__(method, url, payload, token)

    st = _settings(monkeypatch, url="http://nodo.ente.it")
    node = CaddyNode()
    health = room_client._require_identity(st, node)
    assert health.get("ok")
    assert st.server_url == "http://nodo.ente.it/em", \
        "la base risolta resta sulle settings: le ops vanno su /em/v1"


def _http_error(code, detail, url="http://x/v1/rooms/r1/ops"):
    import io
    import json as _json
    import urllib.error
    return urllib.error.HTTPError(
        url, code, "err", {}, io.BytesIO(_json.dumps({"detail": detail}).encode()))


def test_a_403_is_one_sentence_with_the_servers_detail(monkeypatch):
    """Minor 7 review: il ramo HTTPError non aveva un test — 403/413 devono
    diventare UNA frase col detail del server, mai un traceback."""
    from modules.s3dgraphy.room import room_client
    st = _settings(monkeypatch)

    def forbidden(method, url, payload, token):
        raise _http_error(403, "writing operations into this room needs "
                               "editor or above")

    with pytest.raises(room_client.RoomRefusal) as err:
        room_client._deliver_ops([{"op": "add_node", "id": "n1"}], st,
                                 forbidden)
    assert "403" in str(err.value) and "editor" in str(err.value)


def test_a_413_shrinks_the_pages_to_what_the_node_accepts(monkeypatch):
    """Minor 9 review: OPS_BATCH_MAX è configurabile sul nodo e la health
    non lo espone — sul 413 il client legge la taglia dal detail e
    ri-pagina il lotto (la pagina respinta non era stata applicata:
    non è un retry di un rifiuto)."""
    from modules.s3dgraphy.room import room_client
    st = _settings(monkeypatch)
    calls = []

    def small_node(method, url, payload, token):
        ops = payload["ops"]
        calls.append(len(ops))
        if len(ops) > 2:
            raise _http_error(
                413, "%d operations in one request, and this node accepts 2."
                     " The limit is the room's lock" % len(ops))
        return 200, {"applied": len(ops), "refused": [], "kept": None}

    ops = [{"op": "add_node", "id": "n%d" % i} for i in range(5)]
    out = room_client._deliver_ops(ops, st, small_node)
    assert calls == [5, 2, 2, 1]
    assert out.applied == 5 and out.batches == 3


def test_a_mid_delivery_refusal_reports_what_landed(monkeypatch):
    """Minor 8 review: se una pagina successiva viene rifiutata, la frase
    dice quante operazioni erano GIÀ arrivate."""
    from modules.s3dgraphy.room import room_client
    st = _settings(monkeypatch)
    state = {"page": 0}

    def flaky(method, url, payload, token):
        state["page"] += 1
        if state["page"] == 1:
            return 200, {"applied": len(payload["ops"]), "refused": []}
        raise _http_error(403, "token expired")

    monkeypatch.setattr(room_client, "BATCH_MAX", 3)
    ops = [{"op": "add_node", "id": "n%d" % i} for i in range(5)]
    with pytest.raises(room_client.RoomRefusal) as err:
        room_client._deliver_ops(ops, st, flaky)
    msg = str(err.value)
    assert "3" in msg and "5" in msg, msg


def test_a_clear_text_token_is_named_before_it_travels(monkeypatch):
    """Minor 12 review: un token su http:// verso un nodo non locale
    viaggia in chiaro — il chiamante deve poterlo dire PRIMA."""
    from modules.s3dgraphy.room import room_client
    st = _settings(monkeypatch, url="http://nodo.ente.it", token="segreto")
    assert room_client.token_in_the_clear(st) is True
    st = _settings(monkeypatch, url="http://127.0.0.1:8020", token="segreto")
    assert room_client.token_in_the_clear(st) is False
    st = _settings(monkeypatch, url="https://nodo.ente.it", token="segreto")
    assert room_client.token_in_the_clear(st) is False
    st = _settings(monkeypatch, url="http://nodo.ente.it")
    assert room_client.token_in_the_clear(st) is False


def test_probes_use_a_short_timeout():
    """Minor 10 review (metà client): le sonde (health, porta della UI) non
    tengono in ostaggio il chiamante per 30 s l'una."""
    from modules.s3dgraphy.room import room_client
    assert room_client.PROBE_TIMEOUT <= 5
    import inspect
    src = inspect.getsource(room_client.rooms_door)
    sig = inspect.signature(room_client.rooms_door)
    assert sig.parameters["http"].default is room_client._probe_http


def test_the_delivery_does_not_run_on_the_gui_thread():
    """Minor 10 review (metà menu): la consegna gira in un QgsTask, con
    l'esito mostrato al completamento — QGIS non gela a nodo muto."""
    from pathlib import Path as _P
    src = (_P(__file__).resolve().parents[2]
           / "pyarchinitPlugin.py").read_text(encoding="utf-8")
    assert "QgsTask.fromFunction" in src
    body = src.split("def _run_room_delivery", 1)[1].split("\n    def ", 1)[0]
    assert "deliver_site" in body and "QgsTask" in body


def test_env_locked_fields_say_so():
    """Minor 11 review: se l'env è impostata vince lei — il campo nel
    dialogo lo DICE (sola lettura) invece di fingere di accettare."""
    from pathlib import Path as _P
    src = (_P(__file__).resolve().parents[2]
           / "pyarchinitPlugin.py").read_text(encoding="utf-8")
    body = src.split("def _run_room_delivery", 1)[1].split("\n    def ", 1)[0]
    assert "setReadOnly" in body and "SERVER_URL_VARIABLE" in body


def test_room_work_url_points_at_the_stable_per_room_address(monkeypatch):
    """B2: «/em/work/?room=<id>» è l'indirizzo stabile per stanza
    (rooms_ui/rooms.js:1745); sul nodo nudo la stessa pagina vive sotto
    /rooms/work/. L'id viaggia quotato."""
    from modules.s3dgraphy.room import room_client

    def bare(method, url, payload, token):
        return (200, {}) if "/rooms/work/" in url and "/em/" not in url \
            else (404, {})

    url = room_client.room_work_url("http://x", "scavo 2026/α", http=bare)
    assert url == "http://x/rooms/work/?room=scavo%202026%2F%CE%B1"

    def caddy(method, url, payload, token):
        return (200, {}) if "/em/work/" in url else (404, {})

    url = room_client.room_work_url("http://x", "r1", http=caddy)
    assert url == "http://x/em/work/?room=r1"


def test_room_work_url_never_raises_on_a_mute_node(monkeypatch):
    from modules.s3dgraphy.room import room_client

    def dead(method, url, payload, token):
        raise OSError("no route to host")

    url = room_client.room_work_url("http://x", "r1", http=dead)
    assert url.endswith("/em/work/?room=r1")
