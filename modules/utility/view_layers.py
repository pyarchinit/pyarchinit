"""Le viste di pyArchInit come layer QGIS **non** aggiunti al progetto:
dalla finestra «Stili delle viste» (anteprima) e dalla mappa della
narrativa (geometrie delle unità). SQLite via OGR, PostgreSQL via
``QgsDataSourceUri``; filtro sul sito se la vista ha il campo."""
from __future__ import annotations

import os
from typing import Optional

from .view_styles import ViewSpec, view_label


def load_view_layer(conn_str: str, spec: ViewSpec, site: Optional[str] = None, lang: Optional[str] = None):
    """La vista dal database, come layer **non** aggiunto al progetto,
    filtrata sul sito se la vista ha il campo. ``None`` se non c'è."""
    from qgis.core import QgsDataSourceUri, QgsVectorLayer
    from sqlalchemy.engine import make_url
    try:
        url = make_url(str(conn_str))
    except Exception:                               # noqa: BLE001
        return None
    nome = view_label(spec, lang)
    filtro = ""
    if site and spec.site_field:
        filtro = "%s = '%s'" % (spec.site_field, str(site).replace("'", "''"))
    if url.drivername.startswith("sqlite"):
        percorso = url.database or ""
        if not os.path.isfile(percorso):
            return None
        layer = QgsVectorLayer("%s|layername=%s" % (percorso, spec.name), nome, "ogr",
                               QgsVectorLayer.LayerOptions(loadDefaultStyle=False))
        if not layer.isValid():
            return None
        if filtro and spec.site_field in [f.name() for f in layer.fields()]:
            layer.setSubsetString(filtro)
    else:
        uri = QgsDataSourceUri()
        uri.setConnection(url.host or "", str(url.port or 5432), url.database or "",
                          url.username or "", url.password or "")
        uri.setDataSource("public", spec.name, "the_geom", filtro, "gid")
        layer = QgsVectorLayer(uri.uri(), nome, "postgres",
                               QgsVectorLayer.LayerOptions(loadDefaultStyle=False))
        if not layer.isValid():
            return None
    return layer
