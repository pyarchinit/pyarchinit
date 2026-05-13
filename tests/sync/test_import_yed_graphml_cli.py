"""CLI smoke tests for yE-D `scripts/import_yed_graphml.py`.

L0: argparse plumbing without running the pipeline.
L1: subprocess.run with --dry-run on the mini fixture; verify exit
    code + DB stays empty.
"""
from __future__ import annotations

import os
import subprocess
import sqlite3
import sys
from pathlib import Path

import pytest


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
FIXTURE = PLUGIN_ROOT / "tests" / "sync" / "fixtures" / "em_demo_02_mini.graphml"


def test_cli_argparse_basic():
    """L0: build_parser() exposes the documented flags + policy choices."""
    # Import via module loader to avoid triggering main().
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_yed_cli_under_test",
        PLUGIN_ROOT / "scripts" / "import_yed_graphml.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    parser = mod.build_parser()
    actions = {a.dest: a for a in parser._actions}
    assert "graphml" in actions, "graphml positional arg missing"
    assert "site" in actions, "--site missing"
    assert "db" in actions, "--db missing"
    assert "conn_str" in actions, "--conn-str missing"
    assert "policy" in actions, "--policy missing"
    assert set(actions["policy"].choices) == {
        "skip", "fan_out", "representative", "synthetic"
    }, "policy choices drift"
    assert "dry_run" in actions, "--dry-run missing"
    assert "auto_defaults" in actions, "--auto-defaults missing"


def test_cli_dry_run_subprocess_on_mini_fixture(tmp_path):
    """L1: run the CLI as subprocess in --dry-run mode against a
    freshly built empty SQLite DB; verify exit 0 + DB stays empty
    (rollback worked end-to-end)."""
    assert FIXTURE.exists(), f"fixture missing: {FIXTURE}"

    # Build a minimal SQLite schema that import_yed_raw can write to.
    db = tmp_path / "test_cli.sqlite"
    conn = sqlite3.connect(str(db))
    conn.executescript("""
        CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, area TEXT DEFAULT '1', us TEXT,
            unita_tipo TEXT, node_uuid TEXT,
            rapporti TEXT, periodo_iniziale TEXT, fase_iniziale TEXT,
            d_stratigrafica TEXT, d_interpretativa TEXT,
            attivita TEXT, struttura TEXT, settore TEXT,
            ambient TEXT, saggio TEXT, quad_par TEXT, documentazione TEXT,
            UNIQUE(sito, area, us, unita_tipo)
        );
        CREATE TABLE inventario_materiali_table (
            id_invmat INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, area TEXT DEFAULT '1', us TEXT,
            tipo_reperto TEXT, criterio_schedatura TEXT,
            definizione TEXT,
            numero_inventario INTEGER, node_uuid TEXT
        );
        CREATE TABLE periodizzazione_table (
            id_perfas INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, periodo TEXT, fase TEXT,
            datazione_iniziale INTEGER, datazione_finale INTEGER,
            datazione_estesa TEXT, descrizione TEXT, node_uuid TEXT
        );
    """)
    conn.commit()
    conn.close()

    env = os.environ.copy()
    env["PYTHONPATH"] = str(PLUGIN_ROOT)
    proc = subprocess.run(
        [sys.executable, str(PLUGIN_ROOT / "scripts" / "import_yed_graphml.py"),
         str(FIXTURE),
         "--site", "TestSite",
         "--db", str(db),
         "--policy", "skip",
         "--dry-run"],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert proc.returncode == 0, (
        f"CLI exit non-zero. stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    assert "dry_run: True" in proc.stdout, (
        f"missing dry_run flag in output:\n{proc.stdout}"
    )

    # Verify DB stays empty after dry-run.
    conn = sqlite3.connect(str(db))
    try:
        n_us = conn.execute("SELECT COUNT(*) FROM us_table").fetchone()[0]
        n_inv = conn.execute(
            "SELECT COUNT(*) FROM inventario_materiali_table"
        ).fetchone()[0]
        n_per = conn.execute(
            "SELECT COUNT(*) FROM periodizzazione_table"
        ).fetchone()[0]
    finally:
        conn.close()
    assert n_us == 0, f"us_table not empty after --dry-run: {n_us}"
    assert n_inv == 0, f"inventario_materiali_table not empty: {n_inv}"
    assert n_per == 0, f"periodizzazione_table not empty: {n_per}"
