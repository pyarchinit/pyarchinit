"""L0 unit tests for GroupStore.

Pure pytest, no QGIS, no real DB (uses tmp_path). Pins decisions
D6 (ad-hoc store CRUD) and D7 (file path slug).
"""
from __future__ import annotations
import os
import sqlite3
import sys
from pathlib import Path

import pytest
import pandas  # noqa: F401
from lxml import etree as _e  # noqa: F401
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]


def _make_db(tmp_path) -> Path:
    """Create a minimal sqlite DB so GroupStore has a parent dir."""
    db = tmp_path / "test.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id INTEGER, sito TEXT)")
    conn.commit()
    conn.close()
    return db


def test_file_path_resolves_per_sito(tmp_path):
    """D6/D7: file path is `{db_dir}/groups_{sito_slug}.graphml`."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    db = _make_db(tmp_path)
    store = GroupStore(db, "Scavo Archeologico")
    assert store.file_path == tmp_path / "groups_scavo_archeologico.graphml"


def test_file_path_slugifies_special_chars(tmp_path):
    """Slug replaces non-word chars with underscore + lowercases."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    db = _make_db(tmp_path)
    store = GroupStore(db, "Site #1 — α")
    assert "groups_site__1" in str(store.file_path).lower()


def test_exists_false_when_no_file(tmp_path):
    """exists() reflects on-disk presence, defaults False on init."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    store = GroupStore(_make_db(tmp_path), "X")
    assert store.exists() is False


def test_read_empty_when_no_file(tmp_path):
    """read() returns empty Graph when file doesn't exist (NOT error)."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    store = GroupStore(_make_db(tmp_path), "X")
    graph = store.read()
    assert len(graph.nodes) == 0


def test_low_level_add_node_persists(tmp_path):
    """add_node writes to file; subsequent read sees the node."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    from s3dgraphy.nodes.group_node import ActivityNodeGroup
    store = GroupStore(_make_db(tmp_path), "X")
    node = ActivityNodeGroup(node_id="grp-1", name="basilica")
    node.attributes = {"group_kind": "struttura", "sito": "X"}
    store.add_node(node)
    assert store.exists() is True
    g = store.read()
    assert len(g.nodes) == 1
    assert g.nodes[0].node_id == "grp-1"


def test_remove_node_idempotent(tmp_path):
    """remove_node on missing uuid is a no-op (no error)."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    from s3dgraphy.nodes.group_node import ActivityNodeGroup
    store = GroupStore(_make_db(tmp_path), "X")
    store.remove_node("any-uuid")  # must not raise
    n = ActivityNodeGroup(node_id="g1", name="basilica")
    n.attributes = {"group_kind": "struttura"}
    store.add_node(n)
    store.remove_node("not-present")  # idempotent
    assert len(store.read().nodes) == 1


def test_find_returns_matching_groups(tmp_path):
    """find(group_kind='adhoc', name='X') returns the right group."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    from s3dgraphy.nodes.group_node import ActivityNodeGroup
    store = GroupStore(_make_db(tmp_path), "X")
    for nid, kind, name in [("a", "adhoc", "Marco"),
                             ("b", "adhoc", "Maria"),
                             ("c", "struttura", "basilica")]:
        n = ActivityNodeGroup(node_id=nid, name=name)
        n.attributes = {"group_kind": kind}
        store.add_node(n)
    found = store.find(group_kind="adhoc")
    assert {n.node_id for n in found} == {"a", "b"}


def test_add_group_round_trip(tmp_path):
    """High-level add_group + list_groups round-trip (AC-1)."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    store = GroupStore(_make_db(tmp_path), "X")
    uuid = store.add_group("restauri-2023", group_kind="adhoc",
                            member_us_uuids=["u1", "u2", "u3"])
    assert isinstance(uuid, str) and len(uuid) > 8
    groups = store.list_groups()
    assert len(groups) == 1
    g = groups[0]
    assert g["name"] == "restauri-2023"
    assert g["group_kind"] == "adhoc"
    assert g["member_us_uuids"] == ["u1", "u2", "u3"]
    assert g["group_uuid"] == uuid


def test_remove_group(tmp_path):
    """remove_group deletes the group; list reflects."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    store = GroupStore(_make_db(tmp_path), "X")
    uuid = store.add_group("test", member_us_uuids=["u1"])
    assert len(store.list_groups()) == 1
    store.remove_group(uuid)
    assert len(store.list_groups()) == 0
