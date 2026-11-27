# -*- coding: utf-8 -*-
"""Where a site is, for the em.json's GeoPositionNode.

A graph made by pyArchInit had a GeoPositionNode with no CRS: EMStudio
(``gis-scene.ts``, ``frameOf``) draws GIS layers only when the graph says
its EPSG, so the room's excavation plans were listed and never drawn
(27 Nov 2026). The site's CRS is its GIS layers' (when metric), the anchor
the middle of its drawings rounded to 10 m, so the scene-local numbers stay
small. A graph that already says where it is (TempluMare, from EMStudio) is
left as it is.
"""
from typing import Optional, Tuple

#: the layers of a site's drawings, and the column naming the site
LAYERS = (("pyunitastratigrafiche", "scavo_s"),
          ("pyunitastratigrafiche_usm", "scavo_s"),
          ("pyarchinit_siti", "sito_nome"),
          ("pyarchinit_sondaggi", "sito_sond"))


def _engine(connection_url):
    from sqlalchemy import create_engine, event
    engine = create_engine(connection_url)
    if engine.dialect.name == "sqlite":
        from ..utility.spatialite_loader import load_spatialite

        @event.listens_for(engine, "connect")
        def _spatialite(dbapi_conn, _record):     # noqa: ANN001
            load_spatialite(dbapi_conn)
    return engine


def site_frame(connection_url, site) -> Optional[Tuple[int, float, float]]:
    """``(epsg, x, y)`` of the site, or None (no drawings, no metric CRS)."""
    from sqlalchemy import text
    from .em_drawings import crs_kind
    from .sync.em_drawings_import import layer_srid
    try:
        engine = _engine(connection_url)
        with engine.connect() as conn:
            for table, column in LAYERS:
                srid = layer_srid(conn, table)
                if srid is None or crs_kind(srid) != "metric":
                    continue
                try:
                    row = conn.execute(text(
                        "SELECT AVG(ST_X(ST_Centroid(the_geom))), AVG(ST_Y(ST_Centroid(the_geom))) "
                        "FROM %s WHERE %s = :s AND the_geom IS NOT NULL" % (table, column)),
                        {"s": site}).fetchone()
                except Exception:                   # noqa: BLE001
                    continue
                if row and row[0] is not None and row[1] is not None:
                    return int(srid), round(float(row[0]), -1), round(float(row[1]), -1)
    except Exception:                               # noqa: BLE001
        return None
    return None


def declare_site_frame(graph, connection_url, site) -> Optional[Tuple[int, float, float]]:
    """Write the site's CRS and anchor on a graph that does not say where it
    is; returns what was written, or None."""
    try:
        from s3dgraphy import api
    except ImportError:
        return None
    if api.georeference_state(graph) != "undeclared":
        return None
    frame = site_frame(connection_url, site)
    if frame is None:
        return None
    epsg, x, y = frame
    api.declare_georeference(graph, epsg, shift_x=x, shift_y=y, shift_z=0.0)
    _place_site(graph, epsg, x, y)
    return frame


def _place_site(graph, epsg, x, y) -> None:
    """The site's own position (``site_position``, WGS 84) on the graph node,
    when it has none: with only the scene's georeference the narrative's
    «Where it is» chapter stays «to be written», rightly so — the scene's
    offset is not the site's place. Here the place is known: the middle of
    the drawings."""
    try:
        from s3dgraphy.nodes.graph_node import GraphNode
        from qgis.core import (QgsCoordinateReferenceSystem, QgsCoordinateTransform,
                               QgsPointXY, QgsProject)
    except ImportError:
        return
    nodes = [n for n in (getattr(graph, "nodes", None) or []) if isinstance(n, GraphNode)]
    if not nodes:
        return
    data = nodes[0].data if isinstance(getattr(nodes[0], "data", None), dict) else None
    if data is None or isinstance(data.get("site_position"), dict):
        return
    try:
        t = QgsCoordinateTransform(QgsCoordinateReferenceSystem.fromEpsgId(int(epsg)),
                                   QgsCoordinateReferenceSystem.fromEpsgId(4326),
                                   QgsProject.instance())
        p = t.transform(QgsPointXY(float(x), float(y)))
    except Exception:                               # noqa: BLE001
        return
    if -90 <= p.y() <= 90 and -180 <= p.x() <= 180 and (p.x() or p.y()):
        data["site_position"] = {"lat": round(p.y(), 6), "lon": round(p.x(), 6)}
