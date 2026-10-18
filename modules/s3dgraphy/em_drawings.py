"""Piante e prospetti dai proxy 3D (spec 2026-10-18-geometrie-dai-proxy-3d-design).

Da un array di triangoli (``glb_mesh``) alle geometrie dei due layer di
pyArchInit:

* la **pianta** (``pyunitastratigrafiche``): l'ombra vista dall'alto, nel
  sistema dell'em.json, messa sulla mappa con la regola di s3dgraphy
  (rotazione, poi spostamento: ``api.georeference_scene``);
* i **disegni verticali** (``pyunitastratigrafiche_usm``): la sagoma su un
  piano verticale, in coordinate del disegno, cioè X = metri lungo la vista
  e Y = quota.

Le coppie ``[tipo, nome]`` dei disegni ricavati si riconoscono dal nome
(``3D-PLA``, ``3D-PRO-…``): ``without_derived_pairs`` le toglie dall'export
dell'em.json, ``merge_derived_pairs`` le fa sopravvivere al reimport.
QGIS si importa solo dentro le funzioni di geometria.
"""
from __future__ import annotations

import ast
import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

#: Il disegnatore dei poligoni e dei documenti ricavati (il segno di provenienza).
DRAWER = "pyArchInit 3D"
PLAN_NAME = "3D-PLA"
SIDES = ("N", "E", "S", "W")

MIN_TRIANGLE_AREA = 1e-6        # m²: le facce viste di taglio
MIN_PART_AREA = 1e-4            # m²: parti e buchi più piccoli si tolgono
SIMPLIFY = 0.01                 # m
UNION_BLOCK = 2000
GAP = 10.0                      # m fra un disegno verticale e l'altro
LONG_RATIO = 1.5                # lato lungo / lato corto perché un'unità abbia un «fronte»


# --------------------------------------------------------------- i sistemi

def scene_from_gltf(tri: np.ndarray) -> np.ndarray:
    """Dalla scena glTF (Y in alto) alla scena EM (Z in alto): X = gx, Y = −gz, Z = gy."""
    tri = np.asarray(tri, dtype=np.float64)
    out = np.empty_like(tri)
    out[..., 0] = tri[..., 0]
    out[..., 1] = -tri[..., 2]
    out[..., 2] = tri[..., 1]
    return out


def crs_kind(srid) -> str:
    """``metric``, ``geographic`` o ``undefined`` (``-1``, ``0``, assente o sconosciuto)."""
    try:
        srid = int(srid)
    except (TypeError, ValueError):
        return "undefined"
    if srid <= 0:
        return "undefined"
    from qgis.core import QgsCoordinateReferenceSystem
    crs = QgsCoordinateReferenceSystem.fromEpsgId(srid)
    if not crs.isValid():
        return "undefined"
    return "geographic" if crs.isGeographic() else "metric"


@dataclass(frozen=True)
class Georef:
    """Dove sta la scena, secondo l'em.json (il ``GeoPositionNode``)."""
    state: str                      # declared | undeclared | legacy_default
    epsg: Optional[int]
    shift_x: float = 0.0
    shift_y: float = 0.0
    shift_z: float = 0.0
    rotation: float = 0.0
    metric: bool = False

    @property
    def usable(self) -> bool:
        """Le piante si possono mettere sulla mappa."""
        return self.state == "declared" and self.epsg is not None and self.metric


def georef_of(graph) -> Georef:
    from s3dgraphy import api
    stato = api.georeference_state(graph)
    a = api._geo_anchor(graph)
    epsg = a.get("epsg")
    return Georef(state=stato, epsg=epsg, shift_x=float(a.get("shift_x") or 0.0),
                  shift_y=float(a.get("shift_y") or 0.0), shift_z=float(a.get("shift_z") or 0.0),
                  rotation=float(a.get("rotation") or 0.0),
                  metric=epsg is not None and crs_kind(epsg) == "metric")


def place(graph, georef: Georef, pts: np.ndarray, shift_z: float) -> np.ndarray:
    """Punti della scena EM ``(n, 3)`` → mappa: XY con la regola di s3dgraphy
    (se la scena è georeferenziata), quota + ``shift_z``."""
    pts = np.asarray(pts, dtype=np.float64)
    out = pts.copy()
    if georef.usable and len(pts):
        from s3dgraphy import api
        info = api.georeference_scene(graph, [(float(x), float(y)) for x, y in pts[:, :2]],
                                      epsg_target=int(georef.epsg))
        out[:, :2] = np.asarray(info["points"], dtype=np.float64)
    out[:, 2] = pts[:, 2] + float(shift_z)
    return out


# ------------------------------------------------------------- i poligoni

def _areas(tri2d: np.ndarray) -> np.ndarray:
    a = tri2d[:, 1] - tri2d[:, 0]
    b = tri2d[:, 2] - tri2d[:, 0]
    return 0.5 * np.abs(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0])


def _wkt(blocco: list) -> str:
    parti = ["((%r %r,%r %r,%r %r,%r %r))" % (x0, y0, x1, y1, x2, y2, x0, y0)
             for (x0, y0), (x1, y1), (x2, y2) in blocco]
    return "MULTIPOLYGON(" + ",".join(parti) + ")"


def _union_2d(tri2d):
    """L'unione dei triangoli piani ``(n, 3, 2)``, a blocchi; None se non resta niente."""
    from qgis.core import QgsGeometry
    tri2d = np.asarray(tri2d, dtype=np.float64)
    if tri2d.size == 0:
        return None
    tri2d = tri2d[_areas(tri2d) >= MIN_TRIANGLE_AREA]
    if not len(tri2d):
        return None
    blocchi = []
    for s in range(0, len(tri2d), UNION_BLOCK):
        g = QgsGeometry.fromWkt(_wkt(tri2d[s:s + UNION_BLOCK].tolist()))
        blocchi.append(QgsGeometry.unaryUnion([g]))
    return blocchi[0] if len(blocchi) == 1 else QgsGeometry.unaryUnion(blocchi)


def _polygons(g) -> list:
    from qgis.core import QgsWkbTypes
    if g is None or g.isEmpty():
        return []
    parti = []
    for p in g.asGeometryCollection():
        if p.isEmpty() or p.type() != QgsWkbTypes.PolygonGeometry:
            continue
        parti.extend(p.asGeometryCollection() if p.isMultipart() else [p])
    return parti


def _clean(g):
    """Valida, semplificata a 1 cm, senza briciole: un MultiPolygon o None."""
    from qgis.core import QgsGeometry
    if g is None or g.isEmpty():
        return None
    g = g.makeValid().simplify(SIMPLIFY).makeValid()
    parti = []
    for p in _polygons(g):
        if p.area() < MIN_PART_AREA:
            continue
        p = p.removeInteriorRings(MIN_PART_AREA)
        if not p.isEmpty():
            parti.append(p)
    if not parti:
        return None
    out = QgsGeometry.collectGeometry(parti)
    out.convertToMultiType()
    return out


def plan_geometry(tri_map: np.ndarray):
    """La pianta di triangoli già sulla mappa ``(n, 3, 3)``: MultiPolygon o None."""
    tri_map = np.asarray(tri_map, dtype=np.float64)
    return _clean(_union_2d(tri_map[..., :2])) if tri_map.size else None
