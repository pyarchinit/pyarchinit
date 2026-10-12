# -*- coding: utf-8 -*-
"""L'immagine da segmentare: da un file raster o da un layer di tile.

Il worker SAM lavora su un PNG qualunque; la georeferenza resta qui, in un
`SamImage` (geotrasformazione a sei numeri, CRS, estensione), e serve dopo
per riportare i poligoni dai pixel alla mappa.

Due strade:

- **file raster** (GeoTIFF, JPEG georeferenziato…): si ritaglia e si scala
  con GDAL, senza rendering, cosi' i pixel sono quelli veri;
- **tile e servizi** (XYZ come ESRI/Google, WMS, ArcGIS REST, WCS): non c'e'
  un file, si **rende la vista** con il motore di QGIS alla risoluzione
  della mappa (o quella scelta) e si segmenta il reso.

Tutto in coordinate «nord in alto»: la geotrasformazione e'
(x0, dx, 0, y0, 0, -dy), con l'origine nell'angolo in alto a sinistra.
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor
from qgis.core import (QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsGeometry,
                       QgsMapRendererSequentialJob, QgsMapSettings, QgsPointXY, QgsProject,
                       QgsRasterLayer, QgsRectangle, QgsWkbTypes)

GeoTransform = Tuple[float, float, float, float, float, float]

#: Lingua dei messaggi (la finestra la imposta con `set_language`).
LANGUAGE = "it"
_M = {
    "not_file": {"it": "il layer non è un file raster", "en": "the layer is not a file raster"},
    "gdal_open": {"it": "GDAL non apre {0}", "en": "GDAL cannot open {0}"},
    "rotated": {"it": "raster ruotato: non supportato (riproiettalo prima)",
                "en": "rotated raster: not supported (reproject it first)"},
    "north_down": {"it": "raster con il nord in basso: non supportato",
                   "en": "raster with north at the bottom: not supported"},
    "outside": {"it": "l'area scelta non copre il raster", "en": "the chosen area does not cover the raster"},
    "png_write": {"it": "GDAL non ha scritto il PNG", "en": "GDAL did not write the PNG"},
    "bad_res": {"it": "risoluzione non valida", "en": "invalid resolution"},
    "render_failed": {"it": "rendering fallito", "en": "rendering failed"},
    "write_failed": {"it": "non riesco a scrivere {0}", "en": "cannot write {0}"},
    "tile_needs_area": {"it": "per un layer di tile serve un'area: la vista, un riquadro o un poligono",
                        "en": "a tile layer needs an area: the view, a box or a polygon"},
    "tile_needs_res": {"it": "per un layer di tile serve la risoluzione (unità di mappa per pixel)",
                       "en": "a tile layer needs the resolution (map units per pixel)"},
    "desc_wms": {"it": "tile / WMS (reso dalla vista)", "en": "tiles / WMS (rendered from the view)"},
    "desc_arcgis": {"it": "ArcGIS REST (reso dalla vista)", "en": "ArcGIS REST (rendered from the view)"},
    "desc_wcs": {"it": "WCS (reso dalla vista)", "en": "WCS (rendered from the view)"},
    "desc_other": {"it": "{0} (reso dalla vista)", "en": "{0} (rendered from the view)"},
}


def set_language(lang):
    """'it' o 'en' (tutto il resto cade sull'inglese)."""
    global LANGUAGE
    LANGUAGE = "it" if (lang or "").lower().startswith("it") else "en"


def msg(key, *args):
    text = _M[key].get(LANGUAGE, _M[key]["en"])
    return text.format(*args) if args else text

#: Lato massimo, in pixel, dell'immagine passata al modello (SAM lavora a
#: 1024 interni: oltre i 4096 si paga solo memoria).
DEFAULT_MAX_SIDE = 2048
MAX_SIDE_LIMIT = 8192


@dataclass
class SamImage:
    """Un PNG con la sua georeferenza."""
    path: str
    width: int
    height: int
    geotransform: GeoTransform
    crs: QgsCoordinateReferenceSystem
    source: str = "file"            # 'file' | 'render'

    @property
    def extent(self) -> QgsRectangle:
        x0, dx, _, y0, _, dy = self.geotransform
        return QgsRectangle(x0, y0 + dy * self.height, x0 + dx * self.width, y0)

    @property
    def pixel_size(self) -> float:
        return abs(self.geotransform[1])


# ----------------------------------------------------------------------
# Geometria dei pixel
# ----------------------------------------------------------------------
def map_to_pixel(gt: GeoTransform, x: float, y: float) -> Tuple[float, float]:
    """Coordinate mappa -> (colonna, riga) in pixel, frazionarie."""
    x0, dx, rx, y0, ry, dy = gt
    det = dx * dy - rx * ry
    if det == 0:
        raise ValueError("geotransform degenere")
    col = ((x - x0) * dy - (y - y0) * rx) / det
    row = ((y - y0) * dx - (x - x0) * ry) / det
    return col, row


def pixel_to_map(gt: GeoTransform, col: float, row: float) -> Tuple[float, float]:
    x0, dx, rx, y0, ry, dy = gt
    return x0 + col * dx + row * rx, y0 + col * ry + row * dy


def ring_to_map(gt: GeoTransform, ring: Sequence[Sequence[float]]) -> List[QgsPointXY]:
    return [QgsPointXY(*pixel_to_map(gt, c, r)) for c, r in ring]


def only_polygons(geom: Optional[QgsGeometry]) -> Optional[QgsGeometry]:
    """Le sole parti poligonali di una geometria (dopo `makeValid` un anello
    degenere diventa una linea, uno a farfalla una collezione): None se non resta nulla."""
    if geom is None or geom.isEmpty():
        return None
    if QgsWkbTypes.flatType(geom.wkbType()) == QgsWkbTypes.GeometryCollection:
        parts = [g for g in geom.asGeometryCollection() if g.type() == QgsWkbTypes.PolygonGeometry]
        if not parts:
            return None
        geom = QgsGeometry.collectGeometry(parts)
    if geom.type() != QgsWkbTypes.PolygonGeometry:
        return None
    geom.convertToMultiType()
    return geom


def polygon_to_geometry(polygon: dict, gt: GeoTransform) -> Optional[QgsGeometry]:
    """Un poligono del worker ({'ring': [[c, r], …], 'holes': [...]}) -> QgsGeometry valida (o None)."""
    ring = ring_to_map(gt, polygon.get("ring") or [])
    if len(ring) < 3:
        return None
    holes = [ring_to_map(gt, h) for h in polygon.get("holes") or [] if len(h) >= 3]
    geom = QgsGeometry.fromPolygonXY([ring] + holes)
    if geom.isEmpty():
        return None
    if not geom.isGeosValid():
        geom = only_polygons(geom.makeValid())
    if geom is None or geom.isEmpty():
        return None
    geom.convertToMultiType()
    return geom


def polygons_to_geometries(polygons: Sequence[dict], gt: GeoTransform) -> List[Tuple[dict, QgsGeometry]]:
    out = []
    for poly in polygons:
        geom = polygon_to_geometry(poly, gt)
        if geom is not None:
            out.append((poly, geom))
    return out


def clip_to_area(pairs, area: Optional[QgsGeometry], min_ratio=0.02):
    """Tiene solo la parte dentro `area` (poligono disegnato o da layer); scarta
    i ritagli che restano sotto `min_ratio` dell'area originale."""
    if area is None or area.isEmpty():
        return list(pairs)
    out = []
    for poly, geom in pairs:
        cut = geom.intersection(area)
        if cut.isEmpty():
            continue
        if geom.area() > 0 and cut.area() / geom.area() < min_ratio:
            continue
        cut.convertToMultiType()
        out.append((poly, cut))
    return out


# ----------------------------------------------------------------------
# Che cosa e' il layer
# ----------------------------------------------------------------------
def layer_file_path(layer) -> Optional[str]:
    """Il file del raster se e' un file sul disco (provider gdal), altrimenti None."""
    if layer is None or not isinstance(layer, QgsRasterLayer):
        return None
    provider = layer.providerType()
    if provider != "gdal":
        return None
    source = layer.source().split("|")[0]
    if source.startswith("/vsi"):
        return None
    return source if os.path.isfile(source) else None


def is_file_raster(layer) -> bool:
    return layer_file_path(layer) is not None


def describe_layer(layer) -> str:
    """Una riga per il dialogo: file e dimensioni, oppure servizio."""
    path = layer_file_path(layer)
    if path:
        return f"{os.path.basename(path)} — {layer.width()} × {layer.height()} px"
    provider = layer.providerType() if layer is not None else "?"
    key = {"wms": "desc_wms", "arcgismapserver": "desc_arcgis", "wcs": "desc_wcs"}.get(provider)
    return msg(key) if key else msg("desc_other", provider)


# ----------------------------------------------------------------------
# Preparazione dell'immagine
# ----------------------------------------------------------------------
def _fit(width: float, height: float, max_side: int) -> Tuple[int, int, float]:
    """(w, h, scala) per stare in `max_side`; la scala e' 1 se gia' ci sta."""
    width, height = max(1.0, width), max(1.0, height)
    scale = 1.0
    longest = max(width, height)
    if longest > max_side:
        scale = longest / float(max_side)
    return max(1, int(round(width / scale))), max(1, int(round(height / scale))), scale


def prepare_file_raster(layer, extent: Optional[QgsRectangle], out_path: str,
                        max_side: int = DEFAULT_MAX_SIDE) -> SamImage:
    """Ritaglia (a `extent`, nel CRS del layer) e scala il file con GDAL, in PNG."""
    from osgeo import gdal

    path = layer_file_path(layer)
    if not path:
        raise ValueError(msg("not_file"))
    ds = gdal.Open(path)
    if ds is None:
        raise ValueError(msg("gdal_open", path))
    gt = ds.GetGeoTransform()
    if gt[2] != 0 or gt[4] != 0:
        raise ValueError(msg("rotated"))
    full_w, full_h = ds.RasterXSize, ds.RasterYSize
    x0, dx, _, y0, _, dy = gt
    if dy >= 0:
        raise ValueError(msg("north_down"))

    if extent is None:
        c0, r0, c1, r1 = 0, 0, full_w, full_h
    else:
        c0 = int(math.floor((extent.xMinimum() - x0) / dx))
        c1 = int(math.ceil((extent.xMaximum() - x0) / dx))
        r0 = int(math.floor((extent.yMaximum() - y0) / dy))
        r1 = int(math.ceil((extent.yMinimum() - y0) / dy))
        c0, r0 = max(0, c0), max(0, r0)
        c1, r1 = min(full_w, c1), min(full_h, r1)
    if c1 - c0 < 2 or r1 - r0 < 2:
        raise ValueError(msg("outside"))

    out_w, out_h, _ = _fit(c1 - c0, r1 - r0, max_side)
    bands = ds.RasterCount
    kwargs = dict(format="PNG", srcWin=[c0, r0, c1 - c0, r1 - r0], width=out_w, height=out_h,
                  outputType=gdal.GDT_Byte, resampleAlg="bilinear")
    band1 = ds.GetRasterBand(1)
    if band1.GetRasterColorTable() is not None:
        kwargs["rgbExpand"] = "rgb"
    elif bands >= 3:
        kwargs["bandList"] = [1, 2, 3]
    else:
        kwargs["bandList"] = [1]
    if band1.DataType != gdal.GDT_Byte:
        kwargs["scaleParams"] = [[]]          # min/max -> 0..255 per banda
    result = gdal.Translate(out_path, ds, options=gdal.TranslateOptions(**kwargs))
    if result is None:
        raise ValueError(msg("png_write"))
    result = None
    ds = None
    aux = out_path + ".aux.xml"
    if os.path.exists(aux):
        os.remove(aux)
    sx = (c1 - c0) / float(out_w)
    sy = (r1 - r0) / float(out_h)
    new_gt = (x0 + c0 * dx, dx * sx, 0.0, y0 + r0 * dy, 0.0, dy * sy)
    return SamImage(out_path, out_w, out_h, new_gt, layer.crs(), "file")


def render_layer(layer, extent: QgsRectangle, crs: QgsCoordinateReferenceSystem, out_path: str,
                 map_units_per_pixel: float, max_side: int = DEFAULT_MAX_SIDE,
                 background=QColor(255, 255, 255)) -> SamImage:
    """Rende `layer` su `extent` (in `crs`) alla risoluzione chiesta, in PNG."""
    if map_units_per_pixel <= 0:
        raise ValueError(msg("bad_res"))
    out_w, out_h, scale = _fit(extent.width() / map_units_per_pixel,
                               extent.height() / map_units_per_pixel, max_side)
    mupp = map_units_per_pixel * scale
    # estensione allineata ai pixel: larghezza e altezza esatte
    x0, y0 = extent.xMinimum(), extent.yMaximum()
    aligned = QgsRectangle(x0, y0 - out_h * mupp, x0 + out_w * mupp, y0)

    settings = QgsMapSettings()
    settings.setLayers([layer])
    settings.setDestinationCrs(crs)
    settings.setOutputSize(QSize(out_w, out_h))
    settings.setExtent(aligned)
    settings.setBackgroundColor(background)
    settings.setOutputDpi(96)
    try:
        settings.setFlag(QgsMapSettings.Antialiasing, True)
    except (AttributeError, TypeError):
        pass
    job = QgsMapRendererSequentialJob(settings)
    job.start()
    job.waitForFinished()
    image = job.renderedImage()
    if image.isNull():
        raise ValueError(msg("render_failed"))
    if not image.save(out_path, "PNG"):
        raise ValueError(msg("write_failed", out_path))
    gt = (x0, mupp, 0.0, y0, 0.0, -mupp)
    return SamImage(out_path, out_w, out_h, gt, QgsCoordinateReferenceSystem(crs), "render")


def transform_extent(extent: QgsRectangle, src: QgsCoordinateReferenceSystem,
                     dst: QgsCoordinateReferenceSystem) -> QgsRectangle:
    if not src.isValid() or not dst.isValid() or src == dst:
        return QgsRectangle(extent)
    return QgsCoordinateTransform(src, dst, QgsProject.instance()).transformBoundingBox(extent)


def prepare_image(layer, extent: Optional[QgsRectangle], extent_crs: QgsCoordinateReferenceSystem,
                  out_path: str, map_units_per_pixel: Optional[float] = None,
                  max_side: int = DEFAULT_MAX_SIDE) -> SamImage:
    """L'immagine per il worker: dal file (ritagliata) o resa dalla vista.

    `extent` e' nel CRS `extent_crs` (quello della mappa). None = tutto il
    raster (solo per i file: per i tile serve sempre un'area).
    """
    if is_file_raster(layer):
        if extent is not None:
            extent = transform_extent(extent, extent_crs, layer.crs())
        return prepare_file_raster(layer, extent, out_path, max_side)
    if extent is None:
        raise ValueError(msg("tile_needs_area"))
    if not map_units_per_pixel:
        raise ValueError(msg("tile_needs_res"))
    return render_layer(layer, extent, extent_crs, out_path, map_units_per_pixel, max_side)


# ----------------------------------------------------------------------
# Maschera fuori dal poligono
# ----------------------------------------------------------------------
def mask_outside_polygon(image: SamImage, area: QgsGeometry, fill=(255, 255, 255)) -> None:
    """Imbianca i pixel fuori da `area` (nel CRS dell'immagine), sul PNG stesso.

    Cosi' il modo «tutto automatico» lavora solo dentro il poligono; il bordo
    bianco produce al massimo un poligono-cornice, che `clip_to_area` scarta.
    """
    import numpy as np
    try:
        import cv2
    except ImportError:      # pragma: no cover - QGIS porta sempre cv2, ma non si sa mai
        cv2 = None
    from qgis.PyQt.QtGui import QImage

    qimg = QImage(image.path).convertToFormat(QImage.Format.Format_RGB888)
    w, h = qimg.width(), qimg.height()
    ptr = qimg.constBits()
    ptr.setsize(qimg.sizeInBytes())
    stride = qimg.bytesPerLine()
    buf = np.frombuffer(ptr, dtype=np.uint8).reshape(h, stride)[:, : w * 3].reshape(h, w, 3).copy()

    mask = np.zeros((h, w), dtype=np.uint8)
    polygons = area.asMultiPolygon() if area.isMultipart() else [area.asPolygon()]
    gt = image.geotransform
    for rings in polygons:
        for n, ring in enumerate(rings):
            pts = np.array([map_to_pixel(gt, p.x(), p.y()) for p in ring], dtype=np.float64)
            if len(pts) < 3:
                continue
            if cv2 is not None:
                cv2.fillPoly(mask, [np.round(pts).astype(np.int32)], 255 if n == 0 else 0)
            else:
                from PIL import Image, ImageDraw
                pil = Image.fromarray(mask)
                ImageDraw.Draw(pil).polygon([tuple(p) for p in pts], fill=255 if n == 0 else 0)
                mask = np.array(pil, dtype=np.uint8)
    buf[mask == 0] = np.array(fill, dtype=np.uint8)
    out = QImage(buf.data, w, h, w * 3, QImage.Format.Format_RGB888)
    if not out.save(image.path, "PNG"):
        raise ValueError(msg("write_failed", image.path))


def geometry_in_image_crs(geom: QgsGeometry, geom_crs: QgsCoordinateReferenceSystem,
                          image: SamImage) -> QgsGeometry:
    out = QgsGeometry(geom)
    if geom_crs.isValid() and image.crs.isValid() and geom_crs != image.crs:
        out.transform(QgsCoordinateTransform(geom_crs, image.crs, QgsProject.instance()))
    return out
