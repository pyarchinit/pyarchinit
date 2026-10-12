"""SAM: l'immagine da segmentare, da file o da tile — 2026-10-12.

Prima la finestra prendeva `layer.source()` e pretendeva un file: con un
layer XYZ (ESRI, Google…) o WMS si fermava. Ora `sam_raster_source` ritaglia
i file con GDAL e **rende** i servizi dalla vista; in entrambi i casi il
worker riceve un PNG e QGIS tiene la georeferenza per tornare in mappa.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if sys.platform == "darwin" and os.path.isdir("/Applications/QGIS.app/Contents/Resources/proj"):
    os.environ.setdefault("PROJ_LIB", "/Applications/QGIS.app/Contents/Resources/proj")   # CRS dei GeoTIFF
pytest.importorskip("qgis.core")
np = pytest.importorskip("numpy")
gdal = pytest.importorskip("osgeo.gdal")

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from qgis.core import (QgsApplication, QgsCoordinateReferenceSystem, QgsGeometry,  # noqa: E402
                       QgsRasterLayer, QgsRectangle)
from qgis.PyQt.QtGui import QImage  # noqa: E402

from modules.gis import sam_raster_source as rs  # noqa: E402


@pytest.fixture(scope="module")
def qgs():
    app = QgsApplication.instance()
    if app is None:
        QgsApplication.setPrefixPath(os.environ.get("QGIS_PREFIX_PATH", "/Applications/QGIS.app/Contents/MacOS"), True)
        app = QgsApplication([], False)
        app.initQgis()
    return app


@pytest.fixture
def geotiff(tmp_path):
    """200 x 100 px, RGB, 0.5 m/px, origine (1000, 2000), EPSG:32633; a sinistra rosso, a destra blu."""
    path = str(tmp_path / "orto.tif")
    ds = gdal.GetDriverByName("GTiff").Create(path, 200, 100, 3, gdal.GDT_Byte)
    ds.SetGeoTransform((1000.0, 0.5, 0.0, 2000.0, 0.0, -0.5))
    srs = gdal.osr.SpatialReference()
    srs.ImportFromEPSG(32633)
    ds.SetProjection(srs.ExportToWkt())
    r = np.zeros((100, 200), dtype=np.uint8); r[:, :100] = 255
    b = np.zeros((100, 200), dtype=np.uint8); b[:, 100:] = 255
    ds.GetRasterBand(1).WriteArray(r)
    ds.GetRasterBand(2).WriteArray(np.zeros((100, 200), dtype=np.uint8))
    ds.GetRasterBand(3).WriteArray(b)
    ds.FlushCache()
    ds = None
    return path


def test_geotransform_avanti_e_indietro():
    gt = (1000.0, 0.5, 0.0, 2000.0, 0.0, -0.5)
    assert rs.map_to_pixel(gt, 1000.0, 2000.0) == (0.0, 0.0)
    assert rs.map_to_pixel(gt, 1010.0, 1995.0) == (20.0, 10.0)
    assert rs.pixel_to_map(gt, 20.0, 10.0) == (1010.0, 1995.0)


def test_il_file_raster_si_riconosce_e_il_tile_no(qgs, geotiff):
    layer = QgsRasterLayer(geotiff, "orto")
    assert layer.isValid() and rs.is_file_raster(layer)
    assert "orto.tif" in rs.describe_layer(layer) and "200 × 100" in rs.describe_layer(layer)
    xyz = QgsRasterLayer("type=xyz&url=https://tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0",
                         "osm", "wms")
    assert not rs.is_file_raster(xyz)
    assert "reso dalla vista" in rs.describe_layer(xyz)


def test_ritaglio_del_file_con_gdal(qgs, geotiff, tmp_path):
    layer = QgsRasterLayer(geotiff, "orto")
    # meta' destra: x da 1050 a 1100, y da 1950 a 2000  -> colonne 100..200, righe 0..100
    extent = QgsRectangle(1050, 1950, 1100, 2000)
    img = rs.prepare_image(layer, extent, layer.crs(), str(tmp_path / "a.png"), max_side=4096)
    assert (img.width, img.height) == (100, 100) and img.source == "file"
    assert img.geotransform == (1050.0, 0.5, 0.0, 2000.0, 0.0, -0.5)
    assert img.crs.authid() == "EPSG:32633"
    q = QImage(img.path)
    assert q.width() == 100 and not os.path.exists(img.path + ".aux.xml")
    c = q.pixelColor(50, 50)
    assert c.blue() == 255 and c.red() == 0      # la meta' blu


def test_tutto_il_file_scalato_al_lato_massimo(qgs, geotiff, tmp_path):
    layer = QgsRasterLayer(geotiff, "orto")
    img = rs.prepare_image(layer, None, layer.crs(), str(tmp_path / "a.png"), max_side=50)
    assert (img.width, img.height) == (50, 25)
    assert img.geotransform == (1000.0, 2.0, 0.0, 2000.0, 0.0, -2.0)
    assert img.extent == layer.extent()


def test_estensione_fuori_dal_raster(qgs, geotiff, tmp_path):
    layer = QgsRasterLayer(geotiff, "orto")
    with pytest.raises(ValueError):
        rs.prepare_image(layer, QgsRectangle(5000, 5000, 5100, 5100), layer.crs(), str(tmp_path / "a.png"))


def test_il_rendering_della_vista_rispetta_risoluzione_e_georeferenza(qgs, geotiff, tmp_path):
    layer = QgsRasterLayer(geotiff, "orto")
    extent = QgsRectangle(1000, 1950, 1100, 2000)
    img = rs.render_layer(layer, extent, layer.crs(), str(tmp_path / "r.png"), map_units_per_pixel=1.0)
    assert (img.width, img.height) == (100, 50) and img.source == "render"
    assert img.geotransform == (1000.0, 1.0, 0.0, 2000.0, 0.0, -1.0)
    q = QImage(img.path)
    assert q.pixelColor(10, 25).red() > 200 and q.pixelColor(90, 25).blue() > 200
    # lato massimo: la scala cresce e la georeferenza la segue
    img2 = rs.render_layer(layer, extent, layer.crs(), str(tmp_path / "r2.png"), 1.0, max_side=50)
    assert (img2.width, img2.height) == (50, 25) and img2.geotransform[1] == 2.0


def test_un_tile_vuole_un_area_e_una_risoluzione(qgs):
    xyz = QgsRasterLayer("type=xyz&url=https://tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png",
                         "osm", "wms")
    with pytest.raises(ValueError):
        rs.prepare_image(xyz, None, QgsCoordinateReferenceSystem("EPSG:3857"), "/tmp/x.png")
    with pytest.raises(ValueError):
        rs.prepare_image(xyz, QgsRectangle(0, 0, 10, 10), QgsCoordinateReferenceSystem("EPSG:3857"),
                         "/tmp/x.png", map_units_per_pixel=None)


def test_poligoni_in_pixel_tornano_in_mappa_con_i_buchi(qgs):
    gt = (1000.0, 0.5, 0.0, 2000.0, 0.0, -0.5)
    poly = {"ring": [[0, 0], [100, 0], [100, 100], [0, 100]], "holes": [[[40, 40], [60, 40], [60, 60], [40, 60]]]}
    geom = rs.polygon_to_geometry(poly, gt)
    assert geom is not None and geom.isMultipart()
    assert geom.area() == pytest.approx(50 * 50 - 10 * 10)
    bb = geom.boundingBox()
    assert (bb.xMinimum(), bb.yMaximum()) == (1000.0, 2000.0) and (bb.xMaximum(), bb.yMinimum()) == (1050.0, 1950.0)
    assert rs.polygon_to_geometry({"ring": [[0, 0], [1, 1]]}, gt) is None


def test_clip_to_area_scarta_la_cornice(qgs):
    gt = (0.0, 1.0, 0.0, 0.0, 0.0, -1.0)
    inside = rs.polygon_to_geometry({"ring": [[10, 10], [20, 10], [20, 20], [10, 20]]}, gt)
    frame = rs.polygon_to_geometry({"ring": [[0, 0], [100, 0], [100, 100], [0, 100]],
                                    "holes": [[[1, 1], [99, 1], [99, 99], [1, 99]]]}, gt)
    area = QgsGeometry.fromWkt("POLYGON((5 -5, 50 -5, 50 -50, 5 -50, 5 -5))")
    kept = rs.clip_to_area([({}, inside), ({}, frame)], area)
    assert len(kept) == 1 and kept[0][1].area() == pytest.approx(100)


def test_mask_outside_polygon_imbianca_fuori(qgs, geotiff, tmp_path):
    layer = QgsRasterLayer(geotiff, "orto")
    img = rs.prepare_image(layer, None, layer.crs(), str(tmp_path / "m.png"), max_side=4096)
    # un triangolo nella meta' sinistra (rossa)
    area = QgsGeometry.fromWkt("POLYGON((1005 1995, 1045 1995, 1025 1955, 1005 1995))")
    rs.mask_outside_polygon(img, area)
    q = QImage(img.path)
    assert q.pixelColor(50, 20).red() == 255 and q.pixelColor(50, 20).green() == 0    # dentro: rosso
    assert q.pixelColor(150, 50) == q.pixelColor(190, 90)                              # fuori: bianco
    assert q.pixelColor(150, 50).red() == 255 and q.pixelColor(150, 50).blue() == 255
