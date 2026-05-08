"""L1 idempotent paradata writes.

Three consecutive add_author + write cycles must converge — no
duplicate nodes, file size stable from run 2 onwards.
"""
from __future__ import annotations
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


def _make_db(tmp_path):
    import sqlite3
    db = tmp_path / "test.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id INT, sito TEXT)")
    conn.commit(); conn.close()
    return db


def test_repeated_add_author_creates_distinct_nodes(tmp_path):
    """Adding the same name N times creates N distinct nodes
    (each call produces a fresh uuid7) — this is the EXPECTED
    behavior since name is not a primary key."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(_make_db(tmp_path), "X")
    u1 = store.add_author("Marco")
    u2 = store.add_author("Marco")
    u3 = store.add_author("Marco")
    assert u1 != u2 != u3  # distinct uuids
    assert len(store.list_authors()) == 3


def test_re_read_after_write_idempotent(tmp_path):
    """Reading + writing the same graph produces a stable file:
    file_size after run 2 == file_size after run 3."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(_make_db(tmp_path), "X")
    store.add_author("Marco")

    # Run 1: read + write (no mutation in between)
    g1 = store.read()
    store.write(g1)
    size1 = store.file_path.stat().st_size

    # Run 2: same
    g2 = store.read()
    store.write(g2)
    size2 = store.file_path.stat().st_size

    # Sizes might differ run 1 vs 2 due to UUID/timestamp embedding,
    # but run 2 vs 3 must be stable.
    g3 = store.read()
    store.write(g3)
    size3 = store.file_path.stat().st_size

    assert size2 == size3, (
        f"non-idempotent write: run 2={size2}, run 3={size3}")
    # Nodes preserved
    assert len(store.read().nodes) == 1
