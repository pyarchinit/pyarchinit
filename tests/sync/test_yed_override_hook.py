"""Tests for the yEd-raw override hook (s3dgraphy #10 decoupling).

The hook lets a host application (pyArchInit's QGIS plugin) inject
GUI prompt logic without `graph_ingestor.py` importing Qt or
`pyarchinit.*`. These tests pin down the contract:

    1. No hook registered → populate_list dispatches to import_yed_raw
       with default (overrides=None, policy=SKIP).
    2. Hook registered → it is called with the right args; its
       return value (overrides + policy) is forwarded to import_yed_raw.
    3. Hook returns cancelled=True → populate_list short-circuits with
       an IngestResult carrying applied=0 and a cancellation error;
       import_yed_raw is NOT invoked.
    4. register_yed_override_hook / clear_yed_override_hook are
       symmetric and idempotent.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import text

from modules.s3dgraphy.sync._db_handle import DbHandle
from modules.s3dgraphy.sync import graph_ingestor as gi_mod
from modules.s3dgraphy.sync.graph_ingestor import (
    GraphIngestor,
    YedOverrideResult,
    clear_yed_override_hook,
    register_yed_override_hook,
)
from modules.s3dgraphy.sync.ingest_result import IngestResult
from modules.s3dgraphy.sync.yed_rapporti_policy import FolderEdgePolicy


FIXTURE = (
    Path(__file__).parent / "fixtures" / "em_demo_02_mini.graphml"
)


@pytest.fixture
def handle(tmp_path: Path) -> DbHandle:
    """Bare-bones DbHandle; the real import_yed_raw is monkeypatched
    away in every test, so the schema doesn't need to be complete."""
    dbfile = tmp_path / "hook_test.sqlite"
    h = DbHandle.from_path(dbfile)
    # Empty us_table just so _resolve_db_handle's downstream callers
    # don't trip on a totally bare DB if anything peeks. Tests that
    # actually exercise the import path mock it out entirely.
    with h.engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS us_table (id INTEGER)"))
    return h


@pytest.fixture(autouse=True)
def _clear_hook_around_each_test():
    """Make sure no test leaks a registered hook into the next."""
    clear_yed_override_hook()
    yield
    clear_yed_override_hook()


@pytest.fixture
def workspace_env(tmp_path, monkeypatch):
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", str(tmp_path / "_ws"))
    (tmp_path / "_ws").mkdir(parents=True, exist_ok=True)


def _spy_import_yed_raw(monkeypatch):
    """Replace import_yed_raw with a spy that records its kwargs and
    returns an empty IngestResult. Returns the captured-kwargs dict."""
    captured: dict = {}

    def _spy(handle, graphml_path, sito, drafts, *,
            policy, dry_run, overrides):
        captured["handle"] = handle
        captured["graphml_path"] = graphml_path
        captured["sito"] = sito
        captured["drafts"] = drafts
        captured["policy"] = policy
        captured["dry_run"] = dry_run
        captured["overrides"] = overrides
        return IngestResult(
            applied=0, inserted=0, updated=0,
            skipped=0, epochs_created=0, errors=(),
        )

    # Patch the symbol on the module where graph_ingestor actually
    # looks it up (lazy `from .yed_import_pipeline import import_yed_raw`).
    import modules.s3dgraphy.sync.yed_import_pipeline as pipe
    monkeypatch.setattr(pipe, "import_yed_raw", _spy)
    return captured


# ---------------------------------------------------------------------------
# Test 1 — no hook registered → defaults flow through
# ---------------------------------------------------------------------------

def test_no_hook_uses_defaults(handle, workspace_env, monkeypatch):
    captured = _spy_import_yed_raw(monkeypatch)
    assert gi_mod._yed_override_hook is None  # belt-and-braces

    result = GraphIngestor().populate_list(
        graph=FIXTURE,           # Path → auto-loads + sets graphml_path
        db_path=handle,
        sito="DEMO_SITE",
        graphml_path=FIXTURE,
    )

    assert result.errors == ()
    assert captured["overrides"] is None
    assert captured["policy"] == FolderEdgePolicy.SKIP
    assert captured["sito"] == "DEMO_SITE"


# ---------------------------------------------------------------------------
# Test 2 — registered hook is called and its return value is forwarded
# ---------------------------------------------------------------------------

def test_hook_called_and_return_forwarded(
    handle, workspace_env, monkeypatch,
):
    captured = _spy_import_yed_raw(monkeypatch)
    calls: list[tuple] = []

    def _hook(drafts, graphml_path, h, sito):
        calls.append((drafts, graphml_path, h, sito))
        return YedOverrideResult(
            overrides={"some": "override"},
            policy=FolderEdgePolicy.FAN_OUT,
            cancelled=False,
        )

    register_yed_override_hook(_hook)

    GraphIngestor().populate_list(
        graph=FIXTURE,
        db_path=handle,
        sito="DEMO_SITE",
        graphml_path=FIXTURE,
    )

    # Hook called exactly once with positional args we expect.
    assert len(calls) == 1
    drafts, gpath, h_arg, sito = calls[0]
    assert sito == "DEMO_SITE"
    assert Path(gpath) == FIXTURE
    assert h_arg is handle
    # drafts must carry the 3 yE-D parser outputs.
    assert set(drafts.keys()) == {"classified", "periods", "folders"}

    # The hook's overrides + policy reached import_yed_raw.
    assert captured["overrides"] == {"some": "override"}
    assert captured["policy"] == FolderEdgePolicy.FAN_OUT


# ---------------------------------------------------------------------------
# Test 3 — cancelled=True short-circuits before import_yed_raw
# ---------------------------------------------------------------------------

def test_hook_cancelled_short_circuits(
    handle, workspace_env, monkeypatch,
):
    captured = _spy_import_yed_raw(monkeypatch)

    def _hook(drafts, graphml_path, h, sito):
        return YedOverrideResult(cancelled=True)

    register_yed_override_hook(_hook)

    result = GraphIngestor().populate_list(
        graph=FIXTURE,
        db_path=handle,
        sito="DEMO_SITE",
        graphml_path=FIXTURE,
    )

    assert result.applied == 0
    assert any("cancel" in err.lower() for err in result.errors)
    # The spy must NEVER have been called.
    assert captured == {}


# ---------------------------------------------------------------------------
# Test 4 — register / clear API symmetry
# ---------------------------------------------------------------------------

def test_register_then_clear_restores_default_state():
    def _noop(*a, **kw):
        return YedOverrideResult()

    assert gi_mod._yed_override_hook is None
    register_yed_override_hook(_noop)
    assert gi_mod._yed_override_hook is _noop

    clear_yed_override_hook()
    assert gi_mod._yed_override_hook is None

    # Clearing twice must not raise.
    clear_yed_override_hook()
    assert gi_mod._yed_override_hook is None
