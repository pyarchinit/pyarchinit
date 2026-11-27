"""Excavation plans to a room and back (room_plans, s3Dgraphy#44).

Measured on the dev-stack (27 Nov 2026), sample site: 57 plans (501 polygons
of 37 units, US and USM layers), 56 sent — one is drawn on USM 0, a unit the
records do not have — pulled into an empty SQLite and an empty PostGIS
database: 56/56 identical, a second pull 56 «same», the compare clean, the
catalogue never a us_table row, the 150 photos unaffected.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from modules.stratigraph import room_plans as RP

FIXTURE = Path(__file__).parent / "fixtures" / "mini_volterra.sqlite"
SITE = "TestSite"


def _db(tmp_path, polygons):
    """The fixture with ``(layer, area, us, date, wkt)`` drawn."""
    from sqlalchemy import text
    from modules.stratigraph.room_geometry import _engine
    db = tmp_path / "v.sqlite"
    shutil.copy(FIXTURE, db)
    url = f"sqlite:///{db}"
    with _engine(url).begin() as c:
        for layer, area, us, date, wkt in polygons:
            c.execute(text(f"INSERT INTO {layer} (scavo_s, area_s, us_s, data, tipo_us_s, the_geom) "
                           "VALUES (:s, :a, :u, :d, 'positive', CastToMulti(GeomFromText(:w, -1)))"),
                      {"s": SITE, "a": area, "u": us, "d": date, "w": wkt})
    return url


def _emjson(tmp_path, units, footprint_on=None):
    nodes = [{"id": f"n{us}", "node_type": "US", "name": f"1.US{us}",
              "data": {"node_uuid": f"uuid-{us}", "area": "1", "us": us, "unita_tipo": tipo}}
             for us, tipo in units]
    nodes.append({"id": "site", "node_type": "LocationNodeGroup", "name": SITE})
    edges = []
    if footprint_on:
        nodes.append({"id": "fp", "node_type": "property", "data": {"property_type": "footprint"}})
        edges.append({"id": "e", "edge_type": "has_property", "source": f"n{footprint_on}", "target": "fp"})
    path = tmp_path / "site.em.json"
    path.write_text(json.dumps({"graphs": {"g": {"nodes": nodes, "edges": edges}}}))
    return str(path)


SQ = "POLYGON ((0 0, 2 0, 2 2, 0 2, 0 0))"
SQ2 = "POLYGON ((5 5, 6 5, 6 6, 5 6, 5 5))"


def test_one_plan_per_unit_and_date_with_its_catalogue(tmp_path):
    url = _db(tmp_path, [("pyunitastratigrafiche", "1", "1", "2012-03-29", SQ),
                         ("pyunitastratigrafiche", "1", "1", "2012-03-29", SQ2),
                         ("pyunitastratigrafiche", "1", "1", "2012-04-02", SQ),
                         ("pyunitastratigrafiche", "1", "2", "2012-03-29", SQ),     # a cut: its footprint goes
                         ("pyunitastratigrafiche", "1", "9", "2012-03-29", SQ)])    # no such unit
    em = _emjson(tmp_path, [("1", "US"), ("2", "US")], footprint_on="2")
    report = RP.add_plan_resources(em, url, SITE, str(tmp_path / "w"))
    assert report == {"plans": 2, "units": 1, "skipped_units_with_footprint": 1,
                      "unmatched": ["pyunitastratigrafiche 1.9"]}
    g = json.loads(Path(em).read_text())["graphs"]["g"]
    kinds = {}
    for n in g["nodes"]:
        kinds.setdefault(n["node_type"], []).append(n)
    (catalogue,) = kinds["document"]
    assert catalogue["data"]["pyarchinit_plans"] and catalogue["id"] == RP.catalogue_id("site")
    assert len(kinds["representation_model_doc"]) == 2 and len(kinds["resource"]) == 2
    links = {(e["source"], e["edge_type"], e["target"]) for e in g["edges"]}
    for rm in kinds["representation_model_doc"]:
        (res,) = [t for s, k, t in links if s == rm["id"] and k == "has_linked_resource"]
        assert (catalogue["id"], "has_representation_model_doc", rm["id"]) in links
        assert ("n1", "has_linked_resource", res) in links            # the unit reaches its plan
    first = next(r for r in kinds["resource"] if r["data"]["pyarchinit_plan"]["date"] == "2012-03-29")
    text_ = Path(first["data"]["url"]).read_text()
    collection = json.loads(text_)
    assert collection["type"] == "FeatureCollection" and len(collection["features"]) == 2
    assert first["data"]["feature_count"] == 2 and first["data"]["media_type"] == "application/geo+json"
    # the same plan is the same bytes: uploaded once
    em2 = _emjson(tmp_path, [("1", "US"), ("2", "US")], footprint_on="2")
    RP.add_plan_resources(em2, url, SITE, str(tmp_path / "w2"))
    again = next(n for n in json.loads(Path(em2).read_text())["graphs"]["g"]["nodes"] if n["id"] == first["id"])
    assert again["data"]["checksum"] == first["data"]["checksum"]


def test_pulled_where_nothing_is_drawn_never_over_a_local_drawing(tmp_path, monkeypatch):
    (tmp_path / "a").mkdir()
    src = _db(tmp_path / "a", [("pyunitastratigrafiche", "1", "1", "2012-03-29", SQ),
               ("pyunitastratigrafiche", "1", "2", "2012-03-29", SQ)])
    em = _emjson(tmp_path / "a", [("1", "US"), ("2", "US")])
    RP.add_plan_resources(em, src, SITE, str(tmp_path / "a" / "w"))
    nodes = json.loads(Path(em).read_text())["graphs"]["g"]["nodes"]
    files = {}
    room_nodes = []
    for n in nodes:
        if n["node_type"] == "resource":
            files[n["id"]] = n["data"]["url"]
            n = dict(n, data=dict(n["data"], url=f"/v1/rooms/r/assets/{n['id']}"))
        room_nodes.append(SimpleNamespace(node_id=n["id"], node_type=n["node_type"], data=n.get("data") or {}))
    graph = SimpleNamespace(nodes=room_nodes, edges=[])
    def fake_download(url, token, target):                 # the room's store, here
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        return shutil.copy(files[url.rsplit("/", 1)[-1]], target)
    monkeypatch.setattr("modules.stratigraph.room_media.download", fake_download)
    dst_dir = tmp_path / "b"
    dst_dir.mkdir()
    dst = _db(dst_dir, [("pyunitastratigrafiche", "1", "2", "2012-03-29", SQ2)])   # US 2 drawn otherwise here
    kw = dict(node="https://node.test/em", room="r", token="t", home=str(tmp_path / "home"))
    dry = RP.pull_plans(dst, SITE, graph, dry_run=True, **kw)
    assert dry["plans"] == 2 and not dry["skipped"], dry
    assert (dry["written"], dry["kept_local"]) == (1, ["pyunitastratigrafiche 1.2 2012-03-29"])
    done = RP.pull_plans(dst, SITE, graph, **kw)
    assert (done["written"], done["features"]) == (1, 1)
    again = RP.pull_plans(dst, SITE, graph, **kw)
    assert (again["written"], again["same"], len(again["kept_local"])) == (0, 1, 1)
    assert {(p["us"], len(p["features"])) for p in RP.read_plans(dst, SITE)} == {("1", 1), ("2", 1)}


def test_the_union_does_not_depend_on_the_order_of_an_invalid_part():
    from osgeo import ogr
    parts = [ogr.CreateGeometryFromWkt(w) for w in (
        "POLYGON ((0 0, 4 0, 4 4, 0 4, 0 0))",
        "POLYGON ((3 3, 6 6, 6 3, 3 6, 3 3))",                       # a bow tie
        "POLYGON ((5 0, 7 0, 7 2, 5 2, 5 0))")]
    a, b = RP.union_of(parts), RP.union_of(list(reversed(parts)))
    assert a.SymDifference(b).GetArea() < 1e-9


def test_the_catalogue_and_the_plans_never_become_records():
    from modules.s3dgraphy.sync.graph_ingestor import footprint_chain_ids
    nodes = [SimpleNamespace(node_id="d", data={"pyarchinit_plans": True}),
             SimpleNamespace(node_id="m", data={"pyarchinit_plan": {"us": "1"}}),
             SimpleNamespace(node_id="u", data={"node_uuid": "x", "us": "1"})]
    assert footprint_chain_ids(SimpleNamespace(nodes=nodes, edges=[])) == {"d", "m"}


def test_a_plan_resource_is_not_a_medium():
    assert RP.is_plan({"data": {"pyarchinit_plan": {"us": "1"}}})
    assert not RP.is_plan(SimpleNamespace(data={"url": "x.jpg"}))
