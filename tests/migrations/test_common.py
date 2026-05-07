"""Tests for the migration shared helpers."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from scripts.migrations._common import auto_backup_sqlite, parse_argv


def test_auto_backup_sqlite_copies_file(tmp_path: Path):
    src = tmp_path / "x.sqlite"
    conn = sqlite3.connect(src)
    conn.execute("CREATE TABLE t (id INTEGER)")
    conn.execute("INSERT INTO t VALUES (42)")
    conn.commit()
    conn.close()

    backup_path = auto_backup_sqlite(src, tag="testing")
    assert backup_path.exists()
    assert backup_path != src
    # Open backup and verify the row is there
    bconn = sqlite3.connect(backup_path)
    assert bconn.execute("SELECT id FROM t").fetchone() == (42,)
    bconn.close()


def test_parse_argv_supports_dry_run_apply_rollback():
    args = parse_argv(["--db", "/tmp/x.sqlite", "--dry-run"])
    assert args.dry_run is True
    assert args.apply is False
    assert args.rollback is None
    args = parse_argv(["--db", "/tmp/x.sqlite", "--apply"])
    assert args.apply is True
    args = parse_argv(["--db", "/tmp/x.sqlite", "--rollback", "/tmp/backup.sqlite"])
    assert args.rollback == "/tmp/backup.sqlite"


def test_parse_argv_requires_one_action(capsys):
    with pytest.raises(SystemExit):
        parse_argv(["--db", "/tmp/x.sqlite"])  # no action
