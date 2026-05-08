"""Subprocess tests for scripts/s3dgraphy_sync.py.

Exercises the CLI surface end-to-end via subprocess.run() so test
runs match what a user types in the shell.

Note: the on-disk EXTERNAL_GRAPHML fixture has EMIDs from the
build-time backfill, which uses non-deterministic uuid7 values. To
get a graphml whose EMIDs match the fresh per-test backfill we
generate the graphml inline in tests that need a meaningful import
(see _project_to_graphml below).
"""
from __future__ import annotations
import hashlib
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = PLUGIN_ROOT / "scripts" / "s3dgraphy_sync.py"
FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")
EXTERNAL_GRAPHML = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
                    / "mini_volterra_external.graphml")


@pytest.fixture
def mini_volterra(tmp_path):
    """Copy fixture to tmp + apply Phase 1 migration."""
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    add_columns(dst)
    backfill_uuids(dst)
    return dst


def _run(*args):
    """Run the CLI script as subprocess, returning the
    CompletedProcess. cwd is the plugin root so the script's
    relative imports resolve."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
        cwd=str(PLUGIN_ROOT),
    )


def _sito(db):
    conn = sqlite3.connect(db)
    s = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    return s


def _project_to_graphml(db_path, sito, out_path, *, mutate_field=None,
                        mutate_value=None):
    """Build a graphml from db_path via GraphProjector, optionally
    mutating one stratigraphic node so import will detect a real
    diff. Mirrors tests/sync/fixtures/build_mini_volterra_external.
    py but inline so EMIDs match the freshly-backfilled DB."""
    # Pre-import system pandas/lxml BEFORE ext_libs insertion (same
    # pattern as scripts/s3dgraphy_sync.py:_setup_path).
    import pandas  # noqa: F401
    from lxml import etree as _etree  # noqa: F401
    ext = str(PLUGIN_ROOT / "ext_libs")
    if ext in sys.path:
        sys.path.remove(ext)
    sys.path.insert(0, ext)
    for m in [k for k in list(sys.modules)
              if k == "s3dgraphy" or k.startswith("s3dgraphy.")]:
        del sys.modules[m]
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from s3dgraphy.exporter.graphml.graphml_exporter import GraphMLExporter
    graph = GraphProjector().populate_graph(db_path, sito=sito)
    if mutate_field is not None:
        for n in graph.nodes:
            attrs = getattr(n, "attributes", None) or {}
            if attrs.get("us"):
                attrs[mutate_field] = mutate_value
                break
    GraphMLExporter(graph).export(str(out_path),
                                  persist_auxiliary=False)
    return out_path


def test_cli_export_subprocess(tmp_path, mini_volterra):
    out = tmp_path / "out.graphml"
    r = _run("export", "--db", str(mini_volterra),
             "--graphml", str(out),
             "--sito", _sito(mini_volterra))
    assert r.returncode == 0, f"stderr={r.stderr!r}"
    assert out.exists() and out.stat().st_size > 1000


def test_cli_import_dry_run_default(tmp_path, mini_volterra):
    """AC-10 — no --apply means no DB writes."""
    sito = _sito(mini_volterra)
    graphml = tmp_path / "live.graphml"
    _project_to_graphml(mini_volterra, sito, graphml,
                        mutate_field="d_stratigrafica",
                        mutate_value="DRY_RUN_PROBE")
    sha_before = hashlib.sha256(mini_volterra.read_bytes()).hexdigest()
    r = _run("import", "--db", str(mini_volterra),
             "--graphml", str(graphml),
             "--sito", sito)
    assert r.returncode == 0, f"stderr={r.stderr!r}\nstdout={r.stdout!r}"
    assert "DRY-RUN" in r.stdout
    sha_after = hashlib.sha256(mini_volterra.read_bytes()).hexdigest()
    assert sha_before == sha_after, "import without --apply modified DB"


def test_cli_import_apply_writes(tmp_path, mini_volterra):
    """--apply must reach WRITTEN status (commit path), not DRY-RUN.

    Note: we don't assert a sha256 change because the GraphML
    serialize+parse round-trip via s3dgraphy 0.1.40 strips
    PyArchInit-specific attributes (`us`, `node_uuid`,
    `d_stratigrafica`, ...), so a mutated graphml typically
    produces applied=0 — i.e. the WRITTEN-but-no-op contract
    documented by test_idempotent_ingest. The label difference
    (WRITTEN vs DRY-RUN) is the load-bearing signal that --apply
    routed through the commit branch instead of rollback."""
    sito = _sito(mini_volterra)
    graphml = tmp_path / "live.graphml"
    _project_to_graphml(mini_volterra, sito, graphml,
                        mutate_field="d_stratigrafica",
                        mutate_value="APPLY_PROBE")
    r = _run("import", "--db", str(mini_volterra),
             "--graphml", str(graphml),
             "--sito", sito, "--apply")
    assert r.returncode == 0, f"stderr={r.stderr!r}\nstdout={r.stdout!r}"
    assert "WRITTEN" in r.stdout
    assert "DRY-RUN" not in r.stdout


def test_cli_export_missing_db_exits_1(tmp_path):
    r = _run("export", "--db", str(tmp_path / "nope.sqlite"),
             "--graphml", str(tmp_path / "out.graphml"),
             "--sito", "X")
    assert r.returncode == 1
    assert "ERROR" in r.stderr
