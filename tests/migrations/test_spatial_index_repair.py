"""Self-healing of SpatiaLite spatial indexes (2026-09-10).

A geometry column registered with spatial_index_enabled=1 whose R*Tree
maintenance triggers (gii_/giu_/gid_) are gone, or whose R*Tree is out of
sync with the table, is invisible in QGIS: the SpatiaLite provider selects
the features to draw through the R*Tree. Table-recreating scripts and
updaters (DROP TABLE + CREATE TABLE keeps the geometry_columns row but
loses the triggers) left many user DBs in that state, so
modules/db/spatial_index_repair.py checks and rebuilds the indexes when a
SQLite DB is connected.

The repair needs SpatiaLite: those tests are skipped on interpreters whose
sqlite3 cannot load extensions (e.g. the python.org macOS build); run them
with the QGIS python or a Homebrew python.
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.db import spatial_index_repair as sir  # noqa: E402

_CANDIDATES = [
    "/Applications/QGIS.app/Contents/MacOS/lib/mod_spatialite.so",
    "/opt/homebrew/lib/mod_spatialite",
    "/usr/local/lib/mod_spatialite",
    "mod_spatialite",
    "mod_spatialite.so",
    "mod_spatialite.dll",
]


def _find_spatialite():
    if not hasattr(sqlite3.Connection, "enable_load_extension"):
        return None
    probe = sqlite3.connect(":memory:")
    probe.enable_load_extension(True)
    try:
        for name in _CANDIDATES:
            try:
                probe.load_extension(name)
                return name
            except sqlite3.Error:
                continue
    finally:
        probe.close()
    return None


SPATIALITE = _find_spatialite()
needs_spatialite = pytest.mark.skipif(
    SPATIALITE is None, reason="sqlite3 cannot load mod_spatialite here")


def load_spatialite(con):
    con.enable_load_extension(True)
    con.load_extension(SPATIALITE)


def _refuse_spatialite(con):
    raise sqlite3.OperationalError("mod_spatialite not available")


X, Y = 479757.0, 4097377.0
POLY = f"MULTIPOLYGON((({X} {Y}, {X + 1} {Y}, {X + 1} {Y + 1}, {X} {Y})))"


def _spatial_db(path):
    """pyunitastratigrafiche (MULTIPOLYGON) + pyarchinit_us_negative_doc
    (LINESTRING), both indexed, 3 US geometries."""
    con = sqlite3.connect(path)
    load_spatialite(con)
    con.execute("SELECT InitSpatialMetaData(1)")
    con.execute("CREATE TABLE pyunitastratigrafiche (gid INTEGER PRIMARY KEY AUTOINCREMENT, us_s TEXT)")
    con.execute("SELECT AddGeometryColumn('pyunitastratigrafiche', 'the_geom', 32633, 'MULTIPOLYGON', 'XY')")
    con.execute("SELECT CreateSpatialIndex('pyunitastratigrafiche', 'the_geom')")
    con.execute("CREATE TABLE pyarchinit_us_negative_doc (gid INTEGER PRIMARY KEY AUTOINCREMENT, us_n TEXT)")
    con.execute("SELECT AddGeometryColumn('pyarchinit_us_negative_doc', 'the_geom', 32633, 'LINESTRING', 'XY')")
    con.execute("SELECT CreateSpatialIndex('pyarchinit_us_negative_doc', 'the_geom')")
    for i in range(3):
        con.execute("INSERT INTO pyunitastratigrafiche (us_s, the_geom) VALUES (?, GeomFromText(?, 32633))",
                    (str(i + 1), POLY))
    con.commit()
    con.close()
    return path


def _recreate_table_like_the_alignment_script(path, table="pyunitastratigrafiche"):
    """DROP TABLE + CREATE TABLE + reinsert, as scripts/fixes/
    final_postgres_alignment.py did: triggers gone, geometry_columns row
    (spatial_index_enabled=1) and the old R*Tree left behind."""
    con = sqlite3.connect(path)
    load_spatialite(con)
    con.execute(f"CREATE TABLE _bak AS SELECT * FROM {table}")
    con.execute(f"DROP TABLE {table}")
    con.execute(f"CREATE TABLE {table} (gid INTEGER PRIMARY KEY AUTOINCREMENT, us_s TEXT, the_geom BLOB)")
    con.execute(f"INSERT INTO {table} SELECT * FROM _bak")
    con.execute("DROP TABLE _bak")
    con.commit()
    con.close()


def _insert_and_is_visible(path, table="pyunitastratigrafiche"):
    """Digitise one geometry and check the R*Tree returns it, the way the
    QGIS SpatiaLite provider selects the features to draw."""
    con = sqlite3.connect(path)
    load_spatialite(con)
    cur = con.execute("INSERT INTO pyunitastratigrafiche (us_s, the_geom) VALUES ('new', GeomFromText(?, 32633))",
                      (POLY,))
    rowid = cur.lastrowid
    con.commit()
    seen = con.execute(
        f'SELECT count(*) FROM "idx_{table}_the_geom" WHERE pkid = ? '
        "AND xmin <= ? AND xmax >= ? AND ymin <= ? AND ymax >= ?",
        (rowid, X + 2, X - 1, Y + 2, Y - 1)).fetchone()[0]
    con.close()
    return seen == 1


def _status(path):
    con = sqlite3.connect(path)
    try:
        return {s.table: s for s in sir.audit_spatial_indexes(con)}
    finally:
        con.close()


@pytest.fixture(autouse=True)
def _fresh_session():
    sir.reset_session_cache()
    yield
    sir.reset_session_cache()


# --- audit (plain sqlite3, no SpatiaLite needed) ---------------------------

@needs_spatialite
def test_audit_flags_a_recreated_table_that_lost_its_index_triggers(tmp_path):
    db = _spatial_db(str(tmp_path / "scavo.sqlite"))
    _recreate_table_like_the_alignment_script(db)
    st = _status(db)
    assert not st["pyunitastratigrafiche"].ok
    assert st["pyunitastratigrafiche"].triggers < 3
    assert st["pyarchinit_us_negative_doc"].ok


def test_non_spatial_db_is_ignored(tmp_path):
    db = str(tmp_path / "plain.sqlite")
    sqlite3.connect(db).execute("CREATE TABLE t (a)").connection.commit()
    assert sir.ensure_spatial_indexes(db, _refuse_spatialite) == []


# --- repair ----------------------------------------------------------------

@needs_spatialite
def test_repair_makes_new_geometries_visible_again(tmp_path):
    db = _spatial_db(str(tmp_path / "scavo.sqlite"))
    _recreate_table_like_the_alignment_script(db)
    assert not _insert_and_is_visible(str(tmp_path / "scavo.sqlite"))  # the bug

    repaired = sir.ensure_spatial_indexes(db, load_spatialite, force=True)

    assert repaired == ["pyunitastratigrafiche.the_geom"]
    st = _status(db)
    assert all(s.ok for s in st.values())
    assert st["pyunitastratigrafiche"].indexed == st["pyunitastratigrafiche"].geometries
    assert _insert_and_is_visible(db)


@needs_spatialite
def test_index_out_of_sync_is_rebuilt_even_with_triggers_in_place(tmp_path):
    db = _spatial_db(str(tmp_path / "scavo.sqlite"))
    con = sqlite3.connect(db)
    con.execute('DELETE FROM "idx_pyunitastratigrafiche_the_geom"')
    con.commit()
    con.close()
    assert _status(db)["pyunitastratigrafiche"].indexed == 0

    assert sir.ensure_spatial_indexes(db, load_spatialite) == ["pyunitastratigrafiche.the_geom"]

    st = _status(db)["pyunitastratigrafiche"]
    assert st.ok and st.indexed == st.geometries == 3


@needs_spatialite
def test_a_geometry_column_registered_without_index_gets_one(tmp_path):
    # pyarchinit_punti_rif & co. in the shipped DBs: spatial_index_enabled = 0.
    # OGR then filters with SpatiaLite SQL functions, missing in some GDAL
    # builds (QGIS 3.x on macOS), and draws nothing
    db = _spatial_db(str(tmp_path / "scavo.sqlite"))
    con = sqlite3.connect(db)
    load_spatialite(con)
    con.execute("CREATE TABLE pyarchinit_punti_rif (gid INTEGER PRIMARY KEY AUTOINCREMENT, def_punto TEXT)")
    con.execute("SELECT AddGeometryColumn('pyarchinit_punti_rif', 'the_geom', 32633, 'POINT', 'XY')")
    con.execute("INSERT INTO pyarchinit_punti_rif (def_punto, the_geom) VALUES ('a', MakePoint(?, ?, 32633))",
                (X, Y))
    con.commit()
    con.close()
    assert not _status(db)["pyarchinit_punti_rif"].ok

    assert sir.ensure_spatial_indexes(db, load_spatialite) == ["pyarchinit_punti_rif.the_geom"]

    st = _status(db)["pyarchinit_punti_rif"]
    assert st.ok and st.indexed == st.geometries == 1
    con = sqlite3.connect(db)
    assert con.execute("SELECT spatial_index_enabled FROM geometry_columns "
                       "WHERE f_table_name = 'pyarchinit_punti_rif'").fetchone()[0] == 1
    con.close()


@needs_spatialite
def test_a_backup_of_the_broken_db_is_written_before_repairing(tmp_path):
    db = _spatial_db(str(tmp_path / "scavo.sqlite"))
    _recreate_table_like_the_alignment_script(db)

    sir.ensure_spatial_indexes(db, load_spatialite)

    backups = sorted(tmp_path.glob("scavo.sqlite.pre_spatial_index_repair_*"))
    assert len(backups) == 1
    assert not _status(str(backups[0]))["pyunitastratigrafiche"].ok  # original state kept


@needs_spatialite
def test_healthy_db_is_untouched_no_backup_no_spatialite_needed(tmp_path):
    db = _spatial_db(str(tmp_path / "scavo.sqlite"))
    before = Path(db).read_bytes()

    # the audit alone must not need the extension
    assert sir.ensure_spatial_indexes(db, _refuse_spatialite) == []

    assert Path(db).read_bytes() == before
    assert not list(tmp_path.glob("*.pre_spatial_index_repair_*"))


@needs_spatialite
def test_missing_spatialite_never_raises_and_leaves_the_db_alone(tmp_path):
    db = _spatial_db(str(tmp_path / "scavo.sqlite"))
    _recreate_table_like_the_alignment_script(db)
    before = Path(db).read_bytes()

    assert sir.ensure_spatial_indexes(db, _refuse_spatialite) == []

    assert Path(db).read_bytes() == before
    assert not list(tmp_path.glob("*.pre_spatial_index_repair_*"))


@needs_spatialite
def test_each_db_is_checked_once_per_session(tmp_path):
    db = _spatial_db(str(tmp_path / "scavo.sqlite"))
    assert sir.ensure_spatial_indexes(db, load_spatialite) == []
    _recreate_table_like_the_alignment_script(db)

    assert sir.ensure_spatial_indexes(db, load_spatialite) == []           # cached
    assert sir.ensure_spatial_indexes(db, load_spatialite, force=True) == [
        "pyunitastratigrafiche.the_geom"]


@needs_spatialite
def test_spatialite_internal_iso_metadata_is_ignored(tmp_path):
    db = _spatial_db(str(tmp_path / "scavo.sqlite"))
    con = sqlite3.connect(db)
    load_spatialite(con)
    con.execute("CREATE TABLE iso_metadata (id INTEGER PRIMARY KEY)")
    con.execute("SELECT AddGeometryColumn('iso_metadata', 'geometry', 4326, 'MULTIPOLYGON', 'XY')")
    con.execute("SELECT CreateSpatialIndex('iso_metadata', 'geometry')")
    for p in ("gii", "giu", "gid"):
        con.execute(f"DROP TRIGGER IF EXISTS {p}_iso_metadata_geometry")
    con.commit()
    con.close()

    assert "iso_metadata" not in _status(db)
    assert sir.ensure_spatial_indexes(db, load_spatialite) == []
