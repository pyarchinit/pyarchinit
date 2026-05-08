"""L0 unit tests for ParadataStore.

Pure pytest, no QGIS, no real DB (uses tmp_path).
Pins decisions D2 (file path), D4 (paradata-only filter),
D5 (low+high level API), D9 (site-level isolation).
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
    """Create a minimal sqlite DB so ParadataStore has a parent dir."""
    db = tmp_path / "test.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id INTEGER, sito TEXT)")
    conn.commit()
    conn.close()
    return db


def test_file_path_resolves_per_sito(tmp_path):
    """D2: file path is `{db_dir}/paradata_{sito_slug}.graphml`."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    db = _make_db(tmp_path)
    store = ParadataStore(db, "Scavo Archeologico")
    assert store.file_path == tmp_path / "paradata_scavo_archeologico.graphml"


def test_file_path_slugifies_special_chars(tmp_path):
    """Slug replaces non-word chars with underscore + lowercases."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    db = _make_db(tmp_path)
    store = ParadataStore(db, "Site #1 — α")
    assert "paradata_site__1" in str(store.file_path).lower()


def test_exists_false_when_no_file(tmp_path):
    """exists() reflects on-disk presence, defaults False on init."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(_make_db(tmp_path), "X")
    assert store.exists() is False


def test_read_empty_when_no_file(tmp_path):
    """read() returns empty Graph when file doesn't exist (NOT error)."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(_make_db(tmp_path), "X")
    graph = store.read()
    assert len(graph.nodes) == 0


def _make_minimal_graph_with_strat_node(sito: str):
    """Build a Graph with one StratigraphicUnit node (NOT paradata)."""
    from s3dgraphy import Graph
    g = Graph(graph_id=sito)
    # Use a generic Node class that's not paradata to test filtering
    from s3dgraphy.nodes.base_node import Node
    n = Node(node_id="not-paradata-uuid", name="US1")
    n.attributes = {"sito": sito}
    g.add_node(n)
    return g


def test_low_level_add_node_paradata_only(tmp_path):
    """add_node refuses non-paradata types (D4)."""
    from modules.s3dgraphy.sync.paradata_store import (
        ParadataStore, ParadataValidationError)
    from s3dgraphy.nodes.base_node import Node
    store = ParadataStore(_make_db(tmp_path), "X")
    with pytest.raises(ParadataValidationError):
        store.add_node(Node(node_id="abc", name="bogus"))


def test_low_level_add_node_persists(tmp_path):
    """add_node writes to file; subsequent read sees the node."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    from s3dgraphy.nodes.author_node import AuthorNode
    store = ParadataStore(_make_db(tmp_path), "X")
    node = AuthorNode(node_id="auth-123", name="Marco")
    store.add_node(node)
    assert store.exists() is True
    graph2 = store.read()
    assert len(graph2.nodes) == 1
    assert graph2.nodes[0].node_id == "auth-123"


def test_low_level_remove_node_idempotent(tmp_path):
    """remove_node on missing uuid is a no-op (no error)."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(_make_db(tmp_path), "X")
    # File doesn't exist yet
    store.remove_node("any-uuid")  # must not raise

    from s3dgraphy.nodes.author_node import AuthorNode
    store.add_node(AuthorNode(node_id="a1", name="Marco"))
    store.remove_node("not-present-uuid")  # idempotent, no raise
    assert len(store.read().nodes) == 1


def test_read_filters_to_paradata_only(tmp_path):
    """If the file accidentally contains non-paradata nodes
    (corrupt input), read() filters them out silently.

    NOTE: the seed file is written directly via lxml (rather than
    GraphMLExporter) because the latter only emits paradata image
    nodes when they sit inside a ParadataNodeGroup attached to a
    stratigraphic unit; an isolated AuthorNode passed to it is
    silently dropped, so the heavy exporter cannot produce the
    "mixed" corrupt input this test needs.
    """
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    from lxml import etree as ET

    store = ParadataStore(_make_db(tmp_path), "X")
    NS = "http://graphml.graphdrawing.org/xmlns"
    NS_Y = "http://www.yworks.com/xml/graphml"
    NSMAP = {None: NS, "y": NS_Y}
    root = ET.Element(f"{{{NS}}}graphml", nsmap=NSMAP)
    # Minimal key set: description + nodegraphics + EMID
    for kid, kfor, yftype, attr_name, attr_type in [
        ("d1", "node", None, "description", "string"),
        ("d2", "node", "nodegraphics", None, None),
        ("d3", "node", None, "EMID", "string"),
    ]:
        kel = ET.SubElement(root, f"{{{NS}}}key")
        kel.set("id", kid); kel.set("for", kfor)
        if yftype: kel.set("yfiles.type", yftype)
        if attr_name: kel.set("attr.name", attr_name)
        if attr_type: kel.set("attr.type", attr_type)
    g_el = ET.SubElement(root, f"{{{NS}}}graph")
    g_el.set("id", "X"); g_el.set("edgedefault", "directed")

    # Paradata: AuthorNode (with the round-trip marker)
    a_el = ET.SubElement(g_el, f"{{{NS}}}node"); a_el.set("id", "auth-1")
    d1 = ET.SubElement(a_el, f"{{{NS}}}data"); d1.set("key", "d1")
    d1.text = "_s3d_node_type:AuthorNode"
    d2 = ET.SubElement(a_el, f"{{{NS}}}data"); d2.set("key", "d2")
    img = ET.SubElement(d2, f"{{{NS_Y}}}ImageNode")
    nl = ET.SubElement(img, f"{{{NS_Y}}}NodeLabel"); nl.text = "Marco"
    d3 = ET.SubElement(a_el, f"{{{NS}}}data"); d3.set("key", "d3")
    d3.text = "auth-1"

    # Non-paradata: a generic <node> with no marker — importer
    # will reconstruct as a plain Node.
    s_el = ET.SubElement(g_el, f"{{{NS}}}node"); s_el.set("id", "strat-1")
    sd1 = ET.SubElement(s_el, f"{{{NS}}}data"); sd1.set("key", "d1")
    sd1.text = "US1"

    ET.ElementTree(root).write(str(store.file_path),
                                encoding="UTF-8", xml_declaration=True)

    parsed = store.read()
    types = {type(n).__name__ for n in parsed.nodes}
    # Paradata-family should survive
    assert "AuthorNode" in types
    # Non-paradata types must NOT survive the filter
    assert "Node" not in types


def test_find_returns_matching_nodes(tmp_path):
    """find(node_type=AuthorNode, name='Marco') returns the right node."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    from s3dgraphy.nodes.author_node import AuthorNode
    store = ParadataStore(_make_db(tmp_path), "X")
    store.add_node(AuthorNode(node_id="a1", name="Marco"))
    store.add_node(AuthorNode(node_id="a2", name="Maria"))
    found = store.find("AuthorNode", name="Marco")
    assert len(found) == 1
    assert found[0].node_id == "a1"
