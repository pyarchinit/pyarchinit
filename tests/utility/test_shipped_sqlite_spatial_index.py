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

2026-09-11: the spatial views too. Views with no ROWID key or a key from
the attribute table, registrations of missing views, base tables with no
spatial index (OGR then needs SpatiaLite SQL functions some GDAL builds
lack) and views on tables that do not exist all drew nothing.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.db.spatial_view_repair import audit_spatial_views  # noqa: E402

_DBFILES = _ROOT / "resources" / "dbfiles"
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


def _shipped(name) -> Path:
    path = _DBFILES / name
    if not path.exists():
        pytest.skip(f"{name} not shipped")
    return path


def _open(path: Path):
    return sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)


@pytest.mark.parametrize("name", SHIPPED)
def test_every_indexed_geometry_column_is_maintained_and_in_sync(name):
    problems = _problems(_shipped(name))
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("name", SHIPPED)
def test_every_geometry_column_has_a_spatial_index(name):
    con = _open(_shipped(name))
    try:
        unindexed = [t for (t,) in con.execute(
            "SELECT f_table_name FROM geometry_columns WHERE spatial_index_enabled = 0")
            if t not in IGNORED]
    finally:
        con.close()
    assert not unindexed


@pytest.mark.parametrize("name", SHIPPED)
def test_every_spatial_view_is_keyed_on_its_geometry_table(name):
    con = _open(_shipped(name))
    try:
        bad = [f"{s.view}.{s.geometry}: {s.state} {s.detail}".strip()
               for s in audit_spatial_views(con) if s.state != "ok" or s.base_indexed is not True]
    finally:
        con.close()
    assert not bad, "\n".join(bad)


@pytest.mark.parametrize("name", SHIPPED)
def test_no_pyarchinit_view_is_broken(name):
    con = _open(_shipped(name))
    try:
        broken = []
        for (view,) in con.execute("SELECT name FROM sqlite_master WHERE type = 'view' "
                                   "AND (name LIKE 'pyarchinit%' OR name LIKE 'inventario%')").fetchall():
            try:
                con.execute(f'SELECT 1 FROM "{view}" LIMIT 1').fetchall()
            except sqlite3.Error as e:
                broken.append(f"{view}: {e}")
    finally:
        con.close()
    assert not broken, "\n".join(broken)
