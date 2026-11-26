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


def live_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """The room's document without what was removed in it. A removal in a
    room is a TOMBSTONE (the node or edge stays, marked removed, so a late
    edit cannot bring it back): read as live, a relation a colleague removed
    was still «there», and a pull never removed it here (found 26 Nov 2026)."""
    import copy
    from s3dgraphy.crdt import live_edges, live_nodes
    doc = copy.deepcopy(doc)
    graphs = doc.get("graphs") or {}
    for section in (graphs.values() if isinstance(graphs, dict) else graphs):
        nodes = live_nodes(section)
        alive = {n.get("id") for n in nodes}
        section["nodes"] = nodes
        section["edges"] = [e for e in live_edges(section)
                            if e.get("source") in alive and e.get("target") in alive]
    return doc


def room_graph(answer: Dict[str, Any], workdir: str, name: str = "room.em.json") -> Tuple[Any, str, str]:
    """The room as ONE s3dgraphy graph: ``(graph, graph_id, em_json_path)``.
    A room with several graphs is merged (``container.merge_graphs``)."""
    from s3dgraphy.container import load_container_file, merge_graphs
    os.makedirs(workdir, exist_ok=True)
    path = os.path.join(workdir, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(live_document(answer.get("doc") or {}), fh, ensure_ascii=False)
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

def _pairs(value, area: str = "", site: str = "") -> Optional[set]:
    """A rapporti field as a set of ``(type, us, area, site)`` — pyArchInit's
    four elements. An empty area or site is the unit's own (how pyArchInit
    reads ``['Copre', '2', '', '']``), so it equals the written-out form;
    the same number in ANOTHER area is another unit."""
    try:
        items = ast.literal_eval(value) if isinstance(value, str) else (value or [])
    except (ValueError, SyntaxError):
        return None
    out = set()
    for x in items:
        if not isinstance(x, (list, tuple)) or len(x) < 2:
            continue
        a = str(x[2]).strip() if len(x) > 2 and str(x[2] or "").strip() else str(area or "")
        z = str(x[3]).strip() if len(x) > 3 and str(x[3] or "").strip() else str(site or "")
        out.add((str(x[0]).strip(), str(x[1]).strip(), a, z))
    return out


def classify(result, rows_by_uuid: Dict[str, Tuple[str, ...]], site: str = "") -> Dict[str, Any]:
    """The ingest's conflicts, split: format only / real, and per real one
    what only the local row has and what only the room has."""
    format_only, real = 0, []
    for c in result.conflicts:
        if c.field == "rapporti":
            row = tuple(rows_by_uuid.get(c.node_uuid, ("?", "?", "")))
            us, tipo, area = (row + ("",))[:3]
            local, room = _pairs(c.db_value, area, site), _pairs(c.graph_value, area, site)
            if local is not None and local == room:
                format_only += 1
                continue
            real.append({"field": "rapporti", "us": us, "unita_tipo": tipo,
                         "only_local": sorted(local - room) if local is not None and room is not None else [],
                         "only_room": sorted(room - local) if local is not None and room is not None else []})
        else:
            us, tipo = tuple(rows_by_uuid.get(c.node_uuid, ("?", "?")))[:2]
            real.append({"field": c.field, "us": us, "unita_tipo": tipo,
                         "local": c.db_value, "room": c.graph_value})
    return {"format_only": format_only, "real": real}


def _rows_by_uuid(connection_url: str, site: str) -> Dict[str, Tuple[str, str, str]]:
    from sqlalchemy import create_engine, text
    with create_engine(connection_url).connect() as conn:
        return {str(u): (str(us), str(ut), str(area or "")) for u, us, ut, area in conn.execute(
            text("SELECT node_uuid, us, unita_tipo, area FROM us_table WHERE sito = :s"), {"s": site})
            if u}


def _site_exists(connection_url: str, site: str) -> bool:
    from sqlalchemy import create_engine, text
    with create_engine(connection_url).connect() as conn:
        return conn.execute(text("SELECT 1 FROM site_table WHERE sito = :s"),
                            {"s": site}).fetchone() is not None


def _site_identity(connection_url: str, site: str, graph) -> None:
    """A site row the pull CREATED takes the identity the site has in the
    room (its toponym group's ``entity_uuid``): with the one generated on
    insert the next export gave the site another id and its units' location
    links came out «new» (measured on PostgreSQL, 26 Nov 2026). Called only
    for a site the database did not have: an existing site is never
    touched."""
    from sqlalchemy import create_engine, inspect, text
    ident = None
    for n in getattr(graph, "nodes", None) or []:
        data = getattr(n, "data", None) or {}
        # the room's own site node carries entity_uuid; the ingestor adds a
        # site group of its own (no entity_uuid) that must not be taken
        if (type(n).__name__ == "LocationNodeGroup" and data.get("level") == "sito"
                and str(getattr(n, "name", "")) == site and data.get("entity_uuid")):
            ident = data["entity_uuid"]
            break
    if not ident:
        return
    engine = create_engine(connection_url)
    if "entity_uuid" not in {c["name"] for c in inspect(engine).get_columns("site_table")}:
        return
    with engine.begin() as conn:
        conn.execute(text("UPDATE site_table SET entity_uuid = :u WHERE sito = :s"),
                     {"u": str(ident), "s": site})


def _unsent(found: Optional[Dict[str, Any]]) -> Dict[str, list]:
    """What a pull would overwrite or lose of the local work not yet sent:
    field edits, conflicts, relations added here (the pull rewrites a unit's
    relations from the room). Empty without a base: nobody can tell."""
    if not found or not found.get("base"):
        return {"edits": [], "conflicts": [], "relations": [], "removals": []}
    return {"edits": list(found.get("local_edits") or []),
            "conflicts": list(found.get("conflicts") or []),
            "relations": list(found.get("local_relations") or []),
            "removals": list(found.get("removed_relations") or [])}


def _geometries(connection_url: str, site: str, graph, *, dry_run: bool) -> Dict[str, Any]:
    """The room's footprints into pyArchInit's GIS layers; a failure here is
    reported, it never undoes the records already written."""
    try:
        from .room_geometry import pull_geometries
        return pull_geometries(connection_url, site, graph, dry_run=dry_run)
    except Exception as e:  # noqa: BLE001
        return {"footprints": 0, "inserted": 0, "updated": 0, "same": 0, "kept_local": [],
                "skipped": [f"{type(e).__name__}: {e}"], "dry_run": dry_run}


def pull_room(connection_url: str, site: str, *, node: str, room: str, token: str,
              workdir: str, apply: bool = False, force: bool = False,
              media: bool = True, found: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The room into the site's native tables. Dry run unless ``apply``.

    With a base (a previous sync), the apply that would overwrite local edits
    not yet sent, conflicts, or relations added here needs ``force``; a
    relation the room REMOVED since the base is simply removed here too.
    Without a base, any local relation the room lacks needs ``force`` (nobody
    can tell «removed there» from «added here»). After the apply, the room
    that was pulled becomes the base."""
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    from . import room_state

    answer, base, how = room_state.room_now(connection_url, site, node=node, room=room, token=token)
    graph, gid, path = room_graph(answer, workdir)
    rows = _rows_by_uuid(connection_url, site)
    plan = GraphIngestor().populate_list(graph, db_path=connection_url, sito=site,
                                         dry_run=True, create_missing_epochs=True)
    kinds = classify(plan, rows, site)
    drops = [r for r in kinds["real"] if r.get("only_local")]
    if base is not None and found is None:
        found = contribution(connection_url, site, node=node, room=room, token=token,
                             workdir=os.path.join(workdir, "compare"))
    unsent = _unsent(found)
    report = {"room": room, "graph_id": gid, "cursor": answer.get("cursor"), "em_json": path,
              "inserted": plan.inserted, "updated": plan.updated, "skipped": plan.skipped,
              "format_only": kinds["format_only"], "real": kinds["real"],
              "errors": list(plan.errors), "applied": False, "read": how,
              "base": base is not None, "unsent": unsent}
    if not apply:
        if media:
            from .room_media import pull_media
            report["media"] = pull_media(connection_url, site, graph, path, node=node,
                                         room=room, token=token, dry_run=True)
        report["geometry"] = _geometries(connection_url, site, graph, dry_run=True)
        return report
    if base is None and drops and not force:
        raise NodeError(
            f"applying the room would remove {sum(len(r['only_local']) for r in drops)} "
            f"relation(s) of {len(drops)} local unit(s) that the room does not have "
            f"(e.g. US {drops[0]['us']}: {drops[0]['only_local'][:3]}); "
            "review them, then apply with force")
    if base is not None and any(unsent.values()) and not force:
        raise NodeError(
            f"pulling would overwrite local work not yet sent: {len(unsent['edits'])} field edit(s), "
            f"{len(unsent['conflicts'])} conflict(s), {len(unsent['relations'])} relation(s) added here, "
            f"{len(unsent['removals'])} relation(s) removed here "
            "— send your changes first, or apply with force")
    new_site = not _site_exists(connection_url, site)
    done = GraphIngestor().populate_list(graph, db_path=connection_url, sito=site,
                                         dry_run=False, create_missing_epochs=True)
    report.update({"inserted": done.inserted, "updated": done.updated, "skipped": done.skipped,
                   "errors": list(done.errors), "applied": True})
    if new_site:
        _site_identity(connection_url, site, graph)
    if media:
        # after the units: the media attach to their id_us
        from modules.s3dgraphy.sync.graph_ingestor import hydrate_row_fields_from_data
        from .room_media import pull_media
        hydrate_row_fields_from_data(graph)
        report["media"] = pull_media(connection_url, site, graph, path, node=node,
                                     room=room, token=token)
    # the footprints into the GIS layers (site, trenches, areas, cuts)
    report["geometry"] = _geometries(connection_url, site, graph, dry_run=False)
    if not done.errors:
        # both sides now agree on this room: it is the base of the next compare;
        # what the pull did not bring here on purpose is remembered as such
        local_now, _ = local_graph(connection_url, site, os.path.join(workdir, "after"))
        here = {n.node_id for n in local_now.nodes} | _map_only(graph)
        not_here = [n.node_id for n in graph.nodes if n.node_id not in here]
        # relations the pull cannot reproduce here either (on PostgreSQL the
        # area → site links come from the GIS layers, which do not travel)
        local_edges = {(e.edge_source, e.edge_type, e.edge_target) for e in local_now.edges}
        not_here += ["|".join(t) for t in
                     ((e.edge_source, e.edge_type, e.edge_target) for e in graph.edges)
                     if t not in local_edges and t[0] in here and t[2] in here]
        room_state.save(connection_url, site, node, room, answer.get("doc") or {},
                        answer.get("cursor"), how="pull", not_here=not_here)
        report["base_saved"] = True
        report["not_here"] = len(not_here)
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


def _without_noise(delta, skip: set, resources: frozenset = frozenset(),
                   absent: frozenset = frozenset()):
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
        if (op.get("op") == "update_field" and op.get("remove")
                and str(op.get("field", ""))[5:] in absent):
            continue      # a column this database does not have (an older schema): not an edit
        keep.append(op)
    delta.ops = keep
    return delta


def _same_number(op, remote) -> bool:
    """``2`` in the room and ``2.0`` here (a PostgreSQL numeric column) are
    the same value: not a field change."""
    if op.get("op") != "update_field" or not str(op.get("field", "")).startswith("data."):
        return False
    node = remote.find_node_by_id(op.get("node_id")) if hasattr(remote, "find_node_by_id") else None
    data = getattr(node, "data", None)
    if not isinstance(data, dict):
        return False
    old, new = data.get(op["field"][5:]), op.get("value")
    if isinstance(old, bool) or isinstance(new, bool):
        return False
    try:
        return float(old) == float(new)
    except (TypeError, ValueError):
        return False


def contribution(connection_url: str, site: str, *, node: str, room: str, token: str,
                 workdir: str) -> Dict[str, Any]:
    """What the local site adds to the room: new nodes, new relations, fields
    that differ (shown, not sent), and what only the room has (others' work,
    never touched)."""
    from s3dgraphy.em.write import _snapshot, diff

    from . import room_state
    answer, base, how = room_state.room_now(connection_url, site, node=node, room=room, token=token)
    remote, gid, _ = room_graph(answer, workdir)
    local, local_path = local_graph(connection_url, site, workdir)
    resources = {n.node_id for n in list(local.nodes) + list(remote.nodes)
                 if getattr(n, "node_type", "") == "resource"}
    # A key this database cannot hold (not one of its us_table columns) and
    # that its export never writes: an older schema, not an edit — PostgreSQL
    # from pyarchinit_schema_updated.sql lacks five legacy columns of SQLite.
    from .room_records import us_columns

    def _keys(graph):
        return {k for n in graph.nodes if isinstance(getattr(n, "data", None), dict)
                for k in n.data}
    absent = frozenset(_keys(remote) - _keys(local) - us_columns(connection_url))
    delta = _without_noise(diff(_snapshot(remote), local), _map_only(local) | _map_only(remote),
                           resources, absent)
    delta.ops = [op for op in delta.ops if not _same_number(op, remote)]
    names = {n.node_id: n.name for n in list(local.nodes) + list(remote.nodes)}
    found = {"room": room, "graph_id": gid, "cursor": answer.get("cursor"),
             "connection_url": connection_url, "site": site,
             "local_em_json": local_path, "read": how, "base": base is not None,
             "base_doc": (base or {}).get("doc"), "base_cursor": (base or {}).get("cursor"),
             "not_here": list((base or {}).get("not_here") or [])}
    from .room_checks import ambiguous_numbers
    found["ambiguous_numbers"] = ambiguous_numbers(connection_url, site)
    if base is None:
        changes = [op for op in delta.ops if op.get("op") == "update_field"]
        room_only = [op for op in delta.ops if op.get("op") in ("remove_node", "remove_edge")]
        delta.ops = []                                    # without a base no field is sent
        found.update({"delta": delta, "send_fields": [],
                      "new_nodes": [names.get(n.get("id"), n.get("id")) for n in delta.nodes],
                      "new_edges": len(delta.edges),
                      "field_changes": [(names.get(op["node_id"], op["node_id"]), op["field"])
                                        for op in changes],
                      "room_only": len(room_only), "local_edits": [], "room_edits": [],
                      "conflicts": [], "removed_in_room": 0, "removed_here": 0,
                      "local_relations": []})
        return found
    base_graph, _bgid, _ = room_graph({"doc": base["doc"]}, workdir, "base.em.json")
    tw = three_way(delta, base_graph, remote, local, frozenset(base.get("not_here") or ()))
    delta.nodes, delta.edges, delta.ops = tw["send_nodes"], tw["send_edges"], tw["send_fields"]
    label = lambda nid: names.get(nid, nid)
    found.update({
        "delta": delta, "send_fields": tw["send_fields"],
        "new_nodes": [label(n.get("id")) for n in tw["send_nodes"]],
        "new_edges": len(tw["send_edges"]),
        "local_edits": [(label(op["node_id"]), op["field"]) for op in tw["send_fields"]],
        "room_edits": [(label(op["node_id"]), op["field"]) for op in tw["room_fields"]],
        "conflicts": [dict(c, name=label(c["node_id"])) for c in tw["conflicts"]],
        "field_changes": [(label(op["node_id"]), op["field"]) for op in tw["room_fields"]],
        "removed_in_room": tw["removed_in_room"], "removed_here": tw["removed_here"],
        "room_only": tw["room_added"],
        "local_relations": [(label(a), k, label(b)) for a, k, b in tw["local_relations"]],
        "send_removals": tw["send_removals"],
        "removed_relations": [(label(r["triple"][0]), r["triple"][1], label(r["triple"][2]))
                              for r in tw["send_removals"]]})
    return found


def _value(nodes: Dict[str, Dict[str, Any]], nid: str, field: str):
    node = nodes.get(nid)
    if node is None:
        return None
    if field.startswith("data."):
        return (node.get("data") or {}).get(field[5:])
    return node.get(field)


def _equal(a, b) -> bool:
    """Same value: empty is empty, 2 is 2.0, otherwise as JSON."""
    if a in (None, "", [], {}) and b in (None, "", [], {}):
        return True
    if not isinstance(a, bool) and not isinstance(b, bool):
        try:
            return float(a) == float(b)
        except (TypeError, ValueError):
            pass
    try:
        return json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)
    except (TypeError, ValueError):
        return a == b


def three_way(delta, base_graph, room, local, not_here: frozenset = frozenset()) -> Dict[str, Any]:
    """Each difference between the room and the local site (``delta``: what
    turns the room into the local site), given its author by the base.
    ``not_here``: what the last pull left in the room on purpose — absent
    here, never removed here."""
    from s3dgraphy.em.write import _snapshot
    b_nodes, b_edges = _snapshot(base_graph)
    r_nodes, r_edges = _snapshot(room)
    l_nodes, _l = _snapshot(local)
    r_triple = {eid: triple for triple, eid in r_edges.items()}
    rows = {nid for nid, p in l_nodes.items() if (p.get("data") or {}).get("node_uuid")}
    out = {"send_nodes": [], "send_edges": [], "send_fields": [], "room_fields": [],
           "conflicts": [], "removed_in_room": 0, "removed_here": 0, "room_added": 0,
           "local_relations": [], "send_removals": []}
    for n in delta.nodes:
        if n.get("id") in b_nodes:
            out["removed_in_room"] += 1        # it was in the base: the room removed it
        else:
            out["send_nodes"].append(n)
    for e in delta.edges:
        triple = (e.get("source"), e.get("edge_type"), e.get("target"))
        if triple in b_edges:
            out["removed_in_room"] += 1
        else:
            out["send_edges"].append(e)
            if triple[0] in rows and triple[2] in rows:
                out["local_relations"].append(triple)
    for op in delta.ops:
        kind = op.get("op")
        if kind == "update_field":
            nid, field = op["node_id"], op["field"]
            here = None if op.get("remove") else op.get("value")
            there, was = _value(r_nodes, nid, field), _value(b_nodes, nid, field)
            if nid not in b_nodes:
                out["room_fields"].append(op)            # no common ancestor: shown, not sent
            elif _equal(there, was) and not _equal(here, was):
                out["send_fields"].append(op)            # changed here only
            elif _equal(here, was):
                out["room_fields"].append(op)            # changed in the room only
            else:
                out["conflicts"].append({"node_id": nid, "field": field, "here": here,
                                         "room": there, "base": was})
        elif kind == "remove_node":
            gone = op.get("id") in b_nodes and op.get("id") not in not_here
            out["removed_here" if gone else "room_added"] += 1
        elif kind == "remove_edge":
            triple = r_triple.get(op.get("id"))
            gone = (triple in b_edges and triple[0] not in not_here
                    and triple[2] not in not_here and "|".join(triple or ()) not in not_here)
            out["removed_here" if gone else "room_added"] += 1
            if gone and triple[0] in rows and triple[2] in rows:
                # a relation between two units removed here: a local edit
                # like any other, sent with the others (a unit deleted here
                # is only reported — removing it from a shared room is not
                # done on its own)
                out["send_removals"].append({"op": "remove_edge", "id": op.get("id"),
                                             "triple": triple})
    return out


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
    fields = []
    for op in found.get("send_fields") or []:      # local edits: only with a base
        f = {"op": "update_field", "node_id": op["node_id"], "field": op["field"]}
        if op.get("remove"):
            f["remove"] = True
        else:
            f["value"] = op.get("value")
        fields.append(f)
    ops += fields
    removals = [{"op": "remove_edge", "id": r["id"]} for r in found.get("send_removals") or []]
    ops += removals
    if not ops:
        return {"applied": 0, "refused": [], "requests": 0, "uploaded": 0, "fields": 0, "removals": 0}
    sent = nodeio.send_ops(node_base(node), token, room, ops, graph_id=found["graph_id"])
    sent["uploaded"] = uploaded
    sent["fields"] = len(fields)
    sent["removals"] = len(removals)
    if found.get("base") and found.get("connection_url") and not sent.get("refused"):
        # the base moves by what was sent — not to the room, which may hold
        # others' changes not yet pulled
        from . import room_state
        room_state.save(found["connection_url"], found["site"], node, room,
                        room_state.advance(found["base_doc"], found["graph_id"], ops),
                        found.get("base_cursor"), how="send", not_here=found.get("not_here"))
        sent["base_saved"] = True
    return sent
