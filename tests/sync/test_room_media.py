"""room_media without a node: what goes into the em.json, and what the
contribution does not mistake for an edit.

Measured on the dev-stack (26 Nov 2026): the site's 150 unit photos went to a
room, were rebuilt on another computer with identical (photo, unit) links, a
second pull changed nothing, and a photo added at home reached the other
computer with its description and tags.
"""
from __future__ import annotations

import json
import sqlite3

from modules.stratigraph import room_media as RM
from modules.stratigraph import room_sync as RS


def _db(path, photo):
    con = sqlite3.connect(path)
    con.executescript("""
        CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, sito TEXT, us TEXT, node_uuid TEXT);
        CREATE TABLE media_table (id_media INTEGER PRIMARY KEY, mediatype TEXT, filename TEXT,
            filetype TEXT, filepath TEXT, descrizione TEXT, tags TEXT, entity_uuid TEXT);
        CREATE TABLE media_thumb_table (id_media_thumb INTEGER PRIMARY KEY, id_media INTEGER,
            path_resize TEXT);
        CREATE TABLE media_to_entity_table (id_mediaToEntity INTEGER PRIMARY KEY, id_entity INTEGER,
            entity_type TEXT, table_name TEXT, id_media INTEGER, filepath TEXT, media_name TEXT);""")
    con.execute("INSERT INTO us_table VALUES (1, 'S', '5', 'u5')")
    con.execute("INSERT INTO media_table VALUES (10, 'image', 'US_5_1', 'png', ?, 'Sezione', 't', 'm10')",
                (str(photo),))
    con.execute("INSERT INTO media_table VALUES (11, 'image', 'gone', 'png', '/nowhere/gone.png', '', '', 'm11')")
    con.execute("INSERT INTO media_to_entity_table VALUES (1, 1, 'US', 'us_table', 10, '', '')")
    con.execute("INSERT INTO media_to_entity_table VALUES (2, 1, 'US', 'us_table', 11, '', '')")
    con.execute("INSERT INTO media_to_entity_table VALUES (3, 7, 'REPERTO', 'inventario_materiali_table', 10, '', '')")
    con.commit()
    con.close()


def test_unit_media_become_resources_linked_to_their_unit(tmp_path):
    photo = tmp_path / "US_5_1.png"
    photo.write_bytes(b"png")
    _db(tmp_path / "db.sqlite", photo)
    em = tmp_path / "site.em.json"
    em.write_text(json.dumps({"graphs": {"g": {"nodes": [{"id": "u5", "data": {"node_uuid": "u5"}}],
                                               "edges": []}}}))
    report = RM.add_media_resources(str(em), f"sqlite:///{tmp_path / 'db.sqlite'}", "S",
                                    resize_dir=str(tmp_path))
    assert report["resources"] == 1 and report["links"] == 1
    assert report["missing"] == ["/nowhere/gone.png"]
    assert report["other_entities"] == {"REPERTO": 1}        # counted, not sent
    graph = json.loads(em.read_text())["graphs"]["g"]
    res = [n for n in graph["nodes"] if n["id"] == "m10"][0]  # id = entity_uuid
    assert res["node_type"] == "resource" and res["data"]["url"] == str(photo)
    assert graph["edges"] == [{"id": "u5__has_linked_resource__m10", "source": "u5",
                               "target": "m10", "edge_type": "has_linked_resource"}]
    # idempotent: a second pass adds nothing
    again = RM.add_media_resources(str(em), f"sqlite:///{tmp_path / 'db.sqlite'}", "S",
                                   resize_dir=str(tmp_path))
    assert again["resources"] == 0 and again["links"] == 0


def test_the_resize_copy_stands_in_for_a_missing_original(tmp_path):
    copy = tmp_path / "10_US_5_1.png"
    copy.write_bytes(b"png")
    assert RM.media_file("204_US_1_1.png", "10_US_5_1.png", str(tmp_path)) == str(copy)
    assert RM.media_file("/nowhere/x.png", None, str(tmp_path)) is None


def test_where_a_file_lives_is_not_an_edit():
    from s3dgraphy.contract import Delta
    delta = Delta(nodes=[], edges=[])
    delta.update_field("m10", "data.url", "/local/US_5_1.png")       # room store vs local path
    delta.update_field("m10", "data.addresses", [])
    delta.update_field("u5", "description", "Rivista")
    out = RS._without_noise(delta, set(), frozenset({"m10"}))
    assert out.ops == [{"op": "update_field", "node_id": "u5", "field": "description", "value": "Rivista"}]


def test_an_old_database_without_media_identity_sends_its_units_anyway(tmp_path):
    """Measured on an old database (Pesaro): media_table without entity_uuid
    stopped the whole compare. Now the media wait and the rest goes."""
    db = tmp_path / "old.sqlite"
    con = sqlite3.connect(db)
    con.executescript("""
        CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, sito TEXT, us TEXT, node_uuid TEXT);
        CREATE TABLE media_table (id_media INTEGER PRIMARY KEY, filename TEXT, filepath TEXT);
        CREATE TABLE media_thumb_table (id_media_thumb INTEGER PRIMARY KEY, id_media INTEGER);
        CREATE TABLE media_to_entity_table (id_mediaToEntity INTEGER PRIMARY KEY, id_entity INTEGER);""")
    con.close()
    em = tmp_path / "s.em.json"
    em.write_text(json.dumps({"graphs": {"g": {"nodes": [], "edges": []}}}))
    out = RM.add_media_resources(str(em), f"sqlite:///{db}", "S", resize_dir=str(tmp_path))
    assert out["resources"] == 0 and "entity_uuid" in out["skipped"]


def test_a_remembered_resource_gets_the_file_on_this_disk(tmp_path):
    """An em.json imported from EMStudio is remembered with its resources;
    their addresses are relative to THAT file's folder. Sent from elsewhere
    they resolved to nothing and the room got 0 files (TempluMare, 27 Nov
    2026): the local file becomes the address, the old one the second."""
    import json, sqlite3
    from modules.stratigraph.room_media import add_media_resources
    photo = tmp_path / "f.jpg"; photo.write_bytes(b"x")
    db = tmp_path / "d.sqlite"
    c = sqlite3.connect(db)
    c.executescript("""
      CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, sito TEXT, us TEXT, node_uuid TEXT);
      CREATE TABLE media_table (id_media INTEGER PRIMARY KEY, entity_uuid TEXT, filename TEXT, filetype TEXT,
        mediatype TEXT, filepath TEXT, descrizione TEXT, tags TEXT);
      CREATE TABLE media_thumb_table (id_media_thumb INTEGER PRIMARY KEY, id_media INTEGER, path_resize TEXT);
      CREATE TABLE media_to_entity_table (id_mediaToEntity INTEGER PRIMARY KEY, id_entity INTEGER,
        entity_type TEXT, id_media INTEGER);
    """)
    c.execute("INSERT INTO us_table VALUES (1, 'S', '1', 'u1')")
    c.execute("INSERT INTO media_table VALUES (1, 'r1', 'f', 'jpg', 'image', ?, '', '')", (str(photo),))
    c.execute("INSERT INTO media_to_entity_table VALUES (1, 1, 'US', 1)")
    c.commit(); c.close()
    em = tmp_path / "s.em.json"
    em.write_text(json.dumps({"graphs": {"g": {"nodes": [
        {"id": "u1", "node_type": "US", "name": "1.US1", "data": {}},
        {"id": "r1", "node_type": "resource", "name": "f.jpg", "data": {"url": "DosCo/f.jpg"}}],
        "edges": [{"id": "e", "source": "u1", "target": "r1", "edge_type": "has_linked_resource"}]}}}))
    report = add_media_resources(str(em), f"sqlite:///{db}", "S", resize_dir=str(tmp_path))
    node = next(n for n in json.loads(em.read_text())["graphs"]["g"]["nodes"] if n["id"] == "r1")
    assert report["readdressed"] == 1 and node["data"]["url"] == str(photo)
    assert {"locator": "DosCo/f.jpg"} in node["data"]["addresses"]
