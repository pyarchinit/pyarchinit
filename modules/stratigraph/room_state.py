"""What pyArchInit and a room last agreed on: the BASE of a three-way compare,
and the cursor to read only what arrived since.

Without a base, a field that differs between the local site and the room says
nothing about WHO changed it: it could be a local edit or a colleague's, so it
was shown and never sent; a relation only one side has could be an addition
here or a removal there. With the room as it was at the last sync (pull, or
send), each difference has an author:

* changed here only → a local edit, which can be sent;
* changed in the room only → the room's, which the pull brings;
* changed on both sides, differently → a conflict, shown;
* present in the base, gone on one side → removed there, not added here.

The base lives in ``<PYARCHINIT_HOME>/stratigraph_rooms/<key>/`` (``base.em.json``
and ``state.json``), one per database + site + node + room. It moves only at a
sync point: after a pull, to the room that was pulled; after a send, by what was
sent — NOT to the room's current state, which may hold others' changes not yet
pulled (taking them in would make them look like local edits to undo).

The room now is read incrementally: the base document plus the operations that
arrived after the cursor (``GET …/ops?after=``), applied with
``s3dgraphy.api.apply_op`` — the function the server applies them with. When
the node cannot serve the cursor (``granted: false``), the whole document is
read again.

Qt-free.
"""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

FEED_PAGE = 500


# ── where the base lives ─────────────────────────────────────────────────────

def _database_identity(connection_url: str) -> str:
    """The database, without its password (the base folder is named from it)."""
    try:
        from sqlalchemy.engine import make_url
        url = make_url(connection_url)
        if url.get_backend_name() == "sqlite":
            return "sqlite:" + os.path.abspath(url.database or "")
        return url.render_as_string(hide_password=True)
    except Exception:                                       # noqa: BLE001
        return str(connection_url).split("@")[-1]


def _home(home: Optional[str] = None) -> str:
    return home or os.environ.get("PYARCHINIT_HOME") or os.path.join(os.path.expanduser("~"), "pyarchinit_5")


def state_dir(connection_url: str, site: str, node: str, room: str, home: Optional[str] = None) -> str:
    key = "|".join((_database_identity(connection_url), site, node.rstrip("/"), room))
    return os.path.join(_home(home), "stratigraph_rooms",
                        hashlib.sha1(key.encode("utf-8")).hexdigest()[:16])


def load(connection_url: str, site: str, node: str, room: str,
         home: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """``{doc, cursor, saved_at, …}`` of the last sync, or None."""
    d = state_dir(connection_url, site, node, room, home)
    try:
        with open(os.path.join(d, "state.json"), encoding="utf-8") as fh:
            state = json.load(fh)
        with open(os.path.join(d, "base.em.json"), encoding="utf-8") as fh:
            state["doc"] = json.load(fh)
    except (OSError, ValueError):
        return None
    return state


def save(connection_url: str, site: str, node: str, room: str, doc: Dict[str, Any],
         cursor: Optional[str], *, how: str, home: Optional[str] = None,
         not_here: Optional[List[str]] = None) -> str:
    """Write the base (the document both sides agree on) and its cursor.
    ``not_here``: ids of the room the pull did not bring here on purpose (a
    generated continuity unit and its media): absent locally, not removed."""
    d = state_dir(connection_url, site, node, room, home)
    os.makedirs(d, exist_ok=True)
    for name, payload in (("base.em.json", doc),
                          ("state.json", {"database": _database_identity(connection_url),
                                          "site": site, "node": node, "room": room,
                                          "cursor": cursor, "how": how,
                                          "not_here": sorted(set(not_here or [])),
                                          "saved_at": datetime.datetime.now(datetime.timezone.utc)
                                          .strftime("%Y-%m-%dT%H:%M:%SZ")})):
        tmp = os.path.join(d, name + ".part")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False)
        os.replace(tmp, os.path.join(d, name))
    return d


def forget(connection_url: str, site: str, node: str, room: str, home: Optional[str] = None) -> None:
    import shutil
    shutil.rmtree(state_dir(connection_url, site, node, room, home), ignore_errors=True)


# ── the room now, incrementally ──────────────────────────────────────────────

def _site_has_rows(connection_url: str, site: str) -> bool:
    try:
        from sqlalchemy import create_engine, text
        with create_engine(connection_url).connect() as conn:
            return conn.execute(text("SELECT 1 FROM us_table WHERE sito = :s LIMIT 1"),
                                {"s": site}).fetchone() is not None
    except Exception:                                       # noqa: BLE001
        return True                                         # cannot tell: keep the base


def _section(doc: Dict[str, Any], graph_id: Optional[str]) -> Optional[Dict[str, Any]]:
    graphs = doc.get("graphs") or {}
    if isinstance(graphs, dict):
        if graph_id in graphs:
            return graphs[graph_id]
        return next(iter(graphs.values()), None) if len(graphs) == 1 else None
    for g in graphs:
        if g.get("graph_id") == graph_id or g.get("id") == graph_id:
            return g
    return graphs[0] if len(graphs) == 1 else None


def ops_after(node: str, room: str, token: str, cursor: str) -> Dict[str, Any]:
    """Every page of ``GET …/ops?after=cursor``: ``{granted, cursor, operations, reason}``."""
    from .node_client import _json, node_base
    out: List[Dict[str, Any]] = []
    after = cursor
    while True:
        url = (f"{node_base(node)}/v1/rooms/{urllib.parse.quote(room, safe='')}/ops?"
               + urllib.parse.urlencode({"after": after, "limit": FEED_PAGE}))
        page = _json(urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"}))
        if not page.get("granted"):
            return {"granted": False, "reason": page.get("reason"), "detail": page.get("detail"),
                    "operations": [], "cursor": None}
        out.extend(page.get("operations") or [])
        after = page.get("cursor") or after
        if not page.get("has_more"):
            return {"granted": True, "cursor": after, "operations": out, "reason": None}


def room_now(connection_url: str, site: str, *, node: str, room: str, token: str,
             home: Optional[str] = None) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]], Dict[str, Any]]:
    """``(answer, base, how)``: the room as ``{doc, cursor}`` like
    ``GET …/document`` gives it, the base (None before the first sync), and how
    the room was read (``incremental`` with the count of operations, or ``full``
    with the reason)."""
    from s3dgraphy.api import apply_op
    from .room_sync import fetch_document
    base = load(connection_url, site, node, room, home)
    if base is not None and not _site_has_rows(connection_url, site):
        # a base for a site this database does not hold (recreated or emptied
        # under the same name): there is no common history any more
        forget(connection_url, site, node, room, home)
        base = None
    if base and base.get("cursor"):
        feed = ops_after(node, room, token, base["cursor"])
        if feed["granted"]:
            doc = copy.deepcopy(base["doc"])
            refused = 0
            for item in feed["operations"]:
                section = _section(doc, item.get("graph_id"))
                if section is None:
                    refused += 1
                    continue
                answer = apply_op(section, item["op"])
                refused += 0 if answer.get("applied") or answer.get("reason") else 1
            return ({"doc": doc, "cursor": feed["cursor"]}, base,
                    {"read": "incremental", "operations": len(feed["operations"])})
        how = {"read": "full", "reason": feed["reason"]}
    else:
        how = {"read": "full", "reason": "no_base"}
    return fetch_document(node, room, token), base, how


# ── moving the base by what was sent ─────────────────────────────────────────

def _set(node: Dict[str, Any], field: str, value: Any, remove: bool) -> None:
    if field.startswith("data."):
        data = node.setdefault("data", {})
        if remove:
            data.pop(field[5:], None)
        else:
            data[field[5:]] = copy.deepcopy(value)
    elif remove:
        node.pop(field, None)
    else:
        node[field] = copy.deepcopy(value)


def advance(doc: Dict[str, Any], graph_id: Optional[str], ops: List[Dict[str, Any]]) -> Dict[str, Any]:
    """The base plus what was just sent (``add_node``, ``add_edge``,
    ``update_field``): a plain write on the em.json, no clocks — the room's own
    log replays the same operations on top idempotently."""
    doc = copy.deepcopy(doc)
    section = _section(doc, graph_id)
    if section is None:
        return doc
    nodes = {n.get("id"): n for n in section.setdefault("nodes", [])}
    edges = {(e.get("source"), e.get("edge_type"), e.get("target")) for e in section.setdefault("edges", [])}
    for op in ops:
        kind = op.get("op")
        if kind == "add_node":
            body = copy.deepcopy(op.get("node") or {})
            body.setdefault("id", op.get("id"))
            if body["id"] not in nodes:
                section["nodes"].append(body)
                nodes[body["id"]] = body
        elif kind == "add_edge":
            triple = (op.get("source"), op.get("edge_type"), op.get("target"))
            if triple not in edges:
                section["edges"].append({"id": op.get("id"), "source": triple[0],
                                         "edge_type": triple[1], "target": triple[2]})
                edges.add(triple)
        elif kind == "update_field" and op.get("node_id") in nodes:
            _set(nodes[op["node_id"]], op.get("field", ""), op.get("value"), bool(op.get("remove")))
        elif kind == "remove_edge":
            section["edges"] = [e for e in section["edges"] if e.get("id") != op.get("id")]
    return doc
