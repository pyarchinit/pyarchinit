"""L2 subprocess tests for scripts/s3dgraphy_sync.py paradata ..."""
from __future__ import annotations
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


def test_cli_paradata_add_author(mini_volterra):
    r = _run("paradata", "add-author",
             "--db", str(mini_volterra),
             "--sito", "TestSite",
             "--name", "Marco")
    assert r.returncode == 0, f"stderr: {r.stderr}"
    assert "OK" in r.stdout
    assert "author" in r.stdout


def test_cli_paradata_list_authors_after_add(mini_volterra):
    _run("paradata", "add-author",
         "--db", str(mini_volterra),
         "--sito", "TestSite",
         "--name", "Marco",
         "--orcid", "0000-0002-1234-5678")
    r = _run("paradata", "list-authors",
             "--db", str(mini_volterra),
             "--sito", "TestSite")
    assert r.returncode == 0
    assert "Marco" in r.stdout
    assert "0000-0002-1234-5678" in r.stdout


def test_cli_paradata_add_license(mini_volterra):
    r = _run("paradata", "add-license",
             "--db", str(mini_volterra),
             "--sito", "TestSite",
             "--spdx", "CC-BY-NC-4.0")
    assert r.returncode == 0
    assert "OK" in r.stdout


def test_cli_paradata_add_embargo(mini_volterra):
    r = _run("paradata", "add-embargo",
             "--db", str(mini_volterra),
             "--sito", "TestSite",
             "--until", "2030-12-31",
             "--reason", "test embargo")
    assert r.returncode == 0
    assert "OK" in r.stdout


def test_cli_paradata_remove(mini_volterra):
    # Add author, capture uuid, then remove
    r = _run("paradata", "add-author",
             "--db", str(mini_volterra),
             "--sito", "TestSite",
             "--name", "Marco")
    assert r.returncode == 0
    # Output format: "OK — author <uuid>"
    uuid = r.stdout.strip().split()[-1]

    r2 = _run("paradata", "remove",
              "--db", str(mini_volterra),
              "--sito", "TestSite",
              "--uuid", uuid)
    assert r2.returncode == 0
    assert uuid in r2.stdout

    # Verify list is empty
    r3 = _run("paradata", "list-authors",
              "--db", str(mini_volterra),
              "--sito", "TestSite")
    assert r3.returncode == 0
    assert uuid not in r3.stdout


def test_cli_paradata_invalid_subcommand_exits_2(mini_volterra):
    r = _run("paradata", "totally-bogus", "--db", str(mini_volterra))
    assert r.returncode == 2
