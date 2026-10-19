"""L'import da QField su PostgreSQL/PostGIS: gli id scritti MAX + 1 non
devono lasciare indietro i contatori, o il primo record fatto dopo con l'id
di default (un poligono disegnato in QGIS, una scheda) prende un id già
usato. Schema temporaneo di pyarchinit_test_pg, che ricalca quello del
plugin (``resources/dbfiles/pyarchinit_schema_updated.sql``): id con DEFAULT
nextval, sequenze dei gid che non sono OWNED BY e partono da 61400."""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from tests.sync.conftest_pg import PG_CONN_STR  # noqa: E402

SITO = "Scavo QField"

_DDL = [
    "CREATE TABLE us_table (id_us SERIAL PRIMARY KEY, sito TEXT, area TEXT, us TEXT, unita_tipo TEXT, "
    "node_uuid TEXT, created_by TEXT)",
    "CREATE TABLE inventario_materiali_table (id_invmat SERIAL PRIMARY KEY, sito TEXT, "
    "numero_inventario INTEGER, node_uuid TEXT, created_by TEXT)",
    "CREATE SEQUENCE pyunitastratigrafiche_gid_seq START 61400",
    "CREATE TABLE pyunitastratigrafiche (gid BIGINT DEFAULT nextval('pyunitastratigrafiche_gid_seq'::regclass) "
    "NOT NULL PRIMARY KEY, area_s TEXT, scavo_s TEXT, us_s TEXT, the_geom geometry(MultiPolygon, 31700))",
    "CREATE SEQUENCE pyarchinit_quote_gid_seq START 61400",
    "CREATE TABLE pyarchinit_quote (gid BIGINT DEFAULT nextval('pyarchinit_quote_gid_seq'::regclass) "
    "NOT NULL PRIMARY KEY, sito_q TEXT, area_q TEXT, us_q TEXT, quota_q NUMERIC, the_geom geometry(Point, 31700))",
    "CREATE TABLE media_table (id_media SERIAL PRIMARY KEY, mediatype TEXT, filename TEXT, filetype TEXT, "
    "filepath TEXT, descrizione TEXT, tags TEXT)",
    'CREATE TABLE media_to_entity_table ("id_mediaToEntity" SERIAL PRIMARY KEY, id_entity INTEGER, '
    "entity_type TEXT, table_name TEXT, id_media INTEGER, filepath TEXT, media_name TEXT)",
    "CREATE TABLE media_thumb_table (id_media_thumb SERIAL PRIMARY KEY, id_media INTEGER, mediatype TEXT, "
    "media_filename TEXT, media_thumb_filename TEXT, filetype TEXT, filepath TEXT, path_resize TEXT)",
]


@pytest.fixture
def pg():
    from sqlalchemy import create_engine, text
    nome = "qf_" + uuid.uuid4().hex[:8]
    base = create_engine(PG_CONN_STR)
    try:
        with base.begin() as conn:
            conn.execute(text("CREATE SCHEMA %s" % nome))
            if conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'postgis'")).scalar() is None:
                conn.execute(text("CREATE EXTENSION postgis SCHEMA %s" % nome))
    except Exception as e:                              # noqa: BLE001
        pytest.skip("PostGIS non disponibile su pyarchinit_test_pg: %s" % e)
    eng = create_engine(PG_CONN_STR, connect_args={"options": "-csearch_path=%s,public" % nome})
    with eng.begin() as conn:
        for ddl in _DDL:
            conn.execute(text(ddl))
        # quello che c'era già: due US scritte dalla scheda (MAX + 1, il
        # contatore non si muove) e un poligono disegnato in QGIS (61400)
        conn.execute(text("INSERT INTO us_table (id_us, sito, area, us) VALUES (1, :s, '1', '1'), "
                          "(2, :s, '1', '2')"), {"s": SITO})
        conn.execute(text("INSERT INTO pyunitastratigrafiche (scavo_s, area_s, us_s) VALUES (:s, '1', '1')"),
                     {"s": SITO})
    yield eng
    eng.dispose()
    with base.begin() as conn:
        conn.execute(text("DROP SCHEMA %s CASCADE" % nome))
    base.dispose()


def _righe():
    quadrato = "MULTIPOLYGON(((327300 448370, 327301 448370, 327301 448371, 327300 448371, 327300 448370)))"
    return {
        "us_table": [{"_fid": 1, "id_us": 10, "sito": SITO, "area": "1", "us": "3", "unita_tipo": "US"},
                     {"_fid": 2, "id_us": 11, "sito": SITO, "area": "1", "us": "4", "unita_tipo": "US"}],
        "inventario_materiali_table": [{"_fid": 1, "sito": SITO, "numero_inventario": 1}],
        "pyunitastratigrafiche": [{"_fid": 1, "scavo_s": SITO, "area_s": "1", "us_s": "3",
                                   "_wkt": quadrato, "_srid": 31700}],
        "pyarchinit_quote": [{"_fid": 1, "sito_q": SITO, "area_q": "1", "us_q": "3", "quota_q": 12.5,
                              "_wkt": "POINT(327300.5 448370.5)", "_srid": 31700}],
        "media_table": [{"_fid": 1, "id_media": 1, "filepath": "DCIM/foto1.jpg", "filename": "foto1",
                         "mediatype": "image"}],
        "media_to_entity_table": [{"_fid": 1, "id_entity": 10, "id_media": 1, "entity_type": "US"}],
    }


def test_dopo_l_import_i_record_nuovi_non_trovano_doppioni(pg, tmp_path):
    from sqlalchemy import text
    from modules.utility.qfield_importer import run_qfield_import
    esito = run_qfield_import(pg, str(tmp_path), dry_run=False, copy_media=False, make_thumbs=False,
                              log=lambda *_a: None, rows_override=_righe())
    assert (esito.us.inserted, esito.geometrie.inserted, esito.quote.inserted) == (2, 1, 1)
    assert (esito.media.inserted, esito.links.inserted, esito.materiali.inserted) == (1, 1, 1)
    with pg.begin() as conn:
        # come QGIS e come chi usa l'id di default: nessun «duplicate key»
        conn.execute(text("INSERT INTO us_table (sito, area, us) VALUES (:s, '1', '5')"), {"s": SITO})
        conn.execute(text("INSERT INTO inventario_materiali_table (sito, numero_inventario) VALUES (:s, 2)"),
                     {"s": SITO})
        conn.execute(text("INSERT INTO pyunitastratigrafiche (scavo_s, area_s, us_s) VALUES (:s, '1', '9')"),
                     {"s": SITO})
        conn.execute(text("INSERT INTO pyarchinit_quote (sito_q, quota_q) VALUES (:s, 1)"), {"s": SITO})
        conn.execute(text("INSERT INTO media_table (filename) VALUES ('foto2')"))
        conn.execute(text("INSERT INTO media_to_entity_table (id_entity, id_media) VALUES (1, 1)"))
        massimi = conn.execute(text("SELECT (SELECT MAX(id_us) FROM us_table), "
                                    "(SELECT MAX(gid) FROM pyunitastratigrafiche)")).fetchone()
    assert tuple(massimi) == (5, 61402)


def test_le_miniature_non_lasciano_indietro_il_contatore(pg, tmp_path):
    from sqlalchemy import text
    from modules.utility import qfield_importer as qi
    with pg.begin() as conn:
        conn.execute(text("INSERT INTO media_thumb_table (id_media_thumb, id_media) VALUES (1, 1)"))
    esito = qi.QFieldImportResult()
    qi.make_thumbnails(pg, [{"id_media": 7, "filepath": "a.jpg", "filename": "a"}], "/tmp/t", "/tmp/r",
                       esito, lambda *_a: None, resampler=lambda *a: None)
    assert esito.thumbs.inserted == 1
    with pg.begin() as conn:
        conn.execute(text("INSERT INTO media_thumb_table (id_media) VALUES (8)"))
        assert conn.execute(text("SELECT MAX(id_media_thumb) FROM media_thumb_table")).scalar() == 3


# ------------------------------------------- seconda revisione (19 ottobre 2026)

def test_un_contatore_che_resta_indietro_si_dice(pg, tmp_path, monkeypatch):
    from modules.utility import db_sequences as dbs
    from modules.utility.qfield_importer import run_qfield_import
    vero = dbs.sync_sequence_state
    monkeypatch.setattr(dbs, "sync_sequence_state",
                        lambda conn, t, c: "failed" if t == "us_table" else vero(conn, t, c))
    righe = []
    esito = run_qfield_import(pg, str(tmp_path), dry_run=False, copy_media=False, make_thumbs=False,
                              log=righe.append, rows_override=_righe())
    assert any("us_table" in w and "contatore" in w for w in esito.warnings)
    assert any("us_table" in r and "contatore" in r for r in righe)


def test_nessun_avviso_nel_log_per_le_colonne_che_non_ci_sono(pg, tmp_path, caplog):
    import logging
    from modules.utility.qfield_importer import run_qfield_import
    with caplog.at_level(logging.WARNING):
        run_qfield_import(pg, str(tmp_path), dry_run=False, copy_media=False, make_thumbs=False,
                          log=lambda *_a: None, rows_override=_righe())
    assert not [r for r in caplog.records if r.name.endswith("db_sequences")]
