"""Le sezioni dal 3D su PostgreSQL/PostGIS, nello schema temporaneo del primo
pezzo (pyarchinit_test_pg; gli altri database del server non si toccano)."""
from __future__ import annotations

import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from tests.sync.test_em_drawings_import_pg import pg_schema  # noqa: E402,F401


def test_su_postgis_la_sezione_si_scrive_e_si_lega_alla_linea(pg_schema, tmp_path):
    from sqlalchemy import text
    from modules.s3dgraphy.sync import em_sections as es
    from modules.s3dgraphy.sync.em_sources import remember_source
    from tests.sync.test_em_drawings_import import SITO, make_project
    p = make_project(tmp_path)
    with pg_schema.begin() as conn:
        for nid, us in (("u1", "001"), ("u2", "002")):
            conn.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, node_uuid, documentazione) "
                              "VALUES (:s, '1', :u, 'US', :n, '[]')"), {"s": SITO, "u": us, "n": nid})
        conn.execute(text("CREATE TABLE pyarchinit_sezioni (gid SERIAL PRIMARY KEY, id_sezione varchar(80), "
                          "sito varchar(80), area integer, descr varchar(80), "
                          "the_geom geometry(LineString, 31700), tipo_doc text, nome_doc text)"))
        conn.execute(text("INSERT INTO pyarchinit_sezioni (id_sezione, sito, area, descr, the_geom) VALUES "
                          "('A1', :s, 1, 'attraverso SU001', "
                          "ST_GeomFromText('LINESTRING(327298 448380, 327306 448380)', 31700))"), {"s": SITO})
    assert remember_source(pg_schema, SITO, str(p["em"]))
    linee, srid = es.section_lines(pg_schema, SITO)
    assert srid == 31700 and len(linee) == 1
    esito = es.run_sections(pg_schema, SITO, gids=[linee[0].gid], search_dirs=[str(p["radice"] / "EM")], lang="it")
    assert esito.sections == 1 and esito.linked == 1
    with pg_schema.connect() as conn:
        area, xmax = conn.execute(text("SELECT ST_Area(the_geom), ST_XMax(the_geom) FROM pyunitastratigrafiche_usm "
                                       "WHERE nome_doc = '3D-SEZ-A1'")).fetchone()
        assert abs(area - 12.0) < 1e-6 and xmax <= -10.0 + 1e-6
        assert conn.execute(text("SELECT tipo_doc, nome_doc FROM pyarchinit_sezioni")).fetchone() == \
            ("Sezione", "3D-SEZ-A1")
