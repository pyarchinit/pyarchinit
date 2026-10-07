# tests/sync/test_paradata_store_pg.py
"""PG-D: L2 PostgreSQL tests for ParadataStore on the new workspace dir.

Verifies that ParadataStore.file_path resolves to
~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/paradata_<sito>.graphml
on PG, that write+read round-trip works, that _conn_slug is
deterministic, and that multiple sites are isolated.

Skipped cleanly when PG is unreachable at localhost:5433 or when
psycopg2 is not installed.
"""
from __future__ import annotations

from pathlib import Path

import pytest

# Import pg_engine fixture explicitly - conftest_pg.py is not auto-discovered
from tests.sync.conftest_pg import pg_engine  # noqa: F401


def test_paradata_store_workspace_dir_on_pg(pg_engine, monkeypatch, tmp_path):
    """ParadataStore.file_path on PG resolves to
    <home>/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/paradata_<sito>.graphml.

    Use monkeypatch on Path.home to redirect to tmp_path so the test
    doesn't pollute the real user home dir.
    """
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    from s3dgraphy.sync._db_handle import DbHandle
    from s3dgraphy.sync.paradata_store import ParadataStore

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    store = ParadataStore(db_path=handle, sito="TestSite")
    fp = store.file_path

    # The path lives under tmp_path/pyarchinit/pyarchinit_DB_folder/
    assert tmp_path in fp.parents
    assert "pyarchinit" in str(fp)
    assert "pyarchinit_DB_folder" in str(fp)
    assert fp.name == "paradata_testsite.graphml"
    # Parent dir is the sito subdir under conn_slug
    assert fp.parent.name == "TestSite"
    assert fp.parent.parent.parent.name == "pyarchinit_DB_folder"
    # Workspace dir was created by mkdir(parents=True, exist_ok=True)
    assert fp.parent.exists()
    assert fp.parent.is_dir()


def test_paradata_store_write_read_roundtrip_on_pg(
        pg_engine, monkeypatch, tmp_path):
    """Construct ParadataStore on PG, write a paradata graph, read it
    back. End-to-end I/O on the new workspace dir."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    from s3dgraphy.sync._db_handle import DbHandle
    from s3dgraphy.sync.paradata_store import ParadataStore

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    store = ParadataStore(db_path=handle, sito="TestSite")
    assert not store.exists()

    # add_author writes the paradata file
    store.add_author("Test Author", role="creator")
    assert store.exists()

    # Read back
    graph = store.read()
    author_nodes = [
        n for n in graph.nodes
        if type(n).__name__ == "AuthorNode"
    ]
    assert len(author_nodes) == 1, (
        f"expected 1 author, got {len(author_nodes)}"
    )
    assert getattr(author_nodes[0], "name", None) == "Test Author"


def test_paradata_store_conn_slug_deterministic_on_pg(pg_engine):
    """Two ParadataStore instances with the same handle produce the
    same file_path. _conn_slug is deterministic."""
    from s3dgraphy.sync._db_handle import DbHandle
    from s3dgraphy.sync.paradata_store import ParadataStore

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    store1 = ParadataStore(db_path=handle, sito="DeterministicSite")
    store2 = ParadataStore(db_path=handle, sito="DeterministicSite")
    assert store1.file_path == store2.file_path


def test_paradata_store_multiple_sites_isolated_on_pg(
        pg_engine, monkeypatch, tmp_path):
    """Two different sites on the same PG produce file_paths in
    different sito subdirs (isolation under the same conn_slug)."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    from s3dgraphy.sync._db_handle import DbHandle
    from s3dgraphy.sync.paradata_store import ParadataStore

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    store_a = ParadataStore(db_path=handle, sito="SiteAlpha")
    store_b = ParadataStore(db_path=handle, sito="SiteBeta")

    # Same conn_slug parent
    assert store_a.file_path.parent.parent == store_b.file_path.parent.parent
    # Different sito subdirs
    assert store_a.file_path.parent != store_b.file_path.parent
    assert store_a.file_path.parent.name == "SiteAlpha"
    assert store_b.file_path.parent.name == "SiteBeta"
