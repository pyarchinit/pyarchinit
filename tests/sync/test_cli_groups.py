"""L2 subprocess tests for paradata add-group / list-groups /
add-us-to-group / remove-group + export --group-by."""
from __future__ import annotations
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = PLUGIN_ROOT / "scripts" / "s3dgraphy_sync.py"
FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")


@pytest.fixture
def mini_volterra(tmp_path):
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    return dst


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
        cwd=str(PLUGIN_ROOT),
    )


def test_cli_paradata_add_group(mini_volterra):
    r = _run("paradata", "add-group",
             "--db", str(mini_volterra),
             "--sito", "TestSite",
             "--name", "test-grp",
             "--us-uuid", "u1",
             "--us-uuid", "u2")
    assert r.returncode == 0, f"stderr: {r.stderr}"
    assert "OK" in r.stdout
    assert "group" in r.stdout


def test_cli_paradata_list_groups_after_add(mini_volterra):
    _run("paradata", "add-group",
         "--db", str(mini_volterra), "--sito", "TestSite",
         "--name", "test-grp", "--us-uuid", "u1")
    r = _run("paradata", "list-groups",
             "--db", str(mini_volterra), "--sito", "TestSite")
    assert r.returncode == 0
    assert "test-grp" in r.stdout
    assert "adhoc" in r.stdout


def test_cli_paradata_add_us_to_group(mini_volterra):
    r1 = _run("paradata", "add-group",
              "--db", str(mini_volterra), "--sito", "TestSite",
              "--name", "test-grp", "--us-uuid", "u1")
    uuid = r1.stdout.strip().split()[-1]
    r2 = _run("paradata", "add-us-to-group",
              "--db", str(mini_volterra), "--sito", "TestSite",
              "--group-uuid", uuid, "--us-uuid", "u2")
    assert r2.returncode == 0
    assert "OK" in r2.stdout

    r3 = _run("paradata", "list-groups",
              "--db", str(mini_volterra), "--sito", "TestSite")
    assert "u1" in r3.stdout
    assert "u2" in r3.stdout


def test_cli_paradata_remove_group(mini_volterra):
    r1 = _run("paradata", "add-group",
              "--db", str(mini_volterra), "--sito", "TestSite",
              "--name", "test-grp")
    uuid = r1.stdout.strip().split()[-1]
    r2 = _run("paradata", "remove-group",
              "--db", str(mini_volterra), "--sito", "TestSite",
              "--uuid", uuid)
    assert r2.returncode == 0
    r3 = _run("paradata", "list-groups",
              "--db", str(mini_volterra), "--sito", "TestSite")
    assert uuid not in r3.stdout


def test_cli_export_with_group_by(mini_volterra, tmp_path):
    """AC-17: export --group-by emits groups for listed dimensions."""
    # Apply Phase 1 migration first
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    add_columns(mini_volterra)
    backfill_uuids(mini_volterra)
    # Seed struttura on a few rows
    import sqlite3
    conn = sqlite3.connect(mini_volterra)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    rows = list(conn.execute(
        "SELECT id_us FROM us_table WHERE sito=? LIMIT 3", (sito,)))
    for (id_us,) in rows:
        conn.execute(
            "UPDATE us_table SET struttura='basilica' WHERE id_us=?",
            (id_us,))
    conn.commit()
    conn.close()

    out = tmp_path / "out.graphml"
    r = _run("export",
             "--db", str(mini_volterra),
             "--sito", sito,
             "--mapping", "pyarchinit_us_mapping",
             "--output", str(out),
             "--group-by", "struttura")
    assert r.returncode == 0, f"stderr: {r.stderr}"
    assert out.exists()
    text = out.read_text()
    assert "yfiles.foldertype=\"group\"" in text or \
           "yfiles.foldertype='group'" in text
    assert "grp_" in text


def test_cli_invalid_subcommand_exits_2(mini_volterra):
    r = _run("paradata", "totally-bogus",
             "--db", str(mini_volterra), "--sito", "X")
    assert r.returncode == 2
