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


def test_cli_invalid_subcommand_exits_2(mini_volterra):
    r = _run("paradata", "totally-bogus",
             "--db", str(mini_volterra), "--sito", "X")
    assert r.returncode == 2
