# tests/sync/test_group_store_pg.py
"""PG-D: L2 PostgreSQL tests for GroupStore on the new workspace dir.

Verifies that GroupStore.file_path resolves to
~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/groups_<sito>.graphml
on PG, that write+read round-trip works, that _conn_slug is
deterministic, and that GroupStore shares the workspace dir with
ParadataStore (DRY check on _resolve_workspace_dir).

Skipped cleanly when PG is unreachable at localhost:5433 or when
psycopg2 is not installed.
"""
from __future__ import annotations

from pathlib import Path

import pytest

# Import pg_engine fixture explicitly - conftest_pg.py is not auto-discovered
from tests.sync.conftest_pg import pg_engine  # noqa: F401


def test_group_store_workspace_dir_on_pg(pg_engine, monkeypatch, tmp_path):
    """GroupStore.file_path on PG resolves to
    <home>/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/groups_<sito>.graphml."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    from s3dgraphy.sync._db_handle import DbHandle
    from s3dgraphy.sync.group_store import GroupStore

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    store = GroupStore(db_path=handle, sito="TestSite")
    fp = store.file_path

    assert tmp_path in fp.parents
    assert "pyarchinit_DB_folder" in str(fp)
    assert fp.name == "groups_testsite.graphml"
    assert fp.parent.name == "TestSite"
    assert fp.parent.exists()
    assert fp.parent.is_dir()


def test_group_store_write_read_roundtrip_on_pg(
        pg_engine, monkeypatch, tmp_path):
    """Construct GroupStore on PG, add an ad-hoc group, read it back."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    from s3dgraphy.sync._db_handle import DbHandle
    from s3dgraphy.sync.group_store import GroupStore

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    store = GroupStore(db_path=handle, sito="TestSite")
    assert not store.exists()

    # add_group writes the file
    store.add_group(
        group_uuid="test-group-uuid-1",
        name="TestGroup",
        description="A test group",
        member_us_uuids=[],
    )
    assert store.exists()

    groups = store.list_groups()
    assert len(groups) == 1, f"expected 1 group, got {len(groups)}"
    assert groups[0].get("name") == "TestGroup"


def test_group_store_conn_slug_deterministic_on_pg(pg_engine):
    """Two GroupStore instances with the same handle produce the same
    file_path."""
    from s3dgraphy.sync._db_handle import DbHandle
    from s3dgraphy.sync.group_store import GroupStore

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    store1 = GroupStore(db_path=handle, sito="DeterministicSite")
    store2 = GroupStore(db_path=handle, sito="DeterministicSite")
    assert store1.file_path == store2.file_path


def test_group_store_uses_same_workspace_as_paradata_on_pg(
        pg_engine, monkeypatch, tmp_path):
    """ParadataStore + GroupStore with the same (handle, sito) produce
    file_paths in the SAME <conn_slug>/<sito>/ dir. Verifies DRY of
    _resolve_workspace_dir."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    from s3dgraphy.sync._db_handle import DbHandle
    from s3dgraphy.sync.paradata_store import ParadataStore
    from s3dgraphy.sync.group_store import GroupStore

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    pstore = ParadataStore(db_path=handle, sito="SharedSite")
    gstore = GroupStore(db_path=handle, sito="SharedSite")

    # Same parent dir (the <conn_slug>/<sito>/ subdir)
    assert pstore.file_path.parent == gstore.file_path.parent
    # Different filenames (paradata vs groups)
    assert pstore.file_path.name != gstore.file_path.name
    assert "paradata_" in pstore.file_path.name
    assert "groups_" in gstore.file_path.name
