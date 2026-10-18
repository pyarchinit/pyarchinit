"""La scrittura dei disegni ricavati dal 3D su PostgreSQL/PostGIS, in uno
schema temporaneo di pyarchinit_test_pg (gli altri database del server non
si toccano)."""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from tests.sync.conftest_pg import PG_CONN_STR  # noqa: E402

_DDL = [
    "CREATE TABLE us_table (id_us SERIAL PRIMARY KEY, sito TEXT, area TEXT, us TEXT, "
    "unita_tipo TEXT, node_uuid TEXT, documentazione TEXT)",
    "CREATE TABLE documentazione_table (id_documentazione SERIAL PRIMARY KEY, sito TEXT, "
    "nome_doc TEXT, data TEXT, tipo_documentazione TEXT, sorgente TEXT, scala TEXT, "
    "disegnatore TEXT, note TEXT)",
]
_LAYER = ("CREATE TABLE {t} (gid INTEGER PRIMARY KEY, area_s TEXT, scavo_s TEXT, us_s TEXT, "
          "stratigraph_index_us INTEGER, tipo_us_s TEXT, rilievo_originale TEXT, disegnatore TEXT, "
          "data TEXT, tipo_doc TEXT, nome_doc TEXT, coord TEXT, unita_tipo_s TEXT, "
          "the_geom geometry(MultiPolygon, {srid}))")
_VISTA = ("CREATE VIEW pyarchinit_usm_view AS SELECT a.gid, a.tipo_doc, a.nome_doc, a.the_geom, "
          "b.sito, b.area, b.us FROM pyunitastratigrafiche_usm a JOIN us_table b "
          "ON (a.area_s = b.area AND a.scavo_s = b.sito AND a.us_s = b.us)")


@pytest.fixture
def pg_schema():
    from sqlalchemy import create_engine, text
    nome = "drw_" + uuid.uuid4().hex[:8]
    base = create_engine(PG_CONN_STR)
    try:
        with base.begin() as conn:
            conn.execute(text("CREATE SCHEMA %s" % nome))
            # PostGIS, se manca, dentro lo schema del test: in public
            # pyarchinit_test_pg ha già una spatial_ref_sys copiata da SQLite,
            # e con lo schema se ne va anche l'estensione.
            if conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'postgis'")).scalar() is None:
                conn.execute(text("CREATE EXTENSION postgis SCHEMA %s" % nome))
    except Exception as e:                              # noqa: BLE001
        pytest.skip("PostGIS non disponibile su pyarchinit_test_pg: %s" % e)
    eng = create_engine(PG_CONN_STR, connect_args={"options": "-csearch_path=%s,public" % nome})
    with eng.begin() as conn:
        for ddl in _DDL:
            conn.execute(text(ddl))
        for t in ("pyunitastratigrafiche", "pyunitastratigrafiche_usm"):
            conn.execute(text(_LAYER.format(t=t, srid=31700)))
        conn.execute(text(_VISTA))
    yield eng
    eng.dispose()
    with base.begin() as conn:
        conn.execute(text("DROP SCHEMA %s CASCADE" % nome))
    base.dispose()


def test_su_postgis_si_scrive_e_si_richiama_insieme(pg_schema, tmp_path):
    from sqlalchemy import text
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy.sync import em_drawings_import as edi
    from tests.sync.test_em_drawings_import import SITO, make_project
    p = make_project(tmp_path)                          # l'em.json e i GLB; le schede qui sotto
    with pg_schema.begin() as conn:
        for nid, us in (("u1", "001"), ("u2", "002")):
            conn.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, node_uuid, documentazione) "
                              "VALUES (:s, '1', :u, 'US', :n, '[]')"), {"s": SITO, "u": us, "n": nid})
    unita = edi.plan_units(p["grafo"], str(p["em"]), db=pg_schema, sito=SITO)
    geo = drw.georef_of(p["grafo"])
    scelta = edi.default_choice(unita, geo)
    decisione = edi.crs_decision(pg_schema, geo, scelta)
    assert decisione.kind == "ok"
    esito = edi.run_drawings(pg_schema, p["grafo"], SITO, str(p["em"]), units=unita, choice=scelta,
                             georef=geo, decision=decisione, lang="it")
    assert (esito.plans, esito.side_views, esito.unit_views) == (2, 4, 2)
    with pg_schema.connect() as conn:
        righe = conn.execute(text("SELECT us FROM pyarchinit_usm_view WHERE sito = :s AND "
                                  "nome_doc = '3D-PRO-N' AND tipo_doc = 'Prospetto'"), {"s": SITO}).fetchall()
        assert sorted(r[0] for r in righe) == ["001", "002"]
        assert conn.execute(text("SELECT ST_SRID(the_geom) FROM pyunitastratigrafiche LIMIT 1")).scalar() == 31700
    esito2 = edi.run_drawings(pg_schema, p["grafo"], SITO, str(p["em"]), units=unita, choice=scelta,
                              georef=geo, decision=decisione, lang="it")
    assert esito2.removed == 2 + 8 + 2
