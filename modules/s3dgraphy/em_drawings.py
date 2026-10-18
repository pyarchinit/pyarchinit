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


# ---------------------------------------------------------- le viste verticali

@dataclass(frozen=True)
class View:
    """Un piano verticale da cui si guarda. ``d`` va da chi guarda verso la
    scena (orizzontale, unitario); ``r`` è l'asse destro del disegno;
    ``side`` è da dove si guarda, con gli otto punti della rosa."""
    code: str
    d: Tuple[float, float]
    side: str

    @property
    def r(self) -> Tuple[float, float]:
        return (self.d[1], -self.d[0])


#: Chi guarda sta dal lato che dà il nome alla vista (spec D5).
SITE_VIEWS: Dict[str, View] = {
    "N": View("N", (0.0, -1.0), "N"),
    "E": View("E", (-1.0, 0.0), "E"),
    "S": View("S", (0.0, 1.0), "S"),
    "W": View("W", (1.0, 0.0), "W"),
}

_ROSA = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")


def rose8(dx: float, dy: float) -> str:
    """La direzione ``(dx, dy)`` con gli otto punti della rosa (0 = nord, in senso orario)."""
    angolo = (math.degrees(math.atan2(dx, dy)) + 360.0) % 360.0
    return _ROSA[int((angolo + 22.5) // 45) % 8]


def centroid_xy(tri_map: np.ndarray) -> Tuple[float, float]:
    c = np.asarray(tri_map, dtype=np.float64).reshape(-1, 3).mean(axis=0)
    return float(c[0]), float(c[1])


def site_frame(tri_maps: Iterable[np.ndarray]) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """L'angolo minimo e il centro dell'ingombro in pianta di tutte le unità."""
    pts = np.concatenate([np.asarray(t, dtype=np.float64).reshape(-1, 3) for t in tri_maps])
    lo, hi = pts[:, :2].min(axis=0), pts[:, :2].max(axis=0)
    return (float(lo[0]), float(lo[1])), (float((lo[0] + hi[0]) / 2), float((lo[1] + hi[1]) / 2))


def _long_axis_xy(xy) -> Optional[Tuple[float, float, float, float]]:
    """Asse lungo (versore) e scarti lungo/corto di una nuvola di punti in
    pianta, dalle componenti principali: serve quando la pianta è vuota (un
    muro senza spessore)."""
    pts = np.asarray(xy, dtype=np.float64).reshape(-1, 2)
    if len(pts) < 2:
        return None
    c = pts - pts.mean(axis=0)
    autovalori, autovettori = np.linalg.eigh(c.T @ c / len(pts))
    lungo, corto = math.sqrt(max(autovalori[1], 0.0)), math.sqrt(max(autovalori[0], 0.0))
    return float(autovettori[0, 1]), float(autovettori[1, 1]), lungo, corto


def unit_view(code: str, plan, unit_c: Tuple[float, float], site_c: Tuple[float, float],
              xy=None) -> View:
    """Il prospetto di un'unità: perpendicolare al suo lato lungo, guardato dal
    lato del centro dello scavo; un'unità quasi quadrata si guarda dal centro.
    Senza pianta il lato lungo viene dai vertici ``xy`` (un muro senza
    spessore, che dal centro si vedrebbe di taglio)."""
    vx, vy = unit_c[0] - site_c[0], unit_c[1] - site_c[1]
    d = None
    asse = None
    if plan is not None and not plan.isEmpty():
        anello = plan.orientedMinimumBoundingBox()[0].asPolygon()[0]
        e1 = (anello[1].x() - anello[0].x(), anello[1].y() - anello[0].y())
        e2 = (anello[2].x() - anello[1].x(), anello[2].y() - anello[1].y())
        l1, l2 = math.hypot(*e1), math.hypot(*e2)
        (lx, ly), lungo, corto = (e1, l1, l2) if l1 >= l2 else (e2, l2, l1)
        if lungo > 0:
            asse = (lx / lungo, ly / lungo, lungo, corto)
    elif xy is not None:
        asse = _long_axis_xy(xy)
    if asse is not None:
        lx, ly, lungo, corto = asse
        if lungo > 0 and (corto <= 1e-9 or lungo / corto >= LONG_RATIO):
            nx, ny = -ly, lx
            prodotto = nx * vx + ny * vy
            if prodotto < -1e-9 or (abs(prodotto) <= 1e-9 and ny < 0):
                nx, ny = -nx, -ny
            d = (nx + 0.0, ny + 0.0)
    if d is None:
        n = math.hypot(vx, vy)
        d = (vx / n, vy / n) if n > 1e-9 else (0.0, 1.0)
    return View(code, d, rose8(-d[0], -d[1]))


def view_geometry(tri_map: np.ndarray, view: View, origin: Tuple[float, float]):
    """La sagoma sul piano della vista, in coordinate del disegno:
    u = (P − O)·r, v = quota. MultiPolygon o None."""
    t = np.asarray(tri_map, dtype=np.float64)
    if not t.size:
        return None
    rx, ry = view.r
    u = (t[..., 0] - origin[0]) * rx + (t[..., 1] - origin[1]) * ry
    return _clean(_union_2d(np.stack([u, t[..., 2]], axis=-1)))


def depth(tri_map: np.ndarray, view: View) -> float:
    """Quanto è lontano da chi guarda: più grande, più lontano."""
    x, y = centroid_xy(tri_map)
    return x * view.d[0] + y * view.d[1]


def lay_out(spans: Sequence[Tuple[float, float]], gap: float = GAP) -> List[float]:
    """Lo spostamento in u di ogni disegno, ``spans`` = ``(u_min, u_max)``
    nell'ordine: uno accanto all'altro, separati da ``gap``."""
    spostamenti, cursore = [], 0.0
    for umin, umax in spans:
        spostamenti.append(cursore - umin)
        cursore += (umax - umin) + gap
    return spostamenti


def span_u(geom) -> Tuple[float, float]:
    bb = geom.boundingBox()
    return bb.xMinimum(), bb.xMaximum()


def translated(geom, du: float):
    from qgis.core import QgsGeometry
    out = QgsGeometry(geom)
    out.translate(float(du), 0.0)
    return out


# ------------------------------------------------- i nomi e le coppie della scheda

_DERIVED = re.compile(r"^3D-(PLA|PRO-.+|SEZ-.+)$")
_UNSAFE = re.compile(r"[^0-9A-Za-z._-]+")


def side_name(code: str) -> str:
    return "3D-PRO-" + str(code)


def is_derived_name(nome) -> bool:
    return bool(_DERIVED.match(str(nome or "").strip()))


def _safe(testo) -> str:
    return _UNSAFE.sub("_", str(testo or "").strip().replace("/", "-")).strip("_")


def unit_drawing_names(items: Sequence[Tuple[str, str, str, str]]) -> Dict[str, str]:
    """``(chiave, unita_tipo, us, area)`` → «3D-PRO-<tipo><us>»; ai nomi che
    verrebbero doppi si aggiunge «-A<area>»."""
    base = {k: "3D-PRO-%s%s" % (_safe(t), _safe(u)) for k, t, u, _a in items}
    quanti = Counter(base.values())
    return {k: base[k] + ("-A%s" % _safe(a) if quanti[base[k]] > 1 else "")
            for k, _t, _u, a in items}


def _pairs(value):
    """La lista della scheda US (la ``repr`` di una lista di coppie) → lista;
    ``None`` se non si legge."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [list(p) if isinstance(p, (list, tuple)) else p for p in value]
    testo = str(value).strip()
    if not testo:
        return []
    try:
        dati = ast.literal_eval(testo)
    except (ValueError, SyntaxError, MemoryError, RecursionError):
        return None
    if not isinstance(dati, (list, tuple)):
        return None
    return [list(p) if isinstance(p, (list, tuple)) else p for p in dati]


def _is_derived_pair(p) -> bool:
    return isinstance(p, list) and len(p) >= 2 and is_derived_name(p[1])


def without_derived_pairs(value):
    """Per l'export dell'em.json: la lista senza le coppie ricavate dal 3D.
    Un valore che non si legge, o senza coppie ricavate, torna com'era."""
    coppie = _pairs(value)
    if not coppie or not any(_is_derived_pair(p) for p in coppie):
        return value
    return str([p for p in coppie if not _is_derived_pair(p)])


def with_derived_pairs(value, pairs) -> Optional[str]:
    """La lista della scheda con le coppie ricavate di adesso al posto di
    quelle di prima; le altre restano. ``None`` se la lista non si legge."""
    coppie = _pairs(value)
    if coppie is None:
        return None
    resto = [p for p in coppie if not _is_derived_pair(p)]
    nuove = []
    for p in pairs:
        p = [str(x) for x in p]
        if p not in resto and p not in nuove:
            nuove.append(p)
    return str(resto + nuove)


def merge_derived_pairs(new_value, old_value):
    """Reimport di un em.json: la lista che arriva, più le coppie ricavate che
    la scheda aveva (nell'em.json non ci sono mai)."""
    vecchie = _pairs(old_value)
    ricavate = [p for p in (vecchie or []) if _is_derived_pair(p)]
    if not ricavate:
        return new_value
    nuove = _pairs(new_value)
    if nuove is None:
        return new_value
    return str([p for p in nuove if not _is_derived_pair(p)] + ricavate)


# ------------------------------------------------------------------ le sezioni

def _section_segments(tri_map: np.ndarray, a, b):
    """I segmenti dove i triangoli attraversano il piano verticale per a→b, in
    coordinate del disegno (u lungo il tratto da a, v quota); e la lunghezza."""
    t = np.asarray(tri_map, dtype=np.float64)
    ax, ay = float(a[0]), float(a[1])
    lung = math.hypot(float(b[0]) - ax, float(b[1]) - ay)
    if lung <= 1e-9 or not t.size:
        return np.zeros((0, 2, 2)), lung
    rx, ry = (float(b[0]) - ax) / lung, (float(b[1]) - ay) / lung
    dx, dy = -ry, rx
    s = (t[..., 0] - ax) * dx + (t[..., 1] - ay) * dy
    s = np.where(np.abs(s) < 1e-9, 1e-9, s)            # un vertice sul piano conta da una parte
    sopra = s > 0
    attraversa = sopra.any(axis=1) & (~sopra).any(axis=1)
    t, s, sopra = t[attraversa], s[attraversa], sopra[attraversa]
    if not len(t):
        return np.zeros((0, 2, 2)), lung
    seg = np.zeros((len(t), 2, 3))
    quanti = np.zeros(len(t), dtype=int)
    for i, j in ((0, 1), (1, 2), (2, 0)):
        taglia = sopra[:, i] != sopra[:, j]
        pi, pj, si, sj = t[:, i], t[:, j], s[:, i], s[:, j]
        # Lo stesso spigolo, visto da due triangoli, si calcola sempre dallo
        # stesso estremo (il minore in ordine lessicografico): con i vertici in
        # ordine opposto i due punti differirebbero di 1e-10, i segmenti non si
        # toccherebbero e la poligonazione non chiuderebbe il profilo.
        scambia = (pi[:, 0] > pj[:, 0]) | ((pi[:, 0] == pj[:, 0]) & (
            (pi[:, 1] > pj[:, 1]) | ((pi[:, 1] == pj[:, 1]) & (pi[:, 2] > pj[:, 2]))))
        pa = np.where(scambia[:, None], pj, pi)
        pb = np.where(scambia[:, None], pi, pj)
        sa = np.where(scambia, sj, si)
        sb = np.where(scambia, si, sj)
        with np.errstate(divide="ignore", invalid="ignore"):
            f = sa / (sa - sb)
            punto = pa + (pb - pa) * f[:, None]
        k = np.nonzero(taglia)[0]
        seg[k, quanti[k]] = punto[k]
        quanti[k] += 1
    u = (seg[..., 0] - ax) * rx + (seg[..., 1] - ay) * ry
    return np.stack([u, seg[..., 2]], axis=-1), lung


def section_geometry(tri_map: np.ndarray, a, b):
    """Il profilo tagliato dal piano verticale del tratto a→b, fra u = 0 e
    u = |ab|: MultiPolygon o None. Si riempie tutto quello che sta dentro il
    contorno esterno: un'unità è un volume pieno, e i proxy di TempluMare hanno
    un guscio interno rientrato di un centimetro che, pari/dispari, lascerebbe
    solo un anello sottile (18 ottobre 2026)."""
    from qgis.core import QgsGeometry, QgsRectangle
    seg, lung = _section_segments(tri_map, a, b)
    if not len(seg):
        return None
    seg = seg[np.hypot(seg[:, 1, 0] - seg[:, 0, 0], seg[:, 1, 1] - seg[:, 0, 1]) > 1e-9]
    if not len(seg):
        return None
    wkt = "MULTILINESTRING(" + ",".join(
        "(%r %r,%r %r)" % (x0, y0, x1, y1) for (x0, y0), (x1, y1) in seg.tolist()) + ")"
    facce = _polygons(QgsGeometry.polygonize([QgsGeometry.unaryUnion([QgsGeometry.fromWkt(wkt)])]))
    if not facce:
        return None
    vmin, vmax = float(seg[..., 1].min()) - 1.0, float(seg[..., 1].max()) + 1.0
    tratto = QgsGeometry.fromRect(QgsRectangle(0.0, vmin, lung, vmax))
    return _clean(QgsGeometry.unaryUnion(facce).intersection(tratto))


def line_length(points) -> float:
    return float(sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:])))


def section_line_geometry(tri_map: np.ndarray, points):
    """Il profilo lungo una linea spezzata: ogni tratto si taglia da sé, e u
    continua da un tratto all'altro."""
    from qgis.core import QgsGeometry
    parti, u0 = [], 0.0
    for a, b in zip(points, points[1:]):
        lung = math.hypot(b[0] - a[0], b[1] - a[1])
        if lung <= 1e-9:
            continue
        g = section_geometry(tri_map, a, b)
        if g is not None:
            parti.append(translated(g, u0))
        u0 += lung
    if not parti:
        return None
    return _clean(QgsGeometry.unaryUnion(parti))
