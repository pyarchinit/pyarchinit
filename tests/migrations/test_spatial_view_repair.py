"""Self-healing of SpatiaLite spatial VIEWS (2026-09-11).

QGIS (SpatiaLite provider) and OGR draw a registered spatial view by
filtering its key column against the R*Tree of the base table:
``<key> IN (SELECT pkid FROM idx_<base>_<geom> WHERE <bbox>)``. The key
must therefore be the ROWID of the table the geometry comes from. Found in
shipped and user DBs (2026-09-11):

* views recreated by the dev updater without any ROWID column: the implicit
  view rowid is NULL -> nothing drawn (pyarchinit_us_view: 184 -> 0);
* views whose ``rowid`` comes from the attribute table (``us_table``) instead
  of the geometry table (pyarchinit_quote_view): wrong/duplicated keys;
* registrations of views that do not exist, or that name a geometry column
  the view does not have;
* base tables without a spatial index: OGR builds its spatial filter with
  SpatiaLite SQL functions, missing in some GDAL builds (QGIS 3.x macOS),
  and draws nothing.

The SQL rewrite is pure Python (runs everywhere); the DB tests need
SpatiaLite and are skipped where sqlite3 cannot load extensions.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.db import spatial_index_repair as sir  # noqa: E402
from modules.db import spatial_view_repair as svr  # noqa: E402

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


# --- SQL rewrite (pure, no SpatiaLite) ---------------------------------------

QUOTE_WRONG_KEY = (
    "CREATE VIEW pyarchinit_quote_view AS SELECT a.rowid AS rowid, a.id_us AS id_us, "
    "a.sito AS sito, b.quota_q AS quota_q, b.the_geom AS the_geom "
    "FROM us_table AS a JOIN pyarchinit_quote AS b "
    "ON (a.sito = b.sito_q AND a.area = b.area_q AND a.us = b.us_q) ORDER BY a.us")

US_NO_KEY = (
    "CREATE VIEW pyarchinit_us_view AS\n    SELECT\n"
    "        CAST(pyunitastratigrafiche.gid AS INTEGER) as gid,\n"
    "        pyunitastratigrafiche.the_geom,\n        us_table.id_us,\n        us_table.us\n"
    "    FROM pyunitastratigrafiche\n    JOIN us_table ON\n"
    "        pyunitastratigrafiche.scavo_s = us_table.sito AND\n"
    "        pyunitastratigrafiche.area_s = us_table.area AND\n"
    "        pyunitastratigrafiche.us_s = us_table.us")

USM_QUOTED_OK = (
    'CREATE VIEW pyarchinit_usm_view as SELECT "a"."ROWID" AS "ROWID", "a"."gid" AS "gid", '
    '"a"."the_geom" AS "the_geom", "b"."id_us" AS "id_us" '
    'FROM "pyunitastratigrafiche_usm" AS "a" JOIN "us_table" AS "b" '
    'ON ("a"."us_s" = "b"."us") ORDER BY "b"."order_layer"')


def test_rewrite_replaces_a_key_taken_from_the_attribute_table():
    out = svr.rewrite_view_with_base_rowid(QUOTE_WRONG_KEY, "pyarchinit_quote")
    assert out is not None and out != QUOTE_WRONG_KEY
    head = out.split(" FROM ", 1)[0]
    assert "b.ROWID AS rowid" in head
    assert "a.rowid AS rowid" not in head
    assert out.endswith("ORDER BY a.us")                     # rest untouched
    assert "a.id_us AS id_us" in out and "b.the_geom AS the_geom" in out


def test_rewrite_adds_the_key_when_the_base_table_has_no_alias():
    out = svr.rewrite_view_with_base_rowid(US_NO_KEY, "pyunitastratigrafiche")
    select_list = out.split("SELECT", 1)[1].split("FROM", 1)[0]
    assert select_list.strip().startswith("pyunitastratigrafiche.ROWID AS rowid")
    assert "CAST(pyunitastratigrafiche.gid AS INTEGER) as gid" in out


def test_rewrite_keeps_an_already_correct_quoted_view_unchanged():
    assert svr.rewrite_view_with_base_rowid(USM_QUOTED_OK, "pyunitastratigrafiche_usm") == USM_QUOTED_OK


@pytest.mark.parametrize("sql", [
    "CREATE VIEW v AS SELECT DISTINCT a.x AS x, a.the_geom AS the_geom FROM t AS a",
    "CREATE VIEW v AS SELECT a.x AS x, a.the_geom AS the_geom FROM t AS a GROUP BY a.x",
    "CREATE VIEW v AS SELECT a.the_geom AS the_geom FROM t AS a UNION SELECT b.the_geom FROM t AS b",
    "CREATE VIEW v AS SELECT x.the_geom AS the_geom FROM other AS x",   # base table not in FROM
])
def test_rewrite_refuses_views_it_cannot_change_safely(sql):
    assert svr.rewrite_view_with_base_rowid(sql, "t" if "other" not in sql else "t") is None


# --- DB fixtures ---------------------------------------------------------------

def _pt(x, y=0.0):
    return "POINT(%s %s)" % (x, y)


def _poly(x):
    return "MULTIPOLYGON(((%s 0, %s 0, %s 1, %s 0)))" % (x, x + 1, x + 1, x)


def _db(path):
    """us_table + three geometry tables and five registered views covering
    every defect found in the real DBs."""
    con = sqlite3.connect(path)
    load_spatialite(con)
    con.execute("SELECT InitSpatialMetaData(1)")
    con.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, us TEXT)")
    con.executemany("INSERT INTO us_table VALUES (?, 'S', '1', ?)", [(1, "1"), (2, "2")])

    con.execute("CREATE TABLE pyarchinit_quote (gid INTEGER PRIMARY KEY AUTOINCREMENT, "
                "sito_q TEXT, area_q TEXT, us_q TEXT, quota_q REAL)")
    con.execute("SELECT AddGeometryColumn('pyarchinit_quote', 'the_geom', 32633, 'POINT', 'XY')")
    con.execute("SELECT CreateSpatialIndex('pyarchinit_quote', 'the_geom')")
    for i, us in enumerate(["1", "1", "1", "2"]):          # 3 quotes on US 1
        con.execute("INSERT INTO pyarchinit_quote (sito_q, area_q, us_q, quota_q, the_geom) "
                    "VALUES ('S', '1', ?, ?, GeomFromText(?, 32633))", (us, 10.0 + i, _pt(100 + 10 * i)))

    con.execute("CREATE TABLE pyunitastratigrafiche (gid INTEGER PRIMARY KEY AUTOINCREMENT, "
                "scavo_s TEXT, area_s TEXT, us_s TEXT)")
    con.execute("SELECT AddGeometryColumn('pyunitastratigrafiche', 'the_geom', 32633, 'MULTIPOLYGON', 'XY')")
    con.execute("SELECT CreateSpatialIndex('pyunitastratigrafiche', 'the_geom')")
    for us, x in (("1", 200), ("2", 300)):
        con.execute("INSERT INTO pyunitastratigrafiche (scavo_s, area_s, us_s, the_geom) "
                    "VALUES ('S', '1', ?, GeomFromText(?, 32633))", (us, _poly(x)))

    con.execute("CREATE TABLE pyarchinit_siti (gid INTEGER PRIMARY KEY AUTOINCREMENT, sito_nome TEXT)")
    con.execute("SELECT AddGeometryColumn('pyarchinit_siti', 'the_geom', 32633, 'POINT', 'XY')")  # NO index
    con.execute("INSERT INTO pyarchinit_siti (sito_nome, the_geom) VALUES ('S', GeomFromText(?, 32633))",
                (_pt(500),))

    con.execute(QUOTE_WRONG_KEY)
    con.execute(US_NO_KEY)
    con.execute("CREATE VIEW pyarchinit_site_view AS SELECT a.rowid AS rowid, a.sito_nome AS sito_nome, "
                "a.the_geom AS the_geom FROM pyarchinit_siti AS a")
    con.execute("CREATE VIEW pyarchinit_distinct_view AS SELECT DISTINCT a.us_q AS us_q, "
                "a.the_geom AS the_geom FROM pyarchinit_quote AS a")
    # like the UT views created by ensure_ut_geometry_tables_exist: no key,
    # never registered in views_geometry_columns
    con.execute("CREATE VIEW pyarchinit_ut_point_view AS SELECT p.gid, p.the_geom, p.us_q "
                "FROM pyarchinit_quote p")
    regs = [
        ("pyarchinit_quote_view", "the_geom", "rowid", "pyarchinit_quote", "the_geom"),
        ("pyarchinit_quote_view", "geom", "rowid_1", "pyarchinit_quote", "the_geom"),     # stale
        ("pyarchinit_us_view", "the_geom", "rowid", "pyunitastratigrafiche", "the_geom"),
        ("pyarchinit_site_view", "the_geom", "rowid", "pyarchinit_siti", "the_geom"),
        ("pyarchinit_distinct_view", "the_geom", "rowid", "pyarchinit_quote", "the_geom"),
        ("pyarchinit_sezioni_view", "the_geom", "rowid", "pyarchinit_siti", "the_geom"),  # missing, canonical
        ("ghost_view", "the_geom", "rowid", "pyarchinit_quote", "the_geom"),              # missing, orphan
    ]
    con.executemany("INSERT INTO views_geometry_columns (view_name, view_geometry, view_rowid, "
                    "f_table_name, f_geometry_column, read_only) VALUES (?, ?, ?, ?, ?, 1)", regs)
    con.execute("INSERT INTO views_geometry_columns_auth (view_name, view_geometry, hidden) "
                "VALUES ('ghost_view', 'the_geom', 0)")
    con.commit()
    con.close()
    return path


CANONICAL = {
    "pyarchinit_sezioni_view": (
        "CREATE VIEW pyarchinit_sezioni_view AS SELECT a.rowid AS rowid, a.sito_nome AS sito, "
        "a.the_geom AS the_geom FROM pyarchinit_siti AS a"),
}


def _drawn(con, view, key, base, x, y=0.0, eps=0.5):
    """Rows the QGIS/OGR R*Tree filter returns for a tiny bbox around (x, y)."""
    return con.execute(
        'SELECT count(*) FROM "%s" WHERE "%s" IN (SELECT pkid FROM "idx_%s_the_geom" '
        'WHERE xmin <= ? AND xmax >= ? AND ymin <= ? AND ymax >= ?)' % (view, key, base),
        (x + eps, x - eps, y + eps, y - eps)).fetchone()[0]


def _states(path):
    con = sqlite3.connect(path)
    try:
        return {(s.view, s.geometry): s.state for s in svr.audit_spatial_views(con)}
    finally:
        con.close()


@pytest.fixture(autouse=True)
def _fresh_session():
    sir.reset_session_cache()
    yield
    sir.reset_session_cache()


@pytest.fixture
def broken_db(tmp_path):
    if SPATIALITE is None:
        pytest.skip("sqlite3 cannot load mod_spatialite here")
    return _db(str(tmp_path / "scavo.sqlite"))


# --- audit -------------------------------------------------------------------------

@needs_spatialite
def test_audit_classifies_every_defect(broken_db):
    st = _states(broken_db)
    assert st[("pyarchinit_quote_view", "the_geom")] == "bad_key"      # key from us_table
    assert st[("pyarchinit_quote_view", "geom")] == "stale"
    assert st[("pyarchinit_us_view", "the_geom")] == "bad_key"         # no key at all
    assert st[("pyarchinit_site_view", "the_geom")] == "ok"
    assert st[("pyarchinit_distinct_view", "the_geom")] == "unsafe"
    assert st[("pyarchinit_sezioni_view", "the_geom")] == "missing"
    assert st[("ghost_view", "the_geom")] == "missing"
    assert st[("pyarchinit_ut_point_view", "the_geom")] == "unregistered"
    con = sqlite3.connect(broken_db)
    unindexed = {s.base for s in svr.audit_spatial_views(con) if s.base_indexed is False}
    con.close()
    assert unindexed == {"pyarchinit_siti"}


@needs_spatialite
def test_the_bug_wrong_key_draws_the_wrong_feature(broken_db):
    con = sqlite3.connect(broken_db)
    # quote #3 (pkid 3, x=120): the view's key is us_table.rowid (1 or 2)
    assert _drawn(con, "pyarchinit_quote_view", "rowid", "pyarchinit_quote", 120) == 0
    con.close()


# --- repair ------------------------------------------------------------------------

@needs_spatialite
def test_repair_makes_each_view_draw_exactly_its_own_features(broken_db):
    done = sir.ensure_spatial_layers(broken_db, load_spatialite, canonical_views=CANONICAL)
    assert done
    con = sqlite3.connect(broken_db)
    for i in range(4):                                   # every quote, alone in its bbox
        assert _drawn(con, "pyarchinit_quote_view", "rowid", "pyarchinit_quote", 100 + 10 * i) == 1
    assert _drawn(con, "pyarchinit_us_view", "rowid", "pyunitastratigrafiche", 200.5, 0.5) == 1
    assert _drawn(con, "pyarchinit_us_view", "rowid", "pyunitastratigrafiche", 300.5, 0.5) == 1
    # pyArchInit also opens views with the explicit key "ROWID"
    assert _drawn(con, "pyarchinit_quote_view", "ROWID", "pyarchinit_quote", 110) == 1
    # the unregistered UT-like view is now a registered spatial view
    reg = con.execute("SELECT view_rowid, f_table_name, f_geometry_column FROM views_geometry_columns "
                      "WHERE view_name = 'pyarchinit_ut_point_view'").fetchone()
    assert reg == ("rowid", "pyarchinit_quote", "the_geom")
    assert _drawn(con, "pyarchinit_ut_point_view", "rowid", "pyarchinit_quote", 100) == 1
    con.close()


@needs_spatialite
def test_orphan_and_stale_registrations_are_removed_with_their_children(broken_db):
    sir.ensure_spatial_layers(broken_db, load_spatialite, canonical_views=CANONICAL)
    con = sqlite3.connect(broken_db)
    regs = {(r[0], r[1]) for r in con.execute("SELECT view_name, view_geometry FROM views_geometry_columns")}
    auth = con.execute("SELECT count(*) FROM views_geometry_columns_auth WHERE view_name = 'ghost_view'").fetchone()[0]
    con.close()
    assert ("ghost_view", "the_geom") not in regs and auth == 0
    assert ("pyarchinit_quote_view", "geom") not in regs
    assert ("pyarchinit_quote_view", "the_geom") in regs


@needs_spatialite
def test_missing_view_is_recreated_from_its_canonical_definition(broken_db):
    sir.ensure_spatial_layers(broken_db, load_spatialite, canonical_views=CANONICAL)
    con = sqlite3.connect(broken_db)
    load_spatialite(con)
    assert con.execute("SELECT count(*) FROM pyarchinit_sezioni_view WHERE the_geom IS NOT NULL").fetchone()[0] == 1
    assert _drawn(con, "pyarchinit_sezioni_view", "rowid", "pyarchinit_siti", 500) == 1
    con.close()


@needs_spatialite
def test_base_table_without_spatial_index_gets_one(broken_db):
    sir.ensure_spatial_layers(broken_db, load_spatialite, canonical_views=CANONICAL)
    con = sqlite3.connect(broken_db)
    enabled = con.execute("SELECT spatial_index_enabled FROM geometry_columns "
                          "WHERE f_table_name = 'pyarchinit_siti'").fetchone()[0]
    assert enabled == 1
    assert _drawn(con, "pyarchinit_site_view", "rowid", "pyarchinit_siti", 500) == 1
    con.close()


@needs_spatialite
def test_distinct_view_is_left_untouched(broken_db):
    con = sqlite3.connect(broken_db)
    before = con.execute("SELECT sql FROM sqlite_master WHERE name = 'pyarchinit_distinct_view'").fetchone()[0]
    con.close()
    sir.ensure_spatial_layers(broken_db, load_spatialite, canonical_views=CANONICAL)
    con = sqlite3.connect(broken_db)
    after = con.execute("SELECT sql FROM sqlite_master WHERE name = 'pyarchinit_distinct_view'").fetchone()[0]
    con.close()
    assert after == before


@needs_spatialite
def test_after_the_repair_everything_is_clean_and_a_second_run_does_nothing(broken_db):
    sir.ensure_spatial_layers(broken_db, load_spatialite, canonical_views=CANONICAL)
    st = _states(broken_db)
    assert all(v in ("ok", "unsafe") for v in st.values()), st
    before = Path(broken_db).read_bytes()
    assert sir.ensure_spatial_layers(broken_db, load_spatialite, force=True,
                                     canonical_views=CANONICAL) == []
    assert Path(broken_db).read_bytes() == before


@needs_spatialite
def test_one_backup_before_any_write(broken_db, tmp_path):
    sir.ensure_spatial_layers(broken_db, load_spatialite, canonical_views=CANONICAL)
    backups = list(tmp_path.glob("scavo.sqlite.pre_spatial_index_repair_*"))
    assert len(backups) == 1
    assert _states(str(backups[0]))[("pyarchinit_quote_view", "the_geom")] == "bad_key"


@needs_spatialite
def test_an_empty_view_without_key_is_repaired_from_its_definition(broken_db):
    # template DBs: pyarchinit_usm_view with no ROWID and no rows yet; the
    # key can only be checked on the CREATE VIEW text
    con = sqlite3.connect(broken_db)
    load_spatialite(con)
    con.execute("CREATE TABLE pyunitastratigrafiche_usm (gid INTEGER PRIMARY KEY AUTOINCREMENT, us_s TEXT)")
    con.execute("SELECT AddGeometryColumn('pyunitastratigrafiche_usm', 'the_geom', 32633, 'MULTIPOLYGON', 'XY')")
    con.execute("SELECT CreateSpatialIndex('pyunitastratigrafiche_usm', 'the_geom')")
    con.execute("CREATE VIEW pyarchinit_usm_view AS SELECT pyunitastratigrafiche_usm.gid, "
                "pyunitastratigrafiche_usm.the_geom, us_table.us FROM pyunitastratigrafiche_usm "
                "JOIN us_table ON pyunitastratigrafiche_usm.us_s = us_table.us")
    con.execute("INSERT INTO views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, "
                "f_geometry_column, read_only) VALUES ('pyarchinit_usm_view', 'the_geom', 'rowid', "
                "'pyunitastratigrafiche_usm', 'the_geom', 1)")
    con.commit()
    con.close()
    assert _states(broken_db)[("pyarchinit_usm_view", "the_geom")] == "bad_key"
    sir.ensure_spatial_layers(broken_db, load_spatialite, canonical_views=CANONICAL)
    con = sqlite3.connect(broken_db)
    load_spatialite(con)
    con.execute("INSERT INTO pyunitastratigrafiche_usm (us_s, the_geom) VALUES ('2', GeomFromText(?, 32633))",
                (_poly(700),))
    con.commit()
    assert _drawn(con, "pyarchinit_usm_view", "rowid", "pyunitastratigrafiche_usm", 700.5, 0.5) == 1
    con.close()


@needs_spatialite
def test_registration_of_a_view_on_a_missing_table_is_removed_once(broken_db, tmp_path):
    # sample DB: pyarchinit_uscaratterizzazioni_view registered, its base
    # table never created. The registration goes (nothing can draw it), the
    # view is left as it is, and later sessions have nothing to do
    sir.ensure_spatial_layers(broken_db, load_spatialite, canonical_views=CANONICAL)
    con = sqlite3.connect(broken_db)
    con.execute("CREATE VIEW pyarchinit_uscaratterizzazioni_view AS SELECT pyuscaratterizzazioni.gid, "
                "pyuscaratterizzazioni.the_geom FROM pyuscaratterizzazioni")
    con.execute("INSERT INTO views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, "
                "f_geometry_column, read_only) VALUES ('pyarchinit_uscaratterizzazioni_view', 'the_geom', "
                "'gid', 'pyuscaratterizzazioni', 'the_geom', 1)")
    con.commit()
    st = {s.view: s for s in svr.audit_spatial_views(con, CANONICAL)}
    con.close()
    assert st["pyarchinit_uscaratterizzazioni_view"].state == "broken"
    assert st["pyarchinit_uscaratterizzazioni_view"].base_indexed is None

    assert sir.ensure_spatial_layers(broken_db, load_spatialite, force=True, canonical_views=CANONICAL) == [
        "registrazione rimossa pyarchinit_uscaratterizzazioni_view.the_geom "
        "(tabella base pyuscaratterizzazioni inesistente)"]
    con = sqlite3.connect(broken_db)
    assert con.execute("SELECT count(*) FROM sqlite_master "
                       "WHERE name = 'pyarchinit_uscaratterizzazioni_view'").fetchone()[0] == 1
    con.close()

    before = Path(broken_db).read_bytes()
    backups = set(tmp_path.glob("*.pre_spatial_index_repair_*"))
    assert sir.ensure_spatial_layers(broken_db, load_spatialite, force=True, canonical_views=CANONICAL) == []
    assert Path(broken_db).read_bytes() == before
    assert set(tmp_path.glob("*.pre_spatial_index_repair_*")) == backups


@needs_spatialite
def test_a_geometry_repeated_on_several_rows_gets_the_base_key(broken_db):
    # inventario_materiali_view: the site point joined to every find of the
    # site. The base ROWID repeats, but it is the only key the R*Tree filter
    # can use; with no key nothing at all is drawn
    con = sqlite3.connect(broken_db)
    con.execute("CREATE VIEW inventario_materiali_view AS SELECT a.sito_nome AS sito_nome, "
                "a.the_geom AS the_geom, b.rowid AS rowid_1, b.us AS us "
                "FROM pyarchinit_siti AS a JOIN us_table AS b ON (a.sito_nome = b.sito)")
    con.execute("INSERT INTO views_geometry_columns (view_name, view_geometry, view_rowid, f_table_name, "
                "f_geometry_column, read_only) VALUES ('inventario_materiali_view', 'the_geom', 'rowid', "
                "'pyarchinit_siti', 'the_geom', 1)")
    con.commit()
    con.close()
    assert _states(broken_db)[("inventario_materiali_view", "the_geom")] == "bad_key"

    sir.ensure_spatial_layers(broken_db, load_spatialite, canonical_views=CANONICAL)

    assert _states(broken_db)[("inventario_materiali_view", "the_geom")] == "ok"
    con = sqlite3.connect(broken_db)
    assert _drawn(con, "inventario_materiali_view", "rowid", "pyarchinit_siti", 500) == 2   # one row per US
    con.close()


@needs_spatialite
def test_missing_spatialite_leaves_views_untouched_and_never_raises(broken_db, tmp_path):
    before = Path(broken_db).read_bytes()
    assert sir.ensure_spatial_layers(broken_db, _refuse_spatialite, canonical_views=CANONICAL) == []
    assert Path(broken_db).read_bytes() == before
    assert not list(tmp_path.glob("*.pre_spatial_index_repair_*"))
