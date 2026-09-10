"""The SQLite files shipped in resources/dbfiles must have working spatial
indexes (2026-09-10).

A geometry column registered with ``spatial_index_enabled = 1`` whose
R*Tree maintenance triggers (``gii_/giu_/gid_<table>_<column>``) are
missing is INVISIBLE in QGIS: the SpatiaLite provider selects the features
to draw through the R*Tree, which never receives the new geometries. Since
fa58feb8 (2025-10-12) the template copied by "Crea database SQLite" shipped
pyunitastratigrafiche, pyunitastratigrafiche_usm and
pyarchinit_us_negative_doc in that state (the schema-alignment scripts
dropped and recreated the tables without rebuilding the index), so every
newly created DB showed no US geometry. Plain sqlite3 is enough: the
triggers live in sqlite_master and the R*Tree is a built-in module.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

_DBFILES = Path(__file__).resolve().parents[2] / "resources" / "dbfiles"
SHIPPED = ["pyarchinit.sqlite", "pyarchinit_db.sqlite"]
# SpatiaLite's own ISO-metadata table: never drawn by pyArchInit.
IGNORED = {"iso_metadata"}


def _problems(path: Path) -> list:
    # immutable=1: pyarchinit_db.sqlite is in WAL mode and a plain read-only
    # open would leave -wal/-shm files next to the shipped database.
    con = sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)
    try:
        found = []
        for table, col in con.execute(
                "SELECT f_table_name, f_geometry_column FROM geometry_columns "
                "WHERE spatial_index_enabled = 1").fetchall():
            if table in IGNORED:
                continue
            triggers = {r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type = 'trigger' "
                "AND tbl_name = ?", (table,))}
            missing = [f"{p}_{table}_{col}" for p in ("gii", "giu", "gid")
                       if f"{p}_{table}_{col}" not in triggers]
            geoms = con.execute(
                f'SELECT count(*) FROM "{table}" WHERE "{col}" IS NOT NULL').fetchone()[0]
            indexed = con.execute(f'SELECT count(*) FROM "idx_{table}_{col}"').fetchone()[0]
            if missing or indexed != geoms:
                found.append(f"{table}.{col}: missing triggers {missing or '-'}, "
                             f"R*Tree rows {indexed} vs geometries {geoms}")
        return found
    finally:
        con.close()


@pytest.mark.parametrize("name", SHIPPED)
def test_every_indexed_geometry_column_is_maintained_and_in_sync(name):
    path = _DBFILES / name
    if not path.exists():
        pytest.skip(f"{name} not shipped")
    problems = _problems(path)
    assert not problems, "\n".join(problems)
