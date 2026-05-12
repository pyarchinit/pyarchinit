"""PG-UIFix (5.7.8-alpha): regression tests for partial-scope hotfix.

Bug 1 (paradata/group manager + US picker) — SHIPPED on PG via
ParadataStore/GroupStore which route db_manager through
_resolve_db_handle shim (PG-D, 2026-05-11). Test 1 pins the
obsolete SQLite-only guards as ABSENT.

Bug 2 (graphml export on PG) — DEFERRED to PG-Bv2 milestone.
PG-B (5.7.1-alpha, 2026-05-10) flipped 5 SQL helpers in
graph_projector.py to DbHandle but left the orchestrator
populate_graph() with `Path(db_path)` at line 165 + the upstream
PyArchInitImporter call at line 190, which is SQLite-only.
The user-facing skip-branch in s3dgraphy_dot_bridge.py is restored
with an honest 'pending PG-Bv2' message. Test 2 pins the skip-branch
as PRESENT until PG-Bv2 ships.
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


def test_graphml_export_pg_skip_branch_is_present_pending_pg_bv2():
    """Bug 2 deferred-state pin.

    PG-UIFix (5.7.8-alpha) ships only Bug 1. Bug 2 (graphml export
    on PG) is deferred to PG-Bv2 because populate_graph() in
    modules/s3dgraphy/sync/graph_projector.py still calls the
    upstream SQLite-only PyArchInitImporter at line ~190 + does
    Path(db_path) at line ~165.

    The user-facing skip-branch in s3dgraphy_dot_bridge.py is kept
    with an honest message referencing PG-Bv2. This test asserts:

    - the skip branch IS present (so users don't get TypeError)
    - the honest 'pending PG-Bv2' message IS in source
    - the obsolete 'AI04' wording is NOT in source (was the original
      pre-PG-UIFix message that misleadingly named AI04)

    When PG-Bv2 ships, this test should be DELETED and the original
    'no_skip_branch' assertion restored.

    The Bug 1-like import-flow guards at lines ~742 and ~830 in
    s3dgraphy_dot_bridge are REMOVED by PG-UIFix (those are about
    ingest, not export — and GraphIngestor.populate_list accepts
    db_manager via _resolve_db_handle since PG-C, 2026-05-11).
    """
    from modules.s3dgraphy import s3dgraphy_dot_bridge as bridge

    import inspect
    src = inspect.getsource(bridge)
    assert "pending PG-Bv2 milestone" in src, \
        "PG-Bv2 follow-up message missing from skip-branch"
    assert "postgresql backend deferred to PG-Bv2" in src, \
        "Skip-branch status reason missing"
    assert "PostgreSQL support arrives with AI04" not in src, \
        "Obsolete AI04 wording still present (should be PG-Bv2)"
    assert "Import requires a SQLite-backed" not in src, \
        "Obsolete SQLite-only import-flow guard still present"
