"""The base of a three-way compare, without a node.

Measured on the dev-stack (26 Nov 2026) with two computers on one room: a
field changed by B reached A as «changed in the room»; the same field changed
on both sides was a conflict; A's pull was refused until A sent its work; a
relation a colleague removed in the room was removed here without asking; a
relation removed here was sent, and reached the other computer.
"""
from __future__ import annotations

import json
from types import SimpleNamespace

from modules.stratigraph import room_state as ST
from modules.stratigraph import room_sync as RS


def _doc(nodes, edges):
    return {"graphs": {"S": {"graph_id": "S", "nodes": nodes, "edges": edges}}}


def _unit(nid, us, **data):
    return {"id": nid, "node_type": "US", "name": f"1.US{us}", "description": "",
            "data": dict({"us": us, "node_uuid": nid}, **data)}


def _graph(tmp_path, doc, name):
    graph, _gid, _ = RS.room_graph({"doc": doc}, str(tmp_path), name)
    return graph


def _rel(a, b):
    return {"id": f"{a}_overlies_{b}", "source": a, "target": b, "edge_type": "overlies"}


def test_every_difference_gets_its_author(tmp_path):
    from s3dgraphy.em.write import _snapshot, diff
    base = _doc([_unit("u1", "1", colore="Bruno"), _unit("u2", "2", colore="Grigio"),
                 _unit("u3", "3", descrizione="Strato"), _unit("u4", "4")],
                [_rel("u1", "u2"), _rel("u3", "u4")])
    room = _doc([_unit("u1", "1", colore="Bruno"), _unit("u2", "2", colore="Rosso"),
                 _unit("u3", "3", descrizione="Rivista nella stanza"), _unit("u4", "4")],
                [_rel("u1", "u2")])                       # the room removed u3→u4
    local = _doc([_unit("u1", "1", colore="Giallo"), _unit("u2", "2", colore="Verde"),
                  _unit("u3", "3", descrizione="Strato"), _unit("u4", "4"), _unit("u5", "5")],
                 [_rel("u3", "u4"), _rel("u4", "u5")])  # removed u1→u2 here, added u4→u5
    B, R, L = (_graph(tmp_path, d, n) for d, n in ((base, "b.json"), (room, "r.json"), (local, "l.json")))
    tw = RS.three_way(diff(_snapshot(R), L), B, R, L)
    assert [op["field"] for op in tw["send_fields"]] == ["data.colore"]            # u1: here only
    assert [c["node_id"] for c in tw["conflicts"]] == ["u2"]                       # u2: both sides
    assert [(op["node_id"], op["field"]) for op in tw["room_fields"]] == [("u3", "data.descrizione")]
    assert [n["id"] for n in tw["send_nodes"]] == ["u5"]
    assert [(e["source"], e["target"]) for e in tw["send_edges"]] == [("u4", "u5")]
    assert tw["removed_in_room"] == 1                                              # u3→u4
    assert tw["removed_here"] == 1 and tw["send_removals"][0]["triple"] == ("u1", "overlies", "u2")


def test_what_the_pull_left_in_the_room_is_not_a_removal(tmp_path):
    from s3dgraphy.em.write import _snapshot, diff
    base = room = _doc([_unit("u1", "1"), _unit("con", "500")], [_rel("u1", "con")])
    local = _doc([_unit("u1", "1")], [])
    B, R, L = (_graph(tmp_path, d, n) for d, n in ((base, "b.json"), (room, "r.json"), (local, "l.json")))
    tw = RS.three_way(diff(_snapshot(R), L), B, R, L, frozenset({"con"}))
    assert tw["removed_here"] == 0 and tw["room_added"] == 1 and tw["send_removals"] == []   # the node takes its relation


def test_tombstones_are_not_read_as_live():
    doc = _doc([_unit("u1", "1"), dict(_unit("u2", "2"), attributes={"removed": {"ts": "x", "author": "a"}})],
               [_rel("u1", "u2"), dict(_rel("u2", "u1"))])
    from s3dgraphy.crdt import is_removed
    live = RS.live_document(doc)["graphs"]["S"]
    assert [n["id"] for n in live["nodes"]] == [n["id"] for n in doc["graphs"]["S"]["nodes"]
                                                 if not is_removed(n)]
    assert all(e["source"] in {n["id"] for n in live["nodes"]} for e in live["edges"])


def test_the_base_moves_by_what_was_sent_only():
    base = _doc([_unit("u1", "1", colore="Bruno")], [_rel("u1", "u1")])
    moved = ST.advance(base, "S", [
        {"op": "add_node", "id": "u9", "node": _unit("u9", "9")},
        {"op": "add_edge", "id": "e", "source": "u1", "target": "u9", "edge_type": "overlies"},
        {"op": "update_field", "node_id": "u1", "field": "data.colore", "value": "Giallo"},
        {"op": "remove_edge", "id": "u1_overlies_u1"}])
    sec = moved["graphs"]["S"]
    assert [n["id"] for n in sec["nodes"]] == ["u1", "u9"]
    assert sec["nodes"][0]["data"]["colore"] == "Giallo"
    assert [(e["source"], e["target"]) for e in sec["edges"]] == [("u1", "u9")]
    assert base["graphs"]["S"]["nodes"][0]["data"]["colore"] == "Bruno"         # a copy


def test_the_room_is_read_from_the_cursor_and_again_whole_when_refused(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'x.sqlite'}"
    ST.save(url, "S", "https://n/em", "r", _doc([_unit("u1", "1", colore="Bruno")], []),
            "c:1", how="pull", home=str(tmp_path))
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))
    feed = {"granted": True, "cursor": "c:2", "reason": None, "operations": [
        {"graph_id": "S", "op": {"op": "update_field", "node_id": "u1", "field": "data.colore",
                                 "value": "Rosso", "ts": "2026-11-26T10:00:00.000Z",
                                 "author": "0000-0000-0000-0000"}}]}
    monkeypatch.setattr(ST, "ops_after", lambda *a, **k: feed)
    answer, base, how = ST.room_now(url, "S", node="https://n/em", room="r", token="t")
    assert how == {"read": "incremental", "operations": 1} and answer["cursor"] == "c:2"
    assert answer["doc"]["graphs"]["S"]["nodes"][0]["data"]["colore"] == "Rosso"
    assert base["doc"]["graphs"]["S"]["nodes"][0]["data"]["colore"] == "Bruno"   # the base stays
    monkeypatch.setattr(ST, "ops_after", lambda *a, **k: {"granted": False, "reason": "unknown_cursor",
                                                          "operations": [], "cursor": None})
    monkeypatch.setattr(RS, "fetch_document", lambda *a: {"doc": {"graphs": {}}, "cursor": "c:9"})
    answer, _b, how = ST.room_now(url, "S", node="https://n/em", room="r", token="t")
    assert how == {"read": "full", "reason": "unknown_cursor"} and answer["cursor"] == "c:9"


def test_the_base_folder_never_carries_the_password(tmp_path):
    d = ST.state_dir("postgresql://postgres:segreta@localhost:5433/db", "S", "n", "r", str(tmp_path))
    ST.save("postgresql://postgres:segreta@localhost:5433/db", "S", "n", "r", _doc([], []), None,
            how="pull", home=str(tmp_path))
    assert "segreta" not in d and "segreta" not in open(f"{d}/state.json").read()


def test_a_relation_the_pull_could_not_reproduce_is_not_a_removal(tmp_path):
    from s3dgraphy.em.write import _snapshot, diff
    base = room = _doc([_unit("u1", "1"), _unit("u2", "2")], [_rel("u1", "u2")])
    local = _doc([_unit("u1", "1"), _unit("u2", "2")], [])
    B, R, L = (_graph(tmp_path, d, n) for d, n in ((base, "b.json"), (room, "r.json"), (local, "l.json")))
    tw = RS.three_way(diff(_snapshot(R), L), B, R, L, frozenset({"u1|overlies|u2"}))
    assert tw["removed_here"] == 0 and tw["send_removals"] == []
