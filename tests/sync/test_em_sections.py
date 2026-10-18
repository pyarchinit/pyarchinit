"""Sezioni lungo le linee del layer delle sezioni, dai proxy 3D (spec
2026-10-18 sezioni, S2–S6), con il progetto finto del primo pezzo: SU001 è
una scatola 4 × 1 × 3 m attorno a X 327300–327304, Y 448379,5–448380,5."""
from __future__ import annotations

import ast
import sqlite3
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

pytest.importorskip("s3dgraphy")

from tests.sync.test_em_drawings_import import SITO, _SPATIALITE, _righe, _scrivi, make_project  # noqa: E402

LINEA = "LINESTRING(327298 448380, 327306 448380)"          # da ovest a est, a metà di SU001


def _con(db):
    con = sqlite3.connect(db)
    con.enable_load_extension(True)
    for nome in _SPATIALITE:
        try:
            con.load_extension(nome)
            break
        except sqlite3.Error:
            continue
    return con


def _righe_g(p, sql, *args):
    """Come _righe, ma con SpatiaLite caricato (AsText, Area, MbrMaxX…)."""
    con = _con(p["db"])
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


def _linea(p, wkt=LINEA, id_sezione="A1", tipo_doc=None, nome_doc=None, srid=None):
    con = _con(p["db"])
    if srid is None:
        srid = con.execute("SELECT srid FROM geometry_columns WHERE f_table_name = 'pyarchinit_sezioni'").fetchone()[0]
    gid = (con.execute("SELECT COALESCE(MAX(gid), 0) + 1 FROM pyarchinit_sezioni").fetchone()[0])
    con.execute("INSERT INTO pyarchinit_sezioni (gid, id_sezione, sito, area, descr, the_geom, tipo_doc, nome_doc) "
                "VALUES (?, ?, ?, 1, 'attraverso SU001', GeomFromText(?, ?), ?, ?)",
                (gid, id_sezione, SITO, wkt, srid, tipo_doc, nome_doc))
    con.commit()
    con.close()
    return gid


@pytest.fixture
def sezioni(tmp_path):
    from modules.s3dgraphy.sync.em_sources import remember_source
    p = make_project(tmp_path)
    assert remember_source(p["db"], SITO, str(p["em"]))
    p["cartella"] = str(p["radice"] / "EM")
    return p


def _taglia(p, gids, **kw):
    from modules.s3dgraphy.sync import em_sections as es
    return es.run_sections(p["eng"], SITO, gids=gids, search_dirs=[p["cartella"]], lang="it", **kw)


def test_le_linee_del_sito(sezioni):
    from modules.s3dgraphy.sync import em_sections as es
    gid = _linea(sezioni)
    linee, srid = es.section_lines(sezioni["eng"], SITO)
    assert srid == -1 and [(l.gid, l.id_sezione, l.segments) for l in linee] == [(gid, "A1", 1)]
    assert linee[0].length == pytest.approx(8.0)
    assert es.section_names(linee) == {gid: "3D-SEZ-A1"}


def test_una_sezione_si_scrive_e_si_richiama_insieme(sezioni):
    gid = _linea(sezioni)
    esito = _taglia(sezioni, [gid])
    assert esito.sections == 1 and esito.cut == {"3D-SEZ-A1": 1}
    righe = _righe_g(sezioni, "SELECT us_s, tipo_doc, AsText(the_geom) FROM pyunitastratigrafiche_usm "
                            "WHERE nome_doc = '3D-SEZ-A1'")
    assert [(r[0], r[1]) for r in righe] == [("001", "Sezione")]
    area, xmax = _righe_g(sezioni, "SELECT Area(the_geom), MbrMaxX(the_geom) FROM pyunitastratigrafiche_usm "
                                 "WHERE nome_doc = '3D-SEZ-A1'")[0]
    assert area == pytest.approx(12.0, abs=1e-6) and xmax == pytest.approx(-10.0)
    assert _righe(sezioni, "SELECT tipo_documentazione FROM documentazione_table WHERE nome_doc = '3D-SEZ-A1'") \
        == [("Sezione",)]
    doc = ast.literal_eval(_righe(sezioni, "SELECT documentazione FROM us_table WHERE sito = ? AND us = '001'",
                                  SITO)[0][0])
    assert ["Sezione", "3D-SEZ-A1"] in doc
    assert _righe(sezioni, "SELECT tipo_doc, nome_doc FROM pyarchinit_sezioni WHERE gid = ?", gid) \
        == [("Sezione", "3D-SEZ-A1")]
    assert "non hanno un sistema" in esito.summary()


def test_la_seconda_volta_sostituisce_e_resta_a_sinistra_dei_prospetti(sezioni):
    _scrivi(sezioni)                                     # piante e prospetti del primo pezzo, da u = 0
    gid = _linea(sezioni)
    _taglia(sezioni, [gid])
    _taglia(sezioni, [gid])
    assert _righe(sezioni, "SELECT count(*) FROM pyunitastratigrafiche_usm WHERE nome_doc = '3D-SEZ-A1'")[0][0] == 1
    assert _righe(sezioni, "SELECT count(*) FROM documentazione_table WHERE nome_doc = '3D-SEZ-A1'")[0][0] == 1
    assert _righe_g(sezioni, "SELECT MAX(MbrMaxX(the_geom)) FROM pyunitastratigrafiche_usm "
                           "WHERE nome_doc LIKE '3D-SEZ-%'")[0][0] < 0
    assert _righe_g(sezioni, "SELECT MIN(MbrMinX(the_geom)) FROM pyunitastratigrafiche_usm "
                           "WHERE nome_doc LIKE '3D-PRO-%'")[0][0] >= -1e-6


def test_la_linea_con_un_altro_documento_non_si_tocca(sezioni):
    gid = _linea(sezioni, tipo_doc="Sezione", nome_doc="S1")
    esito = _taglia(sezioni, [gid])
    assert _righe(sezioni, "SELECT tipo_doc, nome_doc FROM pyarchinit_sezioni WHERE gid = ?", gid) \
        == [("Sezione", "S1")]
    assert "S1" in esito.summary()


def test_le_linee_in_un_altro_sistema_si_convertono(sezioni):
    from qgis.core import (QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsGeometry,
                           QgsProject)
    con = sqlite3.connect(sezioni["db"])
    con.execute("UPDATE geometry_columns SET srid = 3004 WHERE f_table_name = 'pyarchinit_sezioni'")
    con.commit()
    con.close()
    g = QgsGeometry.fromWkt(LINEA)
    g.transform(QgsCoordinateTransform(QgsCoordinateReferenceSystem.fromEpsgId(31700),
                                       QgsCoordinateReferenceSystem.fromEpsgId(3004), QgsProject.instance()))
    gid = _linea(sezioni, wkt=g.asWkt(6), srid=3004)
    _taglia(sezioni, [gid])
    area = _righe_g(sezioni, "SELECT Area(the_geom) FROM pyunitastratigrafiche_usm WHERE nome_doc = '3D-SEZ-A1'")[0][0]
    assert area == pytest.approx(12.0, abs=0.05)


def test_senza_em_json_o_senza_linee_si_dice(tmp_path):
    from modules.s3dgraphy.sync import em_sections as es
    p = make_project(tmp_path)
    with pytest.raises(es.SectionsError, match="em.json"):
        es.run_sections(p["eng"], SITO, gids=[1])
    from modules.s3dgraphy.sync.em_sources import remember_source
    remember_source(p["db"], SITO, str(p["em"]))
    with pytest.raises(es.SectionsError, match="nessuna linea"):
        es.run_sections(p["eng"], SITO, gids=[])
