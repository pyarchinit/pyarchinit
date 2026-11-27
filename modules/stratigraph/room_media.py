"""The media of a pyArchInit site, to a StratiGraph room and back.

What travels is what pyArchInit itself archives: the files of ``media_table``
linked to the units (photos, videos, 3D models, documents). Orthophotos and
other rasters are QGIS layers, not pyArchInit media, and never go through
here.

**To the room.** Each medium linked to a unit becomes a ``resource`` node of
the site's graph — its id is the medium's ``entity_uuid`` (stable across
copies of the database), its ``data.url`` the local file — tied to its unit
by ``has_linked_resource``. s3dgraphy's room import then uploads each file
ONCE (HEAD by sha256) and rewrites ``data.url`` to the room's address,
keeping the local path as a second address.

**From the room.** A resource whose id is already the ``entity_uuid`` of a
local medium is NOT downloaded: only its link to the unit is checked. A new
one is downloaded from the room's store into
``<PYARCHINIT_HOME>/stratigraph_media/<room>/`` — that file becomes the
medium's original, as a file loaded from the form would be — and handed to
pyArchInit's media import (thumbnail, copy, link); the new row then takes
the resource's id as ``entity_uuid``, so the next pull recognises it.

Qt-free.
"""
from __future__ import annotations

import ast
import json
import os
import re
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

#: the medium of a unit (entity_type of media_to_entity_table); the other
#: entity types (finds, pottery, tombs, structures) are not nodes of the site's
#: graph yet, and are counted, not sent
UNIT_ENTITY = "US"


def media_dirs(home: Optional[str] = None) -> Tuple[str, str]:
    """``(thumbnail folder, resize folder)`` from pyArchInit's config.cfg."""
    home = home or os.environ.get("PYARCHINIT_HOME") or os.path.join(os.path.expanduser("~"), "pyarchinit_5")
    try:
        with open(os.path.join(home, "pyarchinit_DB_folder", "config.cfg"), encoding="utf-8") as fh:
            config = ast.literal_eval(fh.read())
    except (OSError, ValueError, SyntaxError):
        config = {}
    return (str(config.get("THUMB_PATH") or os.path.join(home, "pyarchinit_Thumbnails_folder")),
            str(config.get("THUMB_RESIZE") or os.path.join(home, "pyarchinit_Resize_folder")))


def media_file(filepath: Optional[str], path_resize: Optional[str], resize_dir: str) -> Optional[str]:
    """The file of a medium: its original when the path is absolute and there,
    else the copy pyArchInit keeps in the resize folder."""
    for candidate in (filepath,
                      os.path.join(resize_dir, path_resize) if path_resize else None,
                      os.path.join(resize_dir, filepath) if filepath else None):
        if candidate and os.path.isabs(candidate) and os.path.isfile(candidate):
            return candidate
    return None


def _graphs(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    graphs = doc.get("graphs") or {}
    return list(graphs.values()) if isinstance(graphs, dict) else list(graphs)


def add_media_resources(em_json: str, connection_url: str, site: str,
                        resize_dir: Optional[str] = None) -> Dict[str, Any]:
    """Write the site's unit media into the exported em.json, in place:
    one ``resource`` per medium, one ``has_linked_resource`` per link."""
    from sqlalchemy import create_engine, text

    resize_dir = resize_dir or media_dirs()[1]
    from sqlalchemy import inspect
    engine = create_engine(connection_url)
    tables = set(inspect(engine).get_table_names())
    needed = {"media_table", "media_to_entity_table", "media_thumb_table"}
    if not needed <= tables or "entity_uuid" not in {
            c["name"] for c in inspect(engine).get_columns("media_table")}:
        # an old database: the media have no stable identity yet (pyArchInit
        # adds media_table.entity_uuid when it connects) — they wait, the rest goes
        return {"resources": 0, "links": 0, "missing": [], "other_entities": {},
                "skipped": "media_table has no entity_uuid (open the database in pyArchInit once)"}
    with open(em_json, encoding="utf-8") as fh:
        doc = json.load(fh)
    graph = _graphs(doc)[0]
    unit_of = {str((n.get("data") or {}).get("node_uuid") or ""): n["id"]
               for n in graph.get("nodes") or [] if (n.get("data") or {}).get("node_uuid")}
    existing = {n["id"] for n in graph.get("nodes") or []}
    edges = {(e.get("source"), e.get("edge_type"), e.get("target")) for e in graph.get("edges") or []}
    report = {"resources": 0, "links": 0, "missing": [], "other_entities": {}}
    query = text("""
        SELECT m.entity_uuid, m.filename, m.filetype, m.mediatype, m.filepath,
               m.descrizione, m.tags, t.path_resize, u.node_uuid
        FROM media_to_entity_table e
        JOIN media_table m ON m.id_media = e.id_media
        LEFT JOIN media_thumb_table t ON t.id_media = m.id_media
        JOIN us_table u ON u.id_us = e.id_entity
        WHERE e.entity_type = :ut AND u.sito = :site""")
    with create_engine(connection_url).connect() as conn:
        rows = conn.execute(query, {"ut": UNIT_ENTITY, "site": site}).fetchall()
        for et, n in conn.execute(text(
                "SELECT entity_type, COUNT(*) FROM media_to_entity_table "
                "WHERE entity_type <> :ut GROUP BY entity_type"), {"ut": UNIT_ENTITY}):
            report["other_entities"][str(et)] = int(n)
    for (uuid_, filename, filetype, mediatype, filepath, descr, tags, resize, unit_uuid) in rows:
        unit = unit_of.get(str(unit_uuid or ""))
        if not uuid_ or not unit:
            continue
        path = media_file(filepath, resize, resize_dir)
        if path is None:
            report["missing"].append(str(filepath or filename))
            continue
        if uuid_ not in existing:
            graph.setdefault("nodes", []).append({
                "id": uuid_, "node_type": "resource",
                "name": f"{filename}.{filetype}" if filetype else str(filename),
                "description": str(descr or ""),
                "data": {"url": path, "pyarchinit_media": {
                    "mediatype": mediatype, "filename": filename, "filetype": filetype,
                    "tags": tags}}})
            existing.add(uuid_)
            report["resources"] += 1
        key = (unit, "has_linked_resource", uuid_)
        if key not in edges:
            graph.setdefault("edges", []).append({
                "id": f"{unit}__has_linked_resource__{uuid_}", "source": unit,
                "target": uuid_, "edge_type": "has_linked_resource"})
            edges.add(key)
            report["links"] += 1
    with open(em_json, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False)
    return report


# ── from the room ────────────────────────────────────────────────────────────

def _link(conn, engine, id_us, id_media, filepath, name) -> None:
    """One media_to_entity_table row with an explicit id, as pyArchInit's own
    media import writes it: on PostgreSQL the serial sequence lags behind
    explicit ids, so leaning on it collided (``id_mediaToEntity`` = 1)."""
    from sqlalchemy import MetaData
    from modules.utility.qfield_importer import next_id, reflected
    table = reflected(MetaData(), engine, "media_to_entity_table")
    conn.execute(table.insert().values(**{
        "id_mediaToEntity": next_id(conn, table, "id_mediaToEntity"),
        "id_entity": id_us, "entity_type": UNIT_ENTITY, "table_name": "us_table",
        "id_media": id_media, "filepath": filepath, "media_name": name}))


def _resync_sequences(engine) -> None:
    """PostgreSQL only: each media table's serial back to MAX(id), so the
    next record saved from the form does not collide with the pulled ones."""
    if engine.dialect.name != "postgresql":
        return
    from sqlalchemy import text
    for table, pk in (("media_table", "id_media"), ("media_thumb_table", "id_media_thumb"),
                      ("media_to_entity_table", "id_mediaToEntity")):
        try:
            with engine.begin() as conn:
                conn.execute(text(
                    f"SELECT setval(pg_get_serial_sequence('{table}', '{pk}'), "
                    f"GREATEST((SELECT COALESCE(MAX(\"{pk}\"), 0) FROM {table}), 1))"))
        except Exception:                                   # no sequence: nothing to align
            pass


def _safe(name: str) -> str:
    return re.sub(r"[^\w.\-]+", "_", name).strip("._") or "media"


def download(url: str, token: str, target: str) -> str:
    """Fetch a room asset into ``target`` (written beside, then moved)."""
    from s3dgraphy.room_import.trust import urlopen
    os.makedirs(os.path.dirname(target), exist_ok=True)
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    partial = target + ".part"
    with urlopen(request, timeout=600) as answer, open(partial, "wb") as out:
        while True:
            piece = answer.read(1 << 20)
            if not piece:
                break
            out.write(piece)
    os.replace(partial, target)
    return target


def pull_media(connection_url: str, site: str, graph: Any, em_json: str, *, node: str,
               room: str, token: str, home: Optional[str] = None,
               dry_run: bool = False) -> Dict[str, Any]:
    """The room's unit media into pyArchInit: known media relinked, new ones
    downloaded and imported. Call AFTER the units are in (``pull_room``)."""
    from sqlalchemy import create_engine, text

    from modules.s3dgraphy.sync.em_media_import import import_emjson_media
    from .node_client import node_base
    from .room_plans import is_plan

    home = home or os.environ.get("PYARCHINIT_HOME") or os.path.join(os.path.expanduser("~"), "pyarchinit_5")
    thumb_dir, resize_dir = media_dirs(home)
    cache = os.path.join(home, "stratigraph_media", _safe(room))
    base = node_base(node)
    engine = create_engine(connection_url)
    nodes = {str(n.node_id): n for n in getattr(graph, "nodes", None) or []}
    links = [(str(e.edge_source), str(e.edge_target)) for e in getattr(graph, "edges", None) or []
             if e.edge_type == "has_linked_resource"
             and getattr(nodes.get(str(e.edge_target)), "node_type", "") == "resource"
             and not is_plan(nodes.get(str(e.edge_target)))]      # a plan is not a medium
    from sqlalchemy import inspect as _inspect
    if "entity_uuid" not in {c["name"] for c in _inspect(engine).get_columns("media_table")}:
        return {"known": 0, "relinked": 0, "downloaded": 0, "imported": 0, "not_on_node": 0,
                "no_unit": 0, "dry_run": dry_run, "new": 0,
                "skipped": "media_table has no entity_uuid (open the database in pyArchInit once)"}
    report = {"known": 0, "relinked": 0, "downloaded": 0, "imported": 0, "not_on_node": 0,
              "no_unit": 0,
              "dry_run": dry_run}
    with engine.begin() as conn:
        known = {str(u): i for u, i in conn.execute(text(
            "SELECT entity_uuid, id_media FROM media_table WHERE entity_uuid IS NOT NULL"))}
        unit_row = {str(u): i for u, i in conn.execute(text(
            "SELECT node_uuid, id_us FROM us_table WHERE sito = :s AND node_uuid IS NOT NULL"),
            {"s": site})}
        fresh = set()
        for unit, res in links:
            unit_node = nodes.get(unit)
            data = getattr(unit_node, "data", None) or {}
            id_us = unit_row.get(str(data.get("node_uuid") or unit))
            if res in known:
                report["known"] += 1
                if id_us is None:
                    continue
                linked = conn.execute(text(
                    "SELECT 1 FROM media_to_entity_table WHERE id_entity = :e "
                    "AND entity_type = :t AND id_media = :m"),
                    {"e": id_us, "t": UNIT_ENTITY, "m": known[res]}).fetchone()
                if not linked and not dry_run:
                    m = conn.execute(text("SELECT filepath, filename FROM media_table "
                                          "WHERE id_media = :m"), {"m": known[res]}).fetchone()
                    _link(conn, engine, id_us, known[res], m[0], m[1])
                    report["relinked"] += 1
                continue
            if id_us is None and not dry_run:
                report["no_unit"] += 1     # its unit is not here (a generated CON, say)
                continue
            # a dry run into a database still without the site counts the
            # media of units the pull is about to insert
            fresh.add(res)
    # the new ones: from the room's store to the room's media folder
    downloaded: Dict[str, str] = {}
    for res in sorted(fresh):
        rnode = nodes[res]
        data = rnode.data if isinstance(getattr(rnode, "data", None), dict) else {}
        url = str(data.get("url") or "")
        if not url.startswith(base + "/"):
            report["not_on_node"] += 1
            continue
        target = os.path.join(cache, f"{res[:8]}_{_safe(str(rnode.name or res))}")
        if not dry_run:
            if not os.path.isfile(target):
                download(url, token, target)
                report["downloaded"] += 1
            data["url"] = target                  # the import reads the local file
            data.pop("addresses", None)
        downloaded[res] = target
    if dry_run or not downloaded:
        report["new"] = len(downloaded)
        if not dry_run:
            _resync_sequences(engine)
        return report
    # Only what was just downloaded goes to the import. Every other resource
    # loses its addresses in this in-memory graph: a known medium still
    # carries the sender's local path as a second address, and on a computer
    # where that path exists the import registered it AGAIN under that path
    # (measured: 150 duplicates on the second pull).
    for nid, rnode in nodes.items():
        if getattr(rnode, "node_type", "") == "resource" and nid not in downloaded:
            data = rnode.data if isinstance(getattr(rnode, "data", None), dict) else None
            if data is not None:
                data["url"] = None
                data.pop("addresses", None)
            if hasattr(rnode, "url"):
                rnode.url = None
    result = import_emjson_media(connection_url, graph, site, em_json,
                                 search_dirs=[cache], thumb_path=thumb_dir,
                                 thumb_resize=resize_dir)
    report["imported"] = int(getattr(result, "inserted", 0) or 0)
    want: Dict[str, set] = {}
    for unit, res in links:
        data = getattr(nodes.get(unit), "data", None) or {}
        id_us = unit_row.get(str(data.get("node_uuid") or unit))
        if id_us is not None:
            want.setdefault(res, set()).add(id_us)
    with engine.begin() as conn:
        for res, target in downloaded.items():
            # its identity, so the next pull recognises it, and its own name,
            # description and tags, as the sender's pyArchInit had them
            rnode = nodes[res]
            rdata = rnode.data if isinstance(getattr(rnode, "data", None), dict) else {}
            meta = rdata.get("pyarchinit_media") or {}
            description = str(getattr(rnode, "description", "") or rdata.get("description") or "")
            conn.execute(text(
                "UPDATE media_table SET entity_uuid = :u, "
                "filename = COALESCE(:f, filename), descrizione = COALESCE(:d, descrizione), "
                "tags = COALESCE(:t, tags) WHERE filepath = :p"),
                {"u": res, "p": target, "f": meta.get("filename") or None,
                 "d": description or None, "t": meta.get("tags") or None})
            # Its links are the sender's, exactly: the import sends a
            # property's files to the unit owning it (EMStudio's rule), but a
            # pyArchInit property is a record of its own and keeps its media.
            row = conn.execute(text("SELECT id_media, filepath, filename FROM media_table "
                                    "WHERE entity_uuid = :u"), {"u": res}).fetchone()
            if row is None:
                continue
            id_media, fpath, fname = row
            have = {e for (e,) in conn.execute(text(
                "SELECT id_entity FROM media_to_entity_table WHERE id_media = :m "
                "AND entity_type = :t"), {"m": id_media, "t": UNIT_ENTITY})}
            desired = want.get(res, set())
            for extra in have - desired:
                conn.execute(text("DELETE FROM media_to_entity_table WHERE id_media = :m "
                                  "AND entity_type = :t AND id_entity = :e"),
                             {"m": id_media, "t": UNIT_ENTITY, "e": extra})
            for missing in desired - have:
                _link(conn, engine, missing, id_media, fpath, fname)
    _resync_sequences(engine)
    return report
