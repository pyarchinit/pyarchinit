"""The excavation plans of a site, to a StratiGraph room and back.

The shape E.D. chose (s3Dgraphy#44, 27 Nov 2026): the polygons of the
POSITIVE units drawn in QGIS are documentation, not the unit's geometry (that
is its 3D proxy). So:

* ONE document per site, the «excavation plans» catalogue
  (``spatial_documentation`` / ``cartography``, as s3dgraphy.gis.document);
* each PLAN — the polygons drawn for one unit on one date, in one layer — is a
  ``representation_model_doc`` of that document;
* its geometry is a FILE, GeoJSON with its CRS, one per plan, which s3dgraphy's
  room import uploads to the room's store like the photos: the graph only
  carries the node, its links and the file's address::

      Document ──has_representation_model_doc──▶ RMDoc ──has_linked_resource──▶ Resource (.geojson)
      unit ─────────────────────────────────────────────has_linked_resource──▶ the same Resource

  (the unit reaches its plan through the resource, the link its photos use:
  the datamodel has no edge between a unit and an RMDoc.)

The polygons of a unit that already travels with a ``footprint`` (a cut) are
not plans: that footprint is its geometry, and goes as before.

**Back.** A plan whose unit, date and layer have no polygons here is
downloaded and written into the layer, in the layer's CRS; one already drawn
here — same shape or not — is never touched (a different drawing is reported).

Qt-free. The layers: ``pyunitastratigrafiche`` (US) and
``pyunitastratigrafiche_usm`` (USM), same columns on SpatiaLite and PostGIS.
"""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from typing import Any, Dict, List, Optional, Tuple

#: the layers of unit polygons, and the unit types each one draws
LAYERS = {"pyunitastratigrafiche": None, "pyunitastratigrafiche_usm": "USM"}
#: what describes a polygon, kept in the GeoJSON's properties (the key columns
#: scavo_s / area_s / us_s / data are the plan's, written on every feature too)
PROPERTIES = ("scavo_s", "area_s", "us_s", "data", "stratigraph_index_us", "tipo_us_s",
              "unita_tipo_s", "disegnatore", "tipo_doc", "nome_doc", "rilievo_originale", "coord")
_NS = uuid.UUID("6f1f6a7e-27b1-4c2e-9d39-5b3c7ac0a044")


def _ids(unit_uuid: str, layer: str, date: str) -> Dict[str, str]:
    key = f"{unit_uuid}|{layer}|{date}"
    return {"rmdoc": str(uuid.uuid5(_NS, key + "|rmdoc")),
            "resource": str(uuid.uuid5(_NS, key + "|geojson"))}


def catalogue_id(site_identity: str) -> str:
    return str(uuid.uuid5(_NS, f"{site_identity}|excavation-plans"))


def is_plan(node: Any) -> bool:
    data = node.get("data") if isinstance(node, dict) else getattr(node, "data", None)
    return bool((data or {}).get("pyarchinit_plan"))


def _graphs(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    graphs = doc.get("graphs") or {}
    return list(graphs.values()) if isinstance(graphs, dict) else list(graphs)


def _with_footprint(graph: Dict[str, Any]) -> set:
    """Units that already travel with a footprint (cuts)."""
    kinds = {n["id"]: (n.get("data") or {}).get("property_type") for n in graph.get("nodes") or []
             if n.get("node_type") == "property"}
    return {e["source"] for e in graph.get("edges") or []
            if e.get("edge_type") == "has_property" and kinds.get(e.get("target")) == "footprint"}


def _crs_of(conn, dialect: str, table: str) -> Optional[int]:
    from .room_geometry import _layer_info
    srid, _multi = _layer_info(conn, dialect, table)
    return srid if srid and srid > 0 else None


def _date(value: Any) -> str:
    return "" if value is None else str(value).strip()


def read_plans(connection_url: str, site: str) -> List[Dict[str, Any]]:
    """The site's plans in the local layers: ``{layer, area, us, date, srid,
    features: [GeoJSON feature]}``, features in a stable order."""
    from sqlalchemy import inspect, text
    from osgeo import ogr
    from .room_geometry import _engine
    engine = _engine(connection_url)
    dialect = engine.dialect.name
    as_wkb = "ST_AsBinary" if dialect == "postgresql" else "AsBinary"
    tables = set(inspect(engine).get_table_names())
    groups: Dict[Tuple[str, str, str, str], Dict[str, Any]] = {}
    with engine.connect() as conn:
        for layer in LAYERS:
            if layer not in tables:
                continue
            have = {c["name"] for c in inspect(conn).get_columns(layer)}
            if not {"scavo_s", "area_s", "us_s", "the_geom"} <= have:
                continue
            cols = [c for c in PROPERTIES if c in have]
            srid = _crs_of(conn, dialect, layer)
            rows = conn.execute(text(
                f'SELECT {", ".join(chr(34) + c + chr(34) for c in cols)}, {as_wkb}(the_geom) '
                f'FROM "{layer}" WHERE scavo_s = :s AND the_geom IS NOT NULL'), {"s": site})
            for row in rows:
                props = {c: (None if v is None else str(v)) for c, v in zip(cols, row[:-1])}
                geom = ogr.CreateGeometryFromWkb(bytes(row[-1])) if row[-1] is not None else None
                if geom is None:
                    continue
                key = (layer, str(props.get("area_s") or ""), str(props.get("us_s") or ""),
                       _date(props.get("data")))
                slot = groups.setdefault(key, {"layer": layer, "area": key[1], "us": key[2],
                                               "date": key[3], "srid": srid, "features": []})
                slot["features"].append({"type": "Feature", "properties": props,
                                         "geometry": json.loads(geom.ExportToJson())})
    for slot in groups.values():
        slot["features"].sort(key=lambda f: json.dumps(f, sort_keys=True))
    return [groups[k] for k in sorted(groups)]


def geojson_text(plan: Dict[str, Any]) -> str:
    """The plan as a GeoJSON FeatureCollection with its CRS (the named-CRS
    member GDAL and QGIS read), byte-identical for the same plan."""
    doc: Dict[str, Any] = {"type": "FeatureCollection", "name": f"{plan['layer']} {plan['area']}.{plan['us']} {plan['date']}".strip(),
                           "features": plan["features"]}
    if plan.get("srid"):
        doc["crs"] = {"type": "name", "properties": {"name": f"urn:ogc:def:crs:EPSG::{plan['srid']}"}}
    return json.dumps(doc, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def add_plan_resources(em_json: str, connection_url: str, site: str, workdir: str) -> Dict[str, Any]:
    """Write the site's plans into the exported em.json, in place (the files
    into ``workdir/plans``). → ``{plans, units, skipped_units_with_footprint,
    unmatched}``."""
    from s3dgraphy.geometry.transform import identity
    report = {"plans": 0, "units": 0, "skipped_units_with_footprint": 0, "unmatched": []}
    plans = read_plans(connection_url, site)
    if not plans:
        return report
    with open(em_json, encoding="utf-8") as fh:
        doc = json.load(fh)
    graph = _graphs(doc)[0]
    nodes = graph.setdefault("nodes", [])
    edges = graph.setdefault("edges", [])
    units: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    site_identity = site
    for n in nodes:
        d = n.get("data") or {}
        if d.get("node_uuid") and d.get("us") is not None:
            units.setdefault((str(d.get("area") or ""), str(d.get("us"))), []).append(n)
        if n.get("node_type") == "LocationNodeGroup" and str(n.get("name") or "") == site:
            site_identity = n["id"]
    cut = _with_footprint(graph)
    existing = {n["id"] for n in nodes}
    seen_edges = {e.get("id") for e in edges}
    out_dir = os.path.join(workdir, "plans")
    os.makedirs(out_dir, exist_ok=True)
    doc_id = catalogue_id(site_identity)
    touched = set()

    def edge(source, kind, target):
        eid = f"{source}__{kind}__{target}"
        if eid not in seen_edges:
            edges.append({"id": eid, "edge_type": kind, "source": source, "target": target})
            seen_edges.add(eid)

    for plan in plans:
        candidates = units.get((plan["area"], plan["us"])) or []
        wanted = LAYERS[plan["layer"]]
        unit = next((u for u in candidates if wanted and (u.get("data") or {}).get("unita_tipo") == wanted), None) \
            or next((u for u in candidates if not wanted and (u.get("data") or {}).get("unita_tipo") != "USM"), None) \
            or (candidates[0] if len(candidates) == 1 else None)
        if unit is None:
            report["unmatched"].append(f"{plan['layer']} {plan['area']}.{plan['us']}")
            continue
        if unit["id"] in cut:
            report["skipped_units_with_footprint"] += 1
            continue
        if doc_id not in existing:
            nodes.append({"id": doc_id, "node_type": "document",
                          "name": f"Piante di scavo · {site}",
                          "description": "The excavation plans drawn in pyArchInit's unit layers",
                          "data": {"document_type": "spatial_documentation",
                                   "document_subtype": "cartography", "pyarchinit_plans": True}})
            existing.add(doc_id)
        uuid_ = str((unit.get("data") or {}).get("node_uuid"))
        ids = _ids(uuid_, plan["layer"], plan["date"])
        text_ = geojson_text(plan)
        path = os.path.join(out_dir, ids["resource"] + ".geojson")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text_)
        raw = text_.encode("utf-8")
        label = f"{unit.get('name') or plan['us']} · {plan['date'] or 's.d.'}"
        meta = {"layer": plan["layer"], "area": plan["area"], "us": plan["us"], "date": plan["date"],
                "unit": uuid_, "features": len(plan["features"])}
        if ids["resource"] not in existing:
            nodes.append({"id": ids["resource"], "node_type": "resource",
                          "name": os.path.basename(path),
                          "data": {"url": path, "url_type": "gis_layer", "packaging": "file",
                                   "checksum": "sha256:" + hashlib.sha256(raw).hexdigest(),
                                   "size_bytes": len(raw), "media_type": "application/geo+json",
                                   "gis_format": "geojson",
                                   "crs": f"EPSG:{plan['srid']}" if plan.get("srid") else None,
                                   "feature_count": len(plan["features"]),
                                   "pyarchinit_plan": meta}})
            existing.add(ids["resource"])
        if ids["rmdoc"] not in existing:
            nodes.append({"id": ids["rmdoc"], "node_type": "representation_model_doc",
                          "name": f"Pianta {label}",
                          "description": f"Excavation plan of {unit.get('name')}, {plan['date'] or 'undated'}",
                          "data": {"transform": identity(), "geometry": "reality_based",
                                   "pyarchinit_plan": meta}})
            existing.add(ids["rmdoc"])
        edge(doc_id, "has_representation_model_doc", ids["rmdoc"])
        edge(ids["rmdoc"], "has_linked_resource", ids["resource"])
        edge(unit["id"], "has_linked_resource", ids["resource"])
        report["plans"] += 1
        touched.add(unit["id"])
    report["units"] = len(touched)
    with open(em_json, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False)
    return report


# ── from the room ────────────────────────────────────────────────────────────

def plans_in(graph) -> List[Dict[str, Any]]:
    """The room's plans: ``{resource, url, layer, area, us, date}``."""
    out = []
    for n in getattr(graph, "nodes", None) or []:
        data = getattr(n, "data", None) or {}
        meta = data.get("pyarchinit_plan")
        if getattr(n, "node_type", "") == "resource" and isinstance(meta, dict):
            out.append({"resource": str(n.node_id), "url": data.get("url"), **meta})
    return out


def _valid(g):
    """A geometry fit for a union, for COMPARING only (what is written stays
    as drawn): one self-intersecting polygon made the union depend on the
    order of the parts — 0.70 m² one way, 1.47 m² the other, on US 5 of the
    sample site (27 Nov 2026)."""
    if g is not None and not g.IsValid() and hasattr(g, "MakeValid"):
        fixed = g.MakeValid()
        if fixed is not None:
            return fixed
    return g


def union_of(geoms):
    union = None
    for g in geoms:
        g = _valid(g)
        if g is None:
            continue
        union = g if union is None else union.Union(g)
    return union


def _in_layer(g, source: Optional[int], target: Optional[int], multi: bool):
    """The geometry in the layer's CRS, single or multi like the layer — the
    OGR object itself, never through WKT: WKT keeps 15 significant digits and
    coordinates in metres of a national grid have 16 (2324922.185450377): a
    45 cm² plan (US 26) came back «different» from its own source (27 Nov)."""
    from osgeo import ogr, osr
    g = g.Clone()
    if source and target and source != target:
        src, dst = osr.SpatialReference(), osr.SpatialReference()
        src.ImportFromEPSG(source)
        dst.ImportFromEPSG(target)
        for ref in (src, dst):
            if hasattr(ref, "SetAxisMappingStrategy"):
                ref.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        g.Transform(osr.CoordinateTransformation(src, dst))
    if multi:
        g = ogr.ForceToMultiPolygon(g)
    elif g.GetGeometryType() in (ogr.wkbMultiPolygon, ogr.wkbMultiPolygon25D) and g.GetGeometryCount() == 1:
        g = g.GetGeometryRef(0).Clone()
    return g


def _union(features: List[Dict[str, Any]], target: Optional[int], source: Optional[int]):
    from osgeo import ogr
    parts = []
    for f in features:
        g = ogr.CreateGeometryFromJson(json.dumps(f["geometry"]))
        if g is not None:
            parts.append(_in_layer(g, source, target, False))
    return union_of(parts)


def _crs_in(collection: Dict[str, Any]) -> Optional[int]:
    name = str(((collection.get("crs") or {}).get("properties") or {}).get("name") or "")
    tail = name.rsplit(":", 1)[-1]
    return int(tail) if tail.isdigit() else None


def pull_plans(connection_url: str, site: str, graph, *, node: str, room: str, token: str,
               home: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
    """The room's plans into the unit layers (see the module): written where
    the unit has nothing drawn on that date, never over a local drawing."""
    from sqlalchemy import inspect, text
    from .node_client import node_base
    from .room_geometry import _engine, _layer_info, _same
    from .room_media import _safe, download

    report = {"plans": 0, "written": 0, "features": 0, "same": 0, "kept_local": [],
              "skipped": [], "dry_run": dry_run}
    found = plans_in(graph)
    report["plans"] = len(found)
    if not found:
        return report
    try:
        from osgeo import ogr
    except ImportError:                                      # pragma: no cover
        report["skipped"].append("GDAL/OGR not available: plans not written")
        return report
    home = home or os.environ.get("PYARCHINIT_HOME") or os.path.join(os.path.expanduser("~"), "pyarchinit_5")
    cache = os.path.join(home, "stratigraph_plans", _safe(room))
    engine = _engine(connection_url)
    dialect = engine.dialect.name
    # written as WKB: exact, as read (WKT would round the 16th digit)
    geom_from = "ST_GeomFromWKB" if dialect == "postgresql" else "GeomFromWKB"
    as_wkb = "ST_AsBinary" if dialect == "postgresql" else "AsBinary"
    tables = set(inspect(engine).get_table_names())
    base = node_base(node)
    with engine.begin() as conn:
        for p in found:
            layer = p.get("layer")
            label = f"{layer} {p.get('area')}.{p.get('us')} {p.get('date')}"
            if layer not in LAYERS or layer not in tables:
                report["skipped"].append(f"{label}: no such layer here")
                continue
            have = {c["name"] for c in inspect(conn).get_columns(layer)}
            srid, multi = _layer_info(conn, dialect, layer)
            srid = srid if srid and srid > 0 else None
            date_sql = "data IS NULL" if not p.get("date") else "CAST(data AS TEXT) = :d"
            key = {"s": site, "a": str(p.get("area")), "u": str(p.get("us")), "d": str(p.get("date") or "")}
            here = [r[0] for r in conn.execute(text(
                f'SELECT {as_wkb}(the_geom) FROM "{layer}" '
                f'WHERE scavo_s = :s AND area_s = :a AND us_s = :u AND {date_sql}'), key)]
            url = str(p.get("url") or "")
            if url.startswith("/"):
                url = base + url
            if not url.startswith("http"):
                report["skipped"].append(f"{label}: not in the room's store")
                continue
            target = os.path.join(cache, p["resource"] + ".geojson")
            try:
                if not os.path.exists(target):
                    download(url, token, target)
                with open(target, encoding="utf-8") as fh:
                    collection = json.load(fh)
            except Exception as e:  # noqa: BLE001
                report["skipped"].append(f"{label}: {type(e).__name__}: {e}")
                continue
            features = collection.get("features") or []
            source = _crs_in(collection)
            if here:
                # both unions in OGR: SpatiaLite's GUnion and GEOS through OGR
                # disagree slightly on overlapping polygons (27 Nov 2026)
                local = union_of(ogr.CreateGeometryFromWkb(bytes(w)) for w in here if w is not None)
                room_shape = _union(features, srid, source)
                if local is not None and room_shape is not None and _same(local.ExportToWkb(), room_shape):
                    report["same"] += 1
                else:
                    report["kept_local"].append(label)
                continue
            if dry_run:
                report["written"] += 1
                report["features"] += len(features)
                continue
            for f in features:
                g = ogr.CreateGeometryFromJson(json.dumps(f["geometry"]))
                if g is None:
                    continue
                g = _in_layer(g, source, srid, multi)
                props = {c: v for c, v in (f.get("properties") or {}).items() if c in have and c != "the_geom"}
                props.update({"scavo_s": site, "area_s": str(p.get("area")), "us_s": str(p.get("us"))})
                if "stratigraph_index_us" in props and props["stratigraph_index_us"] not in (None, ""):
                    try:
                        props["stratigraph_index_us"] = int(float(props["stratigraph_index_us"]))
                    except ValueError:
                        props["stratigraph_index_us"] = None
                cols = list(props)
                params = dict(props, wkb=bytes(g.ExportToIsoWkb() if dialect == "postgresql" else g.ExportToWkb()),
                              srid=srid or source or -1)
                conn.execute(text(
                    f'INSERT INTO "{layer}" ({", ".join(chr(34) + c + chr(34) for c in cols)}, the_geom) '
                    f'VALUES ({", ".join(":" + c for c in cols)}, {geom_from}(:wkb, :srid))'), params)
                report["features"] += 1
            report["written"] += 1
    return report
