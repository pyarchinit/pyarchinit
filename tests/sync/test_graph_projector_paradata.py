"""L1 fixture-based: include_paradata kwarg semantics (D3)."""
from __future__ import annotations
import shutil
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

FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")


@pytest.fixture
def mini_volterra(tmp_path):
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    add_columns(dst); backfill_uuids(dst)
    return dst


def _read_sito(db):
    conn = sqlite3.connect(db)
    s = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    return s


def test_populate_graph_includes_paradata_by_default(mini_volterra):
    """D3: default is include_paradata=True. Add a paradata file
    next to the DB and verify it appears in the graph."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    sito = _read_sito(mini_volterra)
    store = ParadataStore(mini_volterra, sito)
    auth_uuid = store.add_author("Marco Pacifico")

    p = GraphProjector()
    graph = p.populate_graph(mini_volterra, sito=sito)
    types = [type(n).__name__ for n in graph.nodes]
    assert "AuthorNode" in types, (
        f"populate_graph default did not include paradata: {types}")
    # Verify the specific author uuid is present
    assert any(getattr(n, "node_id", "") == auth_uuid
               for n in graph.nodes)


def test_opt_out_disables_merge(mini_volterra):
    """D3 opt-out: include_paradata=False excludes paradata nodes
    even if the file exists."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    sito = _read_sito(mini_volterra)
    ParadataStore(mini_volterra, sito).add_author("Marco")

    graph = GraphProjector().populate_graph(
        mini_volterra, sito=sito, include_paradata=False)
    types = [type(n).__name__ for n in graph.nodes]
    assert "AuthorNode" not in types


def test_populate_graph_no_paradata_file_no_error(mini_volterra):
    """include_paradata=True + no file → returns strat layer (no error)."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    sito = _read_sito(mini_volterra)
    graph = GraphProjector().populate_graph(
        mini_volterra, sito=sito, include_paradata=True)
    # Should still have strat nodes (Volterra fixture)
    assert len(graph.nodes) > 0


def test_populate_graph_corrupt_paradata_falls_back(mini_volterra):
    """If paradata file is corrupt, log warning and return strat layer."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    sito = _read_sito(mini_volterra)
    store = ParadataStore(mini_volterra, sito)
    # Write garbage
    store.file_path.write_text("not valid xml at all")

    # Should NOT raise — falls back to strat-only
    graph = GraphProjector().populate_graph(
        mini_volterra, sito=sito, include_paradata=True)
    types = [type(n).__name__ for n in graph.nodes]
    assert "AuthorNode" not in types
    assert len(graph.nodes) > 0  # strat still present
