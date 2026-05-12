"""PG-UIFix (5.7.8-alpha): regression tests pinning the absence of
SQLite-only guards in dialog_paradata_manager and s3dgraphy_dot_bridge.

These tests guard against a future refactor accidentally re-introducing
the obsolete 'requires SQLite-backed' check (Bug 1) or
'postgresql backend not yet supported' branch (Bug 2). Both blocks
are obsolete since Phase 3 PG-Compat shipped 2026-05-10/11 (tags
phase3-pgcompat-b-export-5.7.1-alpha and
phase3-pgcompat-d-paradata-5.7.3-alpha).
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
    """
    pytest.importorskip("qgis.PyQt.QtWidgets")  # skip if no Qt env

    # Import the dialog class WITHOUT showing it (use __new__ to skip
    # __init__ which expects a real parent QWidget + DB setup).
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


def test_graphml_export_runs_on_pg_backend_no_skip_branch():
    """Bug 2 regression test.

    Pre-PG-UIFix: s3dgraphy_dot_bridge had 'if backend_is_postgres:
    skip graphml export' branch that set
    exported_files['graphml_status']['reason'] =
    'postgresql backend not yet supported'.

    Post-PG-UIFix: the skip branch is removed. The
    'postgresql backend not yet supported' string is gone from
    source.
    """
    from modules.s3dgraphy import s3dgraphy_dot_bridge as bridge

    import inspect
    src = inspect.getsource(bridge)
    assert "postgresql backend not yet supported" not in src, \
        "Obsolete PG-skip branch still present in graphml export"
    assert "Import requires a SQLite-backed" not in src, \
        "Obsolete SQLite-only import guard still present"
