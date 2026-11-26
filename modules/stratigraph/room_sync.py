"""A pyArchInit site and a StratiGraph room, in both directions.

Two questions E.D. asked on 26 Nov 2026, and the answer to each:

* **«Can pyArchInit be rebuilt from a room, in its own data structure?»** —
  ``pull_room``: the room's document (em.json) goes through pyArchInit's own
  ingestor into the native tables (us_table, periodizzazione…), rows matched
  by ``node_uuid``. A dry run by default; the report separates what differs
  only in FORMAT (``[type, us]`` written as ``[type, us, area, site]``) from
  what really differs. Applying a pull that would REMOVE relations the local
  site has and the room does not is refused unless asked for explicitly:
  without a common base nobody can tell «removed in the room» from «never
  known to the room» (a continuity relation the export does not carry, for
  instance).
* **«Connected to a room that already holds data, what is pyArchInit adding?»**
  — ``contribution``: the local site against the room, with
  ``s3dgraphy.em.write.diff``. ``push_new`` sends only the ADDITIONS (new
  nodes, new relations): a field that differs is shown, not sent, because a
  room value may be someone's newer edit; and what others added in the room
  is never removed.

The site always travels as ONE graph (``per_saggio=False``): s3dgraphy's
room import seats each graph's nodes and edges but not the links between
graphs, so a site split by trench lost its cross-trench relations on the way
(measured: 32 links in the export, 0 in the room).

Qt-free; the dialog and the command line call the same functions.
"""
from __future__ import annotations

import ast
import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from .node_client import NodeError, _json, node_base


# ── the room's document ──────────────────────────────────────────────────────

def fetch_document(node: str, room: str, token: str) -> Dict[str, Any]:
    """``GET /v1/rooms/{room}/document`` → ``{doc, cursor, role, can_write…}``."""
    url = f"{node_base(node)}/v1/rooms/{urllib.parse.quote(room, safe='')}/document"
    return _json(urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"}))


def room_graph(answer: Dict[str, Any], workdir: str) -> Tuple[Any, str, str]:
    """The room as ONE s3dgraphy graph: ``(graph, graph_id, em_json_path)``.
    A room with several graphs is merged (``container.merge_graphs``)."""
    from s3dgraphy.container import load_container_file, merge_graphs
    os.makedirs(workdir, exist_ok=True)
    path = os.path.join(workdir, "room.em.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(answer.get("doc") or {}, fh, ensure_ascii=False)
    container, _warnings = load_container_file(path)
    if not container.graphs:
        raise NodeError("the room holds no graph yet")
    if len(container.graphs) == 1:
        (gid, graph), = container.graphs.items()
        return graph, gid, path
    graph, _report = merge_graphs(container)
    return graph, str(answer.get("doc", {}).get("active_graph_id") or next(iter(container.graphs))), path


def local_graph(connection_url: str, site: str, workdir: str) -> Tuple[Any, str]:
    """The local site as ONE graph, through pyArchInit's own exporter."""
    from modules.s3dgraphy import em_export
    from s3dgraphy.container import load_container_file
    out = os.path.join(workdir, "local")
    os.makedirs(out, exist_ok=True)
    path, _n, _e, _w = em_export.export_site(connection_url, site, out, per_saggio=False)
    from .room_media import add_media_resources
    from .room_records import add_unit_records
    add_unit_records(path, connection_url, site)           # the whole records, as in send_site
    add_media_resources(path, connection_url, site)        # the unit media, as in send_site
    container, _ = load_container_file(path)
    (_gid, graph), = container.graphs.items()
    return graph, path


# ── room → pyArchInit ────────────────────────────────────────────────────────

def _pairs(value) -> Optional[set]:
    """A rapporti field as a set of (type, target unit), area and site aside."""
    try:
        items = ast.literal_eval(value) if isinstance(value, str) else (value or [])
    except (ValueError, SyntaxError):
        return None
    return {(str(x[0]), str(x[1])) for x in items if isinstance(x, (list, tuple)) and len(x) >= 2}


def classify(result, rows_by_uuid: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
    """The ingest's conflicts, split: format only / real, and per real one
    what only the local row has and what only the room has."""
    format_only, real = 0, []
    for c in result.conflicts:
        if c.field == "rapporti":
            local, room = _pairs(c.db_value), _pairs(c.graph_value)
            if local is not None and local == room:
                format_only += 1
                continue
            us, tipo = rows_by_uuid.get(c.node_uuid, ("?", "?"))
            real.append({"field": "rapporti", "us": us, "unita_tipo": tipo,
                         "only_local": sorted(local - room) if local is not None and room is not None else [],
                         "only_room": sorted(room - local) if local is not None and room is not None else []})
        else:
            us, tipo = rows_by_uuid.get(c.node_uuid, ("?", "?"))
            real.append({"field": c.field, "us": us, "unita_tipo": tipo,
                         "local": c.db_value, "room": c.graph_value})
    return {"format_only": format_only, "real": real}


def _rows_by_uuid(connection_url: str, site: str) -> Dict[str, Tuple[str, str]]:
    from sqlalchemy import create_engine, text
    with create_engine(connection_url).connect() as conn:
        return {str(u): (str(us), str(ut)) for u, us, ut in conn.execute(
            text("SELECT node_uuid, us, unita_tipo FROM us_table WHERE sito = :s"), {"s": site})
            if u}


def pull_room(connection_url: str, site: str, *, node: str, room: str, token: str,
              workdir: str, apply: bool = False, force: bool = False,
              media: bool = True) -> Dict[str, Any]:
    """The room into the site's native tables. Dry run unless ``apply``;
    an apply that would drop local relations needs ``force``."""
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor

    answer = fetch_document(node, room, token)
    graph, gid, path = room_graph(answer, workdir)
    rows = _rows_by_uuid(connection_url, site)
    plan = GraphIngestor().populate_list(graph, db_path=connection_url, sito=site,
                                         dry_run=True, create_missing_epochs=True)
    kinds = classify(plan, rows)
    drops = [r for r in kinds["real"] if r.get("only_local")]
    report = {"room": room, "graph_id": gid, "cursor": answer.get("cursor"), "em_json": path,
              "inserted": plan.inserted, "updated": plan.updated, "skipped": plan.skipped,
              "format_only": kinds["format_only"], "real": kinds["real"],
              "errors": list(plan.errors), "applied": False}
    if not apply:
        if media:
            from .room_media import pull_media
            report["media"] = pull_media(connection_url, site, graph, path, node=node,
                                         room=room, token=token, dry_run=True)
        return report
    if drops and not force:
        raise NodeError(
            f"applying the room would remove {sum(len(r['only_local']) for r in drops)} "
            f"relation(s) of {len(drops)} local unit(s) that the room does not have "
            f"(e.g. US {drops[0]['us']}: {drops[0]['only_local'][:3]}); "
            "review them, then apply with force")
    done = GraphIngestor().populate_list(graph, db_path=connection_url, sito=site,
                                         dry_run=False, create_missing_epochs=True)
    report.update({"inserted": done.inserted, "updated": done.updated, "skipped": done.skipped,
                   "errors": list(done.errors), "applied": True})
    if media:
        # after the units: the media attach to their id_us
        from modules.s3dgraphy.sync.graph_ingestor import hydrate_row_fields_from_data
        from .room_media import pull_media
        hydrate_row_fields_from_data(graph)
        report["media"] = pull_media(connection_url, site, graph, path, node=node,
                                     room=room, token=token)
    return report


# ── pyArchInit → room ────────────────────────────────────────────────────────

def _map_only(graph) -> set:
    """The GIS footprint chain and the resource its plan points at: map
    artefacts the export rebuilds, with ids that follow the database file's
    path — not excavation data, in either direction."""
    from modules.s3dgraphy.sync.graph_ingestor import footprint_chain_ids
    ids = set(footprint_chain_ids(graph))
    for e in getattr(graph, "edges", None) or []:
        if e.edge_type == "has_linked_resource" and e.edge_source in ids:
            ids.add(e.edge_target)
    return ids


def _without_noise(delta, skip: set, resources: frozenset = frozenset()):
    """The delta minus map artefacts, minus ``data.lang`` the node adds
    (``und``) where the local node simply has none, and minus
    ``data.rapporti`` — a text copy of the relations, which the delta
    already carries as edges."""
    delta.nodes = [n for n in delta.nodes if n.get("id") not in skip]
    delta.edges = [e for e in delta.edges if e.get("source") not in skip and e.get("target") not in skip]
    keep = []
    for op in delta.ops:
        if op.get("id") in skip or op.get("node_id") in skip:
            continue
        if op.get("op") == "update_field" and op.get("field") == "data.lang" and op.get("remove"):
            continue
        if op.get("op") == "update_field" and op.get("field") == "data.rapporti":
            continue      # the text copy of the relations: they travel as edges
        if (op.get("op") == "update_field" and op.get("node_id") in resources
                and str(op.get("field", "")).startswith("data.")):
            continue      # where a file's bytes live (local path, room store): not an edit
        keep.append(op)
    delta.ops = keep
    return delta


def contribution(connection_url: str, site: str, *, node: str, room: str, token: str,
                 workdir: str) -> Dict[str, Any]:
    """What the local site adds to the room: new nodes, new relations, fields
    that differ (shown, not sent), and what only the room has (others' work,
    never touched)."""
    from s3dgraphy.em.write import _snapshot, diff

    answer = fetch_document(node, room, token)
    remote, gid, _ = room_graph(answer, workdir)
    local, local_path = local_graph(connection_url, site, workdir)
    resources = {n.node_id for n in list(local.nodes) + list(remote.nodes)
                 if getattr(n, "node_type", "") == "resource"}
    delta = _without_noise(diff(_snapshot(remote), local), _map_only(local) | _map_only(remote),
                           resources)
    names = {n.node_id: n.name for n in list(local.nodes) + list(remote.nodes)}
    changes = [op for op in delta.ops if op.get("op") == "update_field"]
    room_only = [op for op in delta.ops if op.get("op") in ("remove_node", "remove_edge")]
    return {"room": room, "graph_id": gid, "cursor": answer.get("cursor"),
            "local_em_json": local_path, "delta": delta,
            "new_nodes": [names.get(n.get("id"), n.get("id")) for n in delta.nodes],
            "new_edges": len(delta.edges),
            "field_changes": [(names.get(op["node_id"], op["node_id"]), op["field"]) for op in changes],
            "room_only": len(room_only)}


def push_new(found: Dict[str, Any], *, node: str, room: str, token: str) -> Dict[str, Any]:
    """Send only the additions of a ``contribution``: ``add_node`` and
    ``add_edge``, into the room's graph. Idempotent on the node's side."""
    from s3dgraphy.room_import import node as nodeio
    delta = found["delta"]
    uploaded = 0
    for n in delta.nodes:
        data = n.get("data") or {}
        local = str(data.get("url") or "")
        if n.get("node_type") == "resource" and local and os.path.isfile(local):
            # the bytes first, then the node that points at them
            from s3dgraphy.room_import.inventory import media_type_for
            put = nodeio.upload_asset(node_base(node), room, local, None,
                                      media_type_for(local), token)
            data["url"] = put["url"]
            data["checksum"] = f"sha256:{put['sha256']}"
            data["addresses"] = [{"locator": local}]
            n["data"] = data
            uploaded += 0 if put.get("already") else 1
    ops: List[Dict[str, Any]] = [{"op": "add_node", "id": n["id"], "node": n} for n in delta.nodes]
    ops += [{"op": "add_edge", "id": e["id"], "source": e["source"], "target": e["target"],
             "edge_type": e["edge_type"]} for e in delta.edges]
    if not ops:
        return {"applied": 0, "refused": [], "requests": 0, "uploaded": 0}
    sent = nodeio.send_ops(node_base(node), token, room, ops, graph_id=found["graph_id"])
    sent["uploaded"] = uploaded
    return sent
