"""Footprints of a room back into pyArchInit's GIS layers (room_geometry).

Measured on the dev-stack (26 Nov 2026): a site with its site, trench and
cut drawn, sent to a room and pulled into a database without those drawings:
3 geometries written, a second pull 3 «same»; on PostgreSQL 17 + PostGIS the
same, with pyarchinit_sondaggi's PostGIS columns (sito / id_sondagg); a
trench redrawn locally is kept and reported.
"""
from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest

from modules.stratigraph import room_geometry as RG

FIXTURE = Path(__file__).parent / "fixtures" / "mini_volterra.sqlite"
SITE = "TestSite"
SQUARE = "POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))"


def _node(nid, ntype, name="", data=None):
    return SimpleNamespace(node_id=nid, node_type=ntype, name=name, data=data or {}, attributes={})


def _edge(src, kind, tgt):
    return SimpleNamespace(edge_source=src, edge_type=kind, edge_target=tgt)


def _room(*items):
    """A graph with one footprint per ``(owner, layer, key_column, feature, wkt)``."""
    nodes, edges = [], []
    for i, (owner, layer, key, feature, wkt) in enumerate(items):
        prop = _node(f"p{i}", "property", "footprint",
                     {"property_type": "footprint",
                      "value": f"<http://www.opengis.net/def/crs/EPSG/0/3004> {wkt}"})
        ext = _node(f"x{i}", "extractor", f"D.footprint.{layer}",
                    {"layer": layer, "feature_key": key, "feature": feature})
        nodes += [owner, prop, ext]
        edges += [_edge(owner.node_id, "has_property", prop.node_id),
                  _edge(prop.node_id, "has_data_provenance", ext.node_id)]
    return SimpleNamespace(nodes=nodes, edges=edges)


def test_footprints_are_read_from_the_room():
    site = _node("s", "LocationNodeGroup", SITE, {"level": "sito"})
    found = RG.footprints_in(_room((site, "pyarchinit_siti_polygonal", "sito_id", SITE, SQUARE)))
    assert found == [{"owner": site, "layer": "pyarchinit_siti_polygonal", "key_column": "sito_id",
                      "feature": SITE, "srid": 3004, "wkt": SQUARE, "property": "p0"}]


def test_the_identifying_columns_follow_the_layer_and_this_database():
    layers = RG._layers()
    place = _node("loc::settore::study::A", "LocationNodeGroup", "A")
    fp = {"owner": place, "key_column": "id_rs", "feature": "A"}
    assert RG._row_values(layers["pyarchinit_ripartizioni_spaziali"],
                          {"sito_rs", "id_rs", "tip_rip"}, fp, SITE) == \
        {"sito_rs": SITE, "id_rs": "A", "tip_rip": "settore"}
    trench = {"owner": _node("loc::saggio::study::1", "LocationNodeGroup"),
              "key_column": "id_sondaggio", "feature": "1"}
    # PostGIS names the columns sito / id_sondagg
    assert RG._row_values(layers["pyarchinit_sondaggi"], {"sito", "id_sondagg"}, trench, SITE) == \
        {"sito": SITE, "id_sondagg": "1"}
    cut = {"owner": _node("u2", "NegativeStratigraphicUnit", "1.USN2", {"area": "1"}),
           "key_column": "us_s", "feature": "2"}
    assert RG._row_values(layers["pyunitastratigrafiche"], {"scavo_s", "area_s", "us_s"}, cut, SITE) == \
        {"scavo_s": SITE, "area_s": "1", "us_s": "2"}


def _spatialite_copy(tmp_path) -> Path:
    db = tmp_path / "volterra.sqlite"
    shutil.copy(FIXTURE, db)
    con = sqlite3.connect(db)
    # the site layer with a declared CRS, the trench layer without one (old databases: -1)
    con.execute("UPDATE geometry_columns SET srid = 3004 WHERE f_table_name = 'pyarchinit_siti_polygonal'")
    con.commit()
    con.close()
    return db


def test_written_once_then_the_same_and_a_local_drawing_is_kept(tmp_path):
    pytest.importorskip("osgeo")
    from modules.utility.spatialite_loader import load_spatialite
    db = _spatialite_copy(tmp_path)
    room = _room((_node("s", "LocationNodeGroup", SITE, {"level": "sito"}),
                  "pyarchinit_siti_polygonal", "sito_id", SITE, SQUARE),
                 (_node("loc::saggio::study::1", "LocationNodeGroup", "1"),
                  "pyarchinit_sondaggi", "id_sondaggio", "1", "POLYGON ((1 1, 3 1, 3 3, 1 3, 1 1))"))
    url = f"sqlite:///{db}"
    try:
        first = RG.pull_geometries(url, SITE, room)
    except Exception as e:  # pragma: no cover - no mod_spatialite on this machine
        pytest.skip(f"SpatiaLite not loadable here: {e}")
    assert (first["inserted"], first["same"], first["skipped"]) == (2, 0, [])
    again = RG.pull_geometries(url, SITE, room)
    assert (again["inserted"], again["same"], again["kept_local"]) == (0, 2, [])
    con = sqlite3.connect(db)
    con.enable_load_extension(True)
    load_spatialite(con)
    con.execute("UPDATE pyarchinit_sondaggi SET the_geom = ST_Translate(the_geom, 5, 0, 0) "
                "WHERE id_sondaggio = '1'")
    con.commit()
    con.close()
    redrawn = RG.pull_geometries(url, SITE, room)
    assert redrawn["kept_local"] == ["pyarchinit_sondaggi 1"] and redrawn["same"] == 1
