"""The footprints of a room back into pyArchInit's GIS layers.

What goes TO a room (s3dgraphy's footprint reader, decided with E.D. on
11 Nov 2026): the site (``pyarchinit_siti_polygonal``), its places — trenches
(``pyarchinit_sondaggi``), areas / sectors (``pyarchinit_ripartizioni_spaziali``)
— and the negative units (cuts, ``pyunitastratigrafiche``), each as a
``footprint`` property: ``"<CRS URI> WKT"``, with an extractor naming the layer,
the key column and the feature it was read from. Positive units' polygons are
not sent (s3dgraphy treats their geometry as the 3D proxy).

Here, the way back: each footprint of the room is written into the same layer
of the local database, SpatiaLite or PostGIS, in the layer's own CRS
(transformed with OGR when it differs):

* the feature is missing → inserted, with its site / key / area / type columns;
* the feature is there without a geometry → the geometry is set;
* the feature is there with the same geometry → nothing to do;
* the feature is there with ANOTHER geometry → left alone and reported: a
  drawing made here is never overwritten by the pull.

Orthophotos and other rasters never travel: they are QGIS layers.

Qt-free.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

#: SQLite ↔ PostGIS column names of pyArchInit's layers (the same alternatives
#: s3dgraphy#42 puts in the mapping)
ALIASES = {"sito_sond": ("sito",), "id_sondaggio": ("id_sondagg",),
           "sito": ("sito_sond",), "id_sondagg": ("id_sondaggio",)}

_CRS = re.compile(r"^\s*<[^>]*?/EPSG/0/(\d+)>\s*(.+)$", re.S)


def _layers() -> Dict[str, Dict[str, Any]]:
    """``{table: spec}`` from s3dgraphy's pyArchInit mapping (footprint_layers)."""
    import s3dgraphy
    path = os.path.join(os.path.dirname(s3dgraphy.__file__), "mappings", "pyarchinit",
                        "pyarchinit_us_mapping.json")
    with open(path, encoding="utf-8") as fh:
        cfg = json.load(fh).get("footprint_layers") or {}
    out = {}
    for role, spec in (("site", cfg.get("site")), ("units", cfg.get("units"))):
        if spec:
            out[spec["table"]] = dict(spec, role=role)
    for spec in cfg.get("places") or []:
        out[spec["table"]] = dict(spec, role="place")
    return out


def _first(value) -> Optional[str]:
    return value[0] if isinstance(value, (list, tuple)) and value else value


def footprints_in(graph) -> List[Dict[str, Any]]:
    """The room's footprints: ``{owner, layer, key_column, feature, srid, wkt}``."""
    nodes = {str(n.node_id): n for n in getattr(graph, "nodes", None) or []}
    owner_of: Dict[str, Any] = {}
    source_of: Dict[str, Any] = {}
    for e in getattr(graph, "edges", None) or []:
        if e.edge_type == "has_property":
            owner_of[str(e.edge_target)] = nodes.get(str(e.edge_source))
        elif e.edge_type == "has_data_provenance":
            source_of[str(e.edge_source)] = nodes.get(str(e.edge_target))
    out = []
    for nid, node in nodes.items():
        data = getattr(node, "data", None) or {}
        attrs = getattr(node, "attributes", None) or {}
        kind = (data.get("property_type") or attrs.get("property_type")
                or getattr(node, "property_type", None))
        if kind != "footprint":
            continue
        value = str(data.get("value") or getattr(node, "value", "") or "")
        m = _CRS.match(value)
        ext = source_of.get(nid)
        edata = (getattr(ext, "data", None) or {}) if ext is not None else {}
        if not m or ext is None or not edata.get("layer"):
            continue
        out.append({"owner": owner_of.get(nid), "layer": edata.get("layer"),
                    "key_column": edata.get("feature_key"), "feature": edata.get("feature"),
                    "srid": int(m.group(1)), "wkt": m.group(2).strip(), "property": nid})
    return out


def _engine(connection_url: str):
    """An engine that can write SpatiaLite geometries (its triggers need the
    extension) — pyArchInit's own loader, the mod_spatialite of the QGIS running."""
    from sqlalchemy import create_engine, event
    engine = create_engine(connection_url)
    if engine.dialect.name == "sqlite":
        from modules.utility.spatialite_loader import load_spatialite

        @event.listens_for(engine, "connect")
        def _spatialite(dbapi_conn, _record):
            load_spatialite(dbapi_conn)
    return engine


def _layer_info(conn, dialect: str, table: str) -> Tuple[Optional[int], bool]:
    """``(srid, multi)`` of the layer's geometry column."""
    from sqlalchemy import text
    if dialect == "postgresql":
        row = conn.execute(text("SELECT srid, type FROM geometry_columns WHERE f_table_name = :t "
                                "AND f_geometry_column = 'the_geom'"), {"t": table}).fetchone()
        return (int(row[0]), "MULTI" in str(row[1]).upper()) if row else (None, False)
    row = conn.execute(text("SELECT srid, geometry_type FROM geometry_columns "
                            "WHERE lower(f_table_name) = lower(:t)"), {"t": table}).fetchone()
    if not row:
        return None, False
    return int(row[0]), int(row[1]) % 1000 == 6


def _column(have: set, name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    for c in (name,) + ALIASES.get(name, ()):
        if c in have:
            return c
    return None


def _geometry(wkt: str, srid: int, target: Optional[int], multi: bool):
    """The OGR geometry, in ``target``'s CRS, single or multi like the layer."""
    from osgeo import ogr, osr
    geom = ogr.CreateGeometryFromWkt(wkt)
    if geom is None:
        raise ValueError("unreadable WKT")
    if target and target != srid:
        src, dst = osr.SpatialReference(), osr.SpatialReference()
        src.ImportFromEPSG(srid)
        dst.ImportFromEPSG(target)
        for ref in (src, dst):
            if hasattr(ref, "SetAxisMappingStrategy"):
                ref.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        geom.Transform(osr.CoordinateTransformation(src, dst))
    if multi:
        geom = ogr.ForceToMultiPolygon(geom)
    elif geom.GetGeometryType() in (ogr.wkbMultiPolygon, ogr.wkbMultiPolygon25D) \
            and geom.GetGeometryCount() == 1:
        geom = geom.GetGeometryRef(0).Clone()
    return geom


def _same(a_wkb, b) -> bool:
    """Same shape: the area of their symmetric difference is negligible
    (1e-7 of the shape — well under a millimetre on an excavation)."""
    from osgeo import ogr
    a = ogr.CreateGeometryFromWkb(bytes(a_wkb))
    if a is None:
        return False
    diff = a.SymDifference(b)
    return diff is None or diff.GetArea() <= 1e-7 * max(a.GetArea(), b.GetArea(), 1e-6)


def _row_values(spec: Dict[str, Any], have: set, fp: Dict[str, Any], site: str) -> Optional[Dict[str, Any]]:
    """The identifying columns of the feature in this database (None: cannot)."""
    owner = fp["owner"]
    odata = (getattr(owner, "data", None) or {}) if owner is not None else {}
    values: Dict[str, Any] = {}
    site_col = _column(have, _first(spec.get("site_column")))
    key_col = _column(have, fp.get("key_column")) or _column(have, _first(spec.get("key_column")))
    if not site_col or not key_col:
        return None
    values[site_col] = site
    values[key_col] = str(fp["feature"])
    if spec.get("role") == "units":
        area_col = _column(have, spec.get("area_column"))
        area = odata.get("area") or (getattr(owner, "attributes", None) or {}).get("area")
        if not area_col or not area:
            return None
        values[area_col] = str(area)
    if spec.get("type_column"):
        # the place's own column (loc::<column>::study::<key>) is its type
        m = re.match(r"^loc::([^:]+)::", str(getattr(owner, "node_id", "") or ""))
        type_col = _column(have, spec.get("type_column"))
        if m and type_col:
            values[type_col] = m.group(1)
    return values


def pull_geometries(connection_url: str, site: str, graph, *, dry_run: bool = False) -> Dict[str, Any]:
    """Write the room's footprints into the local GIS layers (see the module)."""
    from sqlalchemy import inspect, text
    report = {"footprints": 0, "inserted": 0, "updated": 0, "same": 0, "kept_local": [],
              "skipped": [], "dry_run": dry_run}
    found = footprints_in(graph)
    report["footprints"] = len(found)
    if not found:
        return report
    try:
        from osgeo import ogr  # noqa: F401
    except ImportError:                                      # pragma: no cover
        report["skipped"].append("GDAL/OGR not available: geometries not written")
        return report
    specs = _layers()
    engine = _engine(connection_url)
    dialect = engine.dialect.name
    geom_from = "ST_GeomFromText" if dialect == "postgresql" else "GeomFromText"
    # read back as WKB, exactly: AsText rounds to 6 decimals
    as_wkb = "ST_AsBinary" if dialect == "postgresql" else "AsBinary"
    # a unit has one row per drawn polygon: compare with their union
    union = "ST_Union" if dialect == "postgresql" else "GUnion"
    tables = set(inspect(engine).get_table_names())
    with engine.begin() as conn:
        for fp in found:
            table = fp["layer"]
            spec = specs.get(table)
            if spec is None or table not in tables:
                report["skipped"].append(f"{table}: no such layer here")
                continue
            have = {c["name"] for c in inspect(conn).get_columns(table)}
            values = _row_values(spec, have, fp, site)
            if values is None:
                report["skipped"].append(f"{table} {fp['feature']}: its columns are not in this layer")
                continue
            srid, multi = _layer_info(conn, dialect, table)
            # a layer without a declared CRS (srid -1, old databases): no
            # transformation, written with the layer's own srid
            try:
                geom = _geometry(fp["wkt"], fp["srid"], srid if srid and srid > 0 else None, multi)
            except Exception as e:  # noqa: BLE001
                report["skipped"].append(f"{table} {fp['feature']}: {e}")
                continue
            where = " AND ".join(f'"{c}" = :{c}' for c in values)
            row = conn.execute(text(f'SELECT {as_wkb}({union}(the_geom)), COUNT(*) FROM "{table}" '
                                    f'WHERE {where}'), values).fetchone()
            row = row if row is not None and row[1] else None
            params = dict(values, wkt=geom.ExportToWkt(), srid=srid if srid is not None else fp["srid"])
            if row is not None and row[0]:
                if _same(row[0], geom):
                    report["same"] += 1
                else:
                    report["kept_local"].append(f"{table} {fp['feature']}")
                continue
            if dry_run:
                report["updated" if row is not None else "inserted"] += 1
                continue
            if row is not None:
                conn.execute(text(f'UPDATE "{table}" SET the_geom = {geom_from}(:wkt, :srid) '
                                  f'WHERE {where}'), params)
                report["updated"] += 1
            else:
                cols = list(values)
                conn.execute(text(
                    f'INSERT INTO "{table}" ({", ".join(chr(34) + c + chr(34) for c in cols)}, the_geom) '
                    f'VALUES ({", ".join(":" + c for c in cols)}, {geom_from}(:wkt, :srid))'), params)
                report["inserted"] += 1
    return report
