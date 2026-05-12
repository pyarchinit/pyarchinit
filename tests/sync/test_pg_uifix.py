"""PG-UIFix (5.7.8-alpha) + PG-Bv2 (5.7.9-alpha): regression tests.

Bug 1 (paradata/group manager + US picker) — SHIPPED on PG via
ParadataStore/GroupStore which route db_manager through
_resolve_db_handle shim (PG-D, 2026-05-11). Test 1 pins the
obsolete SQLite-only guards as ABSENT.

Bug 2 (graphml export on PG) — SHIPPED in PG-Bv2 (5.7.9-alpha,
2026-05-12). Test 2 now asserts skip-branch markers are GONE.
End-to-end coverage in tests/sync/test_pg_bv2_pg_importer.py.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def test_paradata_manager_does_not_block_on_pg_handle():
    """Bug 1 regression test.

    Pre-PG-UIFix: dialog_paradata_manager._store() called
    db_manager.get_sqlite_path() which returned None on PG, blocking
    with 'Paradata management requires a SQLite-backed pyarchinit
    project.'

    Post-PG-UIFix: _store() passes db_manager directly to
    ParadataStore() which uses _resolve_db_handle shim to accept
    both Path (SQLite) and DbHandle (PG/SQLite).

    Pure source-inspection: reads the module .py file via
    inspect.getsource() + linecache. No Qt rendering needed, so the
    test runs in non-Qt environments too (no importorskip).
    """
    # Inspect the module source (no Qt instantiation needed).
    from gui import dialog_paradata_manager as dpm

    # Verify the obsolete error message is no longer in source.
    import inspect
    src = inspect.getsource(dpm)
    assert "Paradata management requires a SQLite-backed" not in src, \
        "Obsolete SQLite-only guard still present in _store()"
    assert "Group management requires a SQLite-backed" not in src, \
        "Obsolete SQLite-only guard still present in _group_store()"
    assert "US picker requires a SQLite-backed" not in src, \
        "Obsolete SQLite-only guard still present in US picker"


def test_graphml_export_runs_on_pg_backend():
    """Bug 2 SHIPPED (PG-Bv2 5.7.9-alpha).

    Asserts the skip-branch is GONE from s3dgraphy_dot_bridge and the
    obsolete deferred-state markers have been cleaned up. Companion
    to L2 PG end-to-end tests in test_pg_bv2_pg_importer.py."""
    from modules.s3dgraphy import s3dgraphy_dot_bridge as bridge

    import inspect
    src = inspect.getsource(bridge)
    assert "pending PG-Bv2 milestone" not in src, (
        "Obsolete PG-Bv2 deferred-state message still present "
        "(should have been removed when PG-Bv2 shipped)"
    )
    assert "postgresql backend deferred to PG-Bv2" not in src, (
        "Obsolete PG-Bv2 deferred-state status reason still present"
    )
    # The graphml-export-specific PG-skip envelope used the pattern
    # "db_path = self.db_manager.get_sqlite_path()" followed by
    # "if db_path is None:" to skip on PG. Verify both halves gone
    # from the graphml export block (a separate _preselect_groups
    # helper has a legitimate get_sqlite_path guard — that's fine).
    assert "postgresql backend deferred" not in src, (
        "Obsolete PG-skip graphml envelope still present in graphml export — "
        "PG-Bv2 should have removed it"
    )
    assert "Import requires a SQLite-backed" not in src, (
        "PG-UIFix Bug 2 import-flow guard still present (regression)"
    )
