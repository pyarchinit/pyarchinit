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
