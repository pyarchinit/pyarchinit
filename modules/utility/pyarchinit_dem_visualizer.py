# -*- coding: utf-8 -*-
"""
DEM Visualization utilities for the PyArchInit Site Dashboard.

Provides persistent storage, 2D map styling, polygonization of the
intervention area and TIN mesh creation used by the Computo Metrico
feature (cut / fill volume between two DEMs).

Compatible with QGIS 3.x (Qt5) and QGIS 4.x (Qt6).

Author: Enzo Cocca
"""
from __future__ import absolute_import

import os
import re
from datetime import datetime

from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsMeshLayer,
    QgsRasterShader,
    QgsColorRampShader,
    QgsSingleBandPseudoColorRenderer,
    QgsFillSymbol,
    QgsRectangle,
)


# --------------------------------------------------------------------------- #
#                           Output directory helpers                          #
# --------------------------------------------------------------------------- #

def _sanitize(name):
    """Return a filesystem-safe version of a string (keeps Unicode letters)."""
    if not name:
        return 'site'
    # Replace path separators and anything that's not alnum/dash/underscore/dot
    safe = re.sub(r'[\\/:*?"<>|\s]+', '_', str(name))
    return safe.strip('_') or 'site'


def ensure_output_dir(sito):
    """
    Return the absolute directory where per-site dashboard artifacts are saved.

    ``${PYARCHINIT_HOME}/site_dashboard/<sanitized-sito>`` — created as needed.
    Falls back to ``~/pyarchinit/site_dashboard/<sito>`` when PYARCHINIT_HOME
    is not set.
    """
    home = os.environ.get('PYARCHINIT_HOME') or os.path.join(
        os.path.expanduser('~'), 'pyarchinit')
    out_dir = os.path.join(home, 'site_dashboard', _sanitize(sito))
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def timestamped_name(prefix, ext):
    """Return ``<prefix>_YYYYMMDD_HHMMSS.<ext>``."""
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"


# --------------------------------------------------------------------------- #
#                            DEM difference & stats                           #
# --------------------------------------------------------------------------- #

def compute_dem_difference(layer_pre, layer_post, out_path):
    """
    Run QgsRasterCalculator ``pre@1 - post@1`` using the pre-DEM's extent
    and pixel grid. Returns ``0`` on success (QGIS convention).
    """
    from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry

    extent = layer_pre.extent()
    n_cols = layer_pre.width()
    n_rows = layer_pre.height()

    e_pre = QgsRasterCalculatorEntry()
    e_pre.ref = 'pre@1'
    e_pre.raster = layer_pre
    e_pre.bandNumber = 1

    e_post = QgsRasterCalculatorEntry()
    e_post.ref = 'post@1'
    e_post.raster = layer_post
    e_post.bandNumber = 1

    calc = QgsRasterCalculator(
        'pre@1 - post@1', out_path, 'GTiff',
        extent, n_cols, n_rows, [e_pre, e_post]
    )
    return calc.processCalculation()


def compute_volume_stats(diff_layer, cut_threshold=0.01):
    """
    Iterate the raster block once and return a dictionary of stats:

    ``{'total_area_m2', 'total_volume_m3', 'cut_volume_m3',
       'fill_volume_m3', 'max_abs', 'min_value', 'max_value'}``

    - ``cut_volume`` = volume removed (diff > threshold, pre higher than post)
    - ``fill_volume`` = volume added (diff < -threshold)
    - ``total_area`` = area where |diff| > threshold
    - ``total_volume`` = sum(|diff|) * pixel_area (gross earth movement)
    """
    provider = diff_layer.dataProvider()
    extent = diff_layer.extent()
    n_cols = diff_layer.width()
    n_rows = diff_layer.height()
    pixel_area = abs(
        diff_layer.rasterUnitsPerPixelX() * diff_layer.rasterUnitsPerPixelY()
    )
    block = provider.block(1, extent, n_cols, n_rows)

    total_volume = 0.0
    cut_volume = 0.0
    fill_volume = 0.0
    total_area = 0.0
    max_abs = 0.0
    min_val = float('inf')
    max_val = float('-inf')

    for r in range(n_rows):
        for c in range(n_cols):
            if block.isNoData(r, c):
                continue
            v = block.value(r, c)
            if v is None:
                continue
            av = abs(v)
            total_volume += av * pixel_area
            if av > cut_threshold:
                total_area += pixel_area
                if v > 0:
                    cut_volume += v * pixel_area
                else:
                    fill_volume += av * pixel_area
            if av > max_abs:
                max_abs = av
            if v < min_val:
                min_val = v
            if v > max_val:
                max_val = v

    if min_val == float('inf'):
        min_val = 0.0
    if max_val == float('-inf'):
        max_val = 0.0

    return {
        'total_area_m2': total_area,
        'total_volume_m3': total_volume,
        'cut_volume_m3': cut_volume,
        'fill_volume_m3': fill_volume,
        'max_abs': max_abs,
        'min_value': min_val,
        'max_value': max_val,
    }


# --------------------------------------------------------------------------- #
#                              2D styling helpers                             #
# --------------------------------------------------------------------------- #

# RdBu diverging palette (ColorBrewer)
_DIVERGING_STOPS = [
    -1.00, -0.50, -0.10,  0.00,  0.10,  0.50, 1.00,
]
_DIVERGING_COLORS = [
    '#053061', '#2166ac', '#92c5de', '#f7f7f7',
    '#f4a582', '#b2182b', '#67001f',
]


def style_diff_raster(layer, max_abs=None):
    """
    Apply a diverging color ramp centered on zero to a DEM difference raster.

    Positive values (cut / removed material) are rendered in red,
    negative values (fill / added material) in blue.
    """
    if max_abs is None or max_abs <= 0:
        try:
            stats = layer.dataProvider().bandStatistics(1)
            mn = stats.minimumValue if stats.minimumValue is not None else 0
            mx = stats.maximumValue if stats.maximumValue is not None else 0
            max_abs = max(abs(mn), abs(mx), 0.5)
        except Exception:
            max_abs = 1.0

    items = []
    for stop, color in zip(_DIVERGING_STOPS, _DIVERGING_COLORS):
        val = stop * max_abs
        items.append(
            QgsColorRampShader.ColorRampItem(val, QColor(color), f"{val:.2f} m")
        )

    ramp_shader = QgsColorRampShader()
    # Qt6/QGIS4 uses strict enums: QgsColorRampShader.Type.Interpolated
    # Qt5/QGIS3 exposes a flat alias at QgsColorRampShader.Interpolated
    interpolated = None
    try:
        interpolated = QgsColorRampShader.Type.Interpolated
    except AttributeError:
        try:
            interpolated = QgsColorRampShader.Interpolated
        except AttributeError:
            interpolated = 0  # Interpolated == 0 in both PyQGIS versions
    try:
        ramp_shader.setColorRampType(interpolated)
    except Exception:
        pass
    ramp_shader.setColorRampItemList(items)

    shader = QgsRasterShader()
    shader.setRasterShaderFunction(ramp_shader)

    renderer = QgsSingleBandPseudoColorRenderer(
        layer.dataProvider(), 1, shader
    )
    try:
        renderer.setClassificationMin(-max_abs)
        renderer.setClassificationMax(max_abs)
    except Exception:
        pass

    layer.setRenderer(renderer)
    layer.triggerRepaint()


def style_cut_polygon(layer):
    """Semi-transparent red hatched fill for the intervention polygon."""
    try:
        sym = QgsFillSymbol.createSimple({
            'color': '230,74,25,70',
            'outline_color': '198,40,40',
            'outline_width': '0.6',
            'outline_style': 'solid',
            'style': 'solid',
        })
        layer.renderer().setSymbol(sym)
        layer.triggerRepaint()
    except Exception:
        pass


# --------------------------------------------------------------------------- #
#                          Polygonize intervention area                        #
# --------------------------------------------------------------------------- #

def polygonize_cut_area(diff_raster_path, out_vector_path, threshold=0.01):
    """
    Vectorize the area where ``|diff| > threshold`` into a polygon layer.

    Uses ``gdal:rastercalculator`` + ``gdal:polygonize`` via QGIS processing.
    Returns the path on success, ``None`` on failure.
    """
    try:
        import processing
    except ImportError:
        return None

    mask_tmp = os.path.splitext(out_vector_path)[0] + '_mask.tif'

    try:
        processing.run('gdal:rastercalculator', {
            'INPUT_A': diff_raster_path,
            'BAND_A': 1,
            'FORMULA': f'(abs(A) > {threshold}) * 1',
            'NO_DATA': 0,
            'RTYPE': 0,  # Byte
            'OPTIONS': '',
            'EXTRA': '',
            'OUTPUT': mask_tmp,
        })
    except Exception:
        return None

    try:
        processing.run('gdal:polygonize', {
            'INPUT': mask_tmp,
            'BAND': 1,
            'FIELD': 'DN',
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'OUTPUT': out_vector_path,
        })
    except Exception:
        try:
            os.remove(mask_tmp)
        except OSError:
            pass
        return None

    try:
        os.remove(mask_tmp)
    except OSError:
        pass

    if not os.path.exists(out_vector_path):
        return None
    return out_vector_path


# --------------------------------------------------------------------------- #
#                       QGIS project / layer tree helpers                     #
# --------------------------------------------------------------------------- #

GROUP_NAME_IT = 'Cruscotto Cantiere - Computi'
GROUP_NAME_EN = 'Site Dashboard - Computi'


def add_layer_to_group(layer, group_name=None, expanded=True):
    """Insert ``layer`` into ``QgsProject`` under a dedicated layer-tree group."""
    if layer is None or not layer.isValid():
        return None
    name = group_name or GROUP_NAME_EN
    QgsProject.instance().addMapLayer(layer, False)
    root = QgsProject.instance().layerTreeRoot()
    group = root.findGroup(name)
    if not group:
        group = root.insertGroup(0, name)
        group.setExpanded(expanded)
    group.insertLayer(0, layer)
    return group


def zoom_canvas_to(iface, rect):
    """Zoom the main map canvas to the given QgsRectangle + refresh."""
    try:
        if iface is None or rect is None or rect.isEmpty():
            return
        buffered = QgsRectangle(rect)
        buffered.scale(1.05)
        canvas = iface.mapCanvas()
        canvas.setExtent(buffered)
        canvas.refresh()
    except Exception:
        pass


# --------------------------------------------------------------------------- #
#                        Raster clipping (polygon mask)                       #
# --------------------------------------------------------------------------- #

def _write_polygon_to_temp_shp(poly_layer, target_crs=None):
    """
    Export a ``QgsVectorLayer`` (including memory layers) to a temporary
    ESRI Shapefile so that ``gdal.Warp`` can use it as a cutline.

    If ``target_crs`` is supplied, every feature is reprojected into
    that CRS in Python using ``QgsCoordinateTransform`` **before** the
    shapefile is written — avoiding any need for GDAL to resolve the
    polygon's native CRS by authid. This is essential for custom CRSs
    like the Turkish "TUREF / TM36" definition used on Kültepe, which
    has no EPSG code registered and makes QGIS log
    ``No transform available between TUREF / TM36 and EPSG:4326``.

    Returns ``(shp_path, temp_dir)`` or ``(None, None)`` on failure.
    The caller is responsible for removing ``temp_dir``.
    """
    import tempfile
    try:
        from qgis.core import (
            QgsProject,
            QgsVectorFileWriter,
            QgsCoordinateTransformContext,
            QgsCoordinateTransform,
            QgsVectorLayer,
            QgsFeature,
            QgsGeometry,
        )
    except ImportError:
        return None, None

    tmp_dir = tempfile.mkdtemp(prefix='pyarch_clip_')
    shp_path = os.path.join(tmp_dir, 'cutline.shp')

    # If asked to reproject, build a memory layer in the target CRS
    # and copy features across (transforming geometries). Writing the
    # memory layer then guarantees the .prj file matches the DEM CRS.
    source_layer = poly_layer
    if target_crs is not None and poly_layer.crs() != target_crs:
        try:
            xform = QgsCoordinateTransform(
                poly_layer.crs(), target_crs, QgsProject.instance())
            uri = f'Polygon?crs={target_crs.toWkt()}'
            mem = QgsVectorLayer(uri, 'pyarch_cutline_reproj', 'memory')
            mem_prov = mem.dataProvider()
            # Copy fields (optional but keeps the writer happy)
            try:
                mem_prov.addAttributes(poly_layer.fields())
                mem.updateFields()
            except Exception:
                pass
            feats_out = []
            for f in poly_layer.getFeatures():
                g = QgsGeometry(f.geometry())
                try:
                    g.transform(xform)
                except Exception:
                    continue
                nf = QgsFeature(mem.fields())
                nf.setGeometry(g)
                try:
                    nf.setAttributes(f.attributes())
                except Exception:
                    pass
                feats_out.append(nf)
            mem_prov.addFeatures(feats_out)
            mem.updateExtents()
            source_layer = mem
        except Exception:
            # Fall back to writing the original layer; GDAL may still
            # manage the transform if the CRS authid resolves.
            source_layer = poly_layer

    # Try the modern API first (QGIS 3.20+)
    written = False
    try:
        opts = QgsVectorFileWriter.SaveVectorOptions()
        opts.driverName = 'ESRI Shapefile'
        writer_fn = getattr(QgsVectorFileWriter, 'writeAsVectorFormatV3', None) \
            or getattr(QgsVectorFileWriter, 'writeAsVectorFormatV2', None)
        if writer_fn is not None:
            writer_fn(source_layer, shp_path,
                       QgsCoordinateTransformContext(), opts)
            written = True
    except Exception:
        written = False

    # Legacy fallback (deprecated but still functional)
    if not written:
        try:
            QgsVectorFileWriter.writeAsVectorFormat(
                source_layer, shp_path, 'UTF-8',
                driverName='ESRI Shapefile',
            )
            written = True
        except Exception:
            written = False

    if not written or not os.path.exists(shp_path):
        import shutil
        try:
            shutil.rmtree(tmp_dir)
        except OSError:
            pass
        return None, None
    return shp_path, tmp_dir


def _clean_raster_path(path):
    """
    Strip any ``|layername=...`` or ``|layerid=...`` suffix from a layer
    source URI so ``gdal.Open`` / ``gdal.Warp`` can consume it directly.
    """
    if not path:
        return path
    # Some providers use the "?" separator for GPKG/WMS/etc.
    for sep in ('|', '?'):
        if sep in path:
            path = path.split(sep, 1)[0]
    return path


def clip_raster_by_polygon(raster_path, poly_layer, out_path,
                            dst_nodata=-9999,
                            target_x_res=None, target_y_res=None,
                            target_bounds=None):
    """
    Clip a raster to a polygon layer using ``gdal.Warp`` with a
    temporary cutline shapefile.

    Returns ``(out_path, None)`` on success, ``(None, error_message)``
    on failure. Safe in all QGIS profiles: does not rely on the
    ``processing`` framework.

    Handles:
      - layer source URIs with ``|layername=...`` suffixes (GPKG, ...)
      - polygon layers in a different CRS than the raster (passes
        ``cutlineSRS``)
      - memory vector layers (exported via
        ``QgsVectorFileWriter`` to a temp shapefile)

    The optional ``target_x_res`` / ``target_y_res`` / ``target_bounds``
    parameters force the output raster onto a specific pixel grid —
    pass the same values to both the pre and post DEM clips so the two
    outputs are perfectly aligned and can be subtracted by
    ``QgsRasterCalculator`` without resampling artefacts.
    """
    try:
        from osgeo import gdal
    except ImportError:
        try:
            import gdal  # older layout
        except ImportError:
            return None, 'GDAL python bindings not available'

    clean_src = _clean_raster_path(raster_path)
    if not clean_src:
        return None, 'empty source raster path'
    if not os.path.exists(clean_src):
        return None, f'source raster not found: {clean_src}'

    # Discover the raster CRS as a QgsCoordinateReferenceSystem so we
    # can reproject the polygon into exactly the same CRS using
    # QgsCoordinateTransform — much more robust than relying on
    # gdal.Warp to resolve custom CRSs (TUREF / TM36 etc.) by authid.
    raster_qgs_crs = None
    raster_srs = None
    try:
        r_ds_probe = gdal.Open(clean_src)
        if r_ds_probe is not None:
            proj = r_ds_probe.GetProjection()
            if proj:
                raster_srs = proj
                try:
                    from qgis.core import QgsCoordinateReferenceSystem
                    raster_qgs_crs = QgsCoordinateReferenceSystem()
                    raster_qgs_crs.createFromWkt(proj)
                    if not raster_qgs_crs.isValid():
                        raster_qgs_crs = None
                except Exception:
                    raster_qgs_crs = None
            r_ds_probe = None
    except Exception:
        pass

    shp_path, tmp_dir = _write_polygon_to_temp_shp(
        poly_layer, target_crs=raster_qgs_crs)
    if shp_path is None:
        return None, 'failed to export polygon to a temporary shapefile'

    # Because the polygon has already been reprojected into the raster
    # CRS, we can tell gdal.Warp the cutline is in the same CRS as the
    # destination — no authid lookup, no "no transform available"
    # errors from QGIS.
    cutline_srs = None

    import shutil
    warp_result = None
    err = None
    try:
        # Enable exceptions so silent failures become catchable
        try:
            gdal.UseExceptions()
        except Exception:
            pass
        warp_opts = dict(
            cutlineDSName=shp_path,
            cropToCutline=True,
            dstNodata=dst_nodata,
            format='GTiff',
            multithread=True,
        )
        if cutline_srs:
            warp_opts['cutlineSRS'] = cutline_srs
        if raster_srs:
            warp_opts['dstSRS'] = raster_srs
        # Force a specific pixel grid so the pre/post clips can be
        # subtracted cell-by-cell without resampling artefacts.
        if target_x_res is not None and target_y_res is not None:
            warp_opts['xRes'] = abs(float(target_x_res))
            warp_opts['yRes'] = abs(float(target_y_res))
            warp_opts['targetAlignedPixels'] = True
        if target_bounds is not None:
            warp_opts['outputBounds'] = tuple(target_bounds)
            # cropToCutline overrides outputBounds; disable it when
            # the caller provided explicit bounds.
            warp_opts['cropToCutline'] = False
        warp_result = gdal.Warp(out_path, clean_src, **warp_opts)
        # gdal.Warp returns a Dataset on success, None on failure
        if warp_result is None:
            err = 'gdal.Warp returned None (empty intersection or ' \
                  'incompatible CRS)'
        else:
            warp_result = None  # close dataset
    except Exception as e:
        err = f'gdal.Warp exception: {e}'
    finally:
        try:
            shutil.rmtree(tmp_dir)
        except OSError:
            pass

    if err is not None:
        return None, err
    if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
        return None, 'output file not written or empty'
    return out_path, None


def exclude_polygons_from_raster(raster_path, poly_layer, nodata_value=-9999):
    """
    Burn the features of ``poly_layer`` into ``raster_path`` using
    ``nodata_value``, effectively removing those areas from any
    downstream volume calculation. Modifies the raster in place.

    Used by the Computo Metrico workflow to subtract walls / built
    structures from the excavation volume: the wall polygons are
    rasterised onto the (already-clipped) DEM-difference raster, and
    the burned cells become NODATA so ``compute_volume_stats`` skips
    them.

    Returns ``(True, None)`` on success, ``(False, error)`` otherwise.
    """
    try:
        from osgeo import gdal
    except ImportError:
        try:
            import gdal  # older layout
        except ImportError:
            return False, 'GDAL python bindings not available'

    if not os.path.exists(raster_path):
        return False, f'raster not found: {raster_path}'

    shp_path, tmp_dir = _write_polygon_to_temp_shp(poly_layer)
    if shp_path is None:
        return False, 'failed to export wall polygon layer'

    import shutil
    err = None
    try:
        try:
            gdal.UseExceptions()
        except Exception:
            pass
        # Open the raster for update and set its nodata value first
        try:
            ds = gdal.Open(raster_path, gdal.GA_Update)
            if ds is not None:
                band = ds.GetRasterBand(1)
                try:
                    band.SetNoDataValue(float(nodata_value))
                except Exception:
                    pass
                ds = None
        except Exception:
            pass
        gdal.Rasterize(
            raster_path,                # destination (in-place update)
            shp_path,
            burnValues=[float(nodata_value)],
            allTouched=True,
        )
    except Exception as e:
        err = f'gdal.Rasterize exception: {e}'
    finally:
        try:
            shutil.rmtree(tmp_dir)
        except OSError:
            pass

    if err is not None:
        return False, err
    return True, None


# --------------------------------------------------------------------------- #
#                   TIN / 2DM mesh generation  (Level 3)                      #
# --------------------------------------------------------------------------- #

def create_tin_mesh_from_dem(dem_layer, out_mesh_path,
                              max_cells=15000, clip_poly_layer=None):
    """
    Convert a DEM raster into a regular-grid 2DM mesh using a pure
    Python writer.

    Earlier versions of this function invoked ``native:pixelstopoints``
    + ``native:tinmeshcreation`` via the QGIS Processing framework,
    which crashed QGIS on some builds. The new implementation:

      1. Reads the DEM directly with GDAL (no Processing).
      2. Downsamples in-memory with NumPy if the grid exceeds ``max_cells``.
      3. Writes a 2DM mesh file manually: one quad (``E4Q``) per valid
         DEM cell, nodes at pixel centres.

    Because no processing algorithm is invoked, this is safe across
    all QGIS versions and never triggers a segfault.

    If ``clip_poly_layer`` is set, only cells whose centre lies inside
    the polygon (via a pre-clipped GDAL warp) are kept — the mesh then
    represents the excavation area only.
    """
    try:
        from osgeo import gdal
    except ImportError:
        try:
            import gdal  # type: ignore
        except ImportError:
            return None

    try:
        import numpy as np
    except ImportError:
        return None

    # Optionally clip the source DEM by polygon first (safer: we read
    # the clipped raster so the mesh covers only the requested region).
    cleanup_paths = []
    raw_src = dem_layer.source() if hasattr(dem_layer, 'source') \
        else str(dem_layer)
    src_path = _clean_raster_path(raw_src)

    if clip_poly_layer is not None:
        tmp_clipped = os.path.splitext(out_mesh_path)[0] + '_src_clipped.tif'
        clipped, _clip_err = clip_raster_by_polygon(
            src_path, clip_poly_layer, tmp_clipped)
        if clipped:
            src_path = clipped
            cleanup_paths.append(clipped)

    ds = gdal.Open(src_path)
    if ds is None:
        _cleanup(cleanup_paths)
        return None

    try:
        band = ds.GetRasterBand(1)
        arr = band.ReadAsArray().astype('float64')
        nodata = band.GetNoDataValue()
        gt = ds.GetGeoTransform()  # (x0, pw, 0, y0, 0, ph)
    except Exception:
        ds = None
        _cleanup(cleanup_paths)
        return None
    ds = None

    if arr is None or arr.size == 0:
        _cleanup(cleanup_paths)
        return None

    n_rows, n_cols = arr.shape
    x0, pw, _, y0, _, ph = gt  # ph is usually negative

    # Downsample to stay within max_cells
    if n_rows * n_cols > max_cells:
        import math
        factor = int(math.ceil(math.sqrt(n_rows * n_cols / float(max_cells))))
        arr = arr[::factor, ::factor]
        pw *= factor
        ph *= factor
        n_rows, n_cols = arr.shape

    # Mark nodata as NaN
    if nodata is not None:
        arr = np.where(arr == nodata, np.nan, arr)
        arr = np.where(arr == -9999, np.nan, arr)

    valid = ~np.isnan(arr)
    if not np.any(valid):
        _cleanup(cleanup_paths)
        return None

    # Fallback Z for nodata cells (used only to keep the mesh closed)
    fill_z = float(np.nanmin(arr)) - 1.0

    # Write the 2DM file
    try:
        with open(out_mesh_path, 'w', encoding='ascii') as f:
            f.write('MESH2D\n')
            # Nodes: one per DEM cell centre, numbered 1..(n_rows*n_cols)
            # Use a flat index: nid = r * n_cols + c + 1
            for r in range(n_rows):
                y = y0 + (r + 0.5) * ph   # pixel centre Y (ph < 0)
                for c in range(n_cols):
                    x = x0 + (c + 0.5) * pw
                    z = arr[r, c]
                    if np.isnan(z):
                        z = fill_z
                    nid = r * n_cols + c + 1
                    f.write(f'ND {nid} {x:.4f} {y:.4f} {z:.4f}\n')

            # Elements: one E4Q (quad) per 2x2 node group, but only if
            # all four corners were valid in the source DEM.
            eid = 0
            for r in range(n_rows - 1):
                for c in range(n_cols - 1):
                    if not (valid[r, c] and valid[r, c + 1]
                            and valid[r + 1, c] and valid[r + 1, c + 1]):
                        continue
                    n1 = r * n_cols + c + 1
                    n2 = r * n_cols + (c + 1) + 1
                    n3 = (r + 1) * n_cols + (c + 1) + 1
                    n4 = (r + 1) * n_cols + c + 1
                    eid += 1
                    # E4Q id n1 n2 n3 n4 mat_id
                    f.write(f'E4Q {eid} {n1} {n2} {n3} {n4} 1\n')
            if eid == 0:
                # No valid cells — mesh would be empty
                raise ValueError('no valid cells')
    except Exception:
        try:
            os.remove(out_mesh_path)
        except OSError:
            pass
        _cleanup(cleanup_paths)
        return None

    _cleanup(cleanup_paths)
    if not os.path.exists(out_mesh_path):
        return None
    return out_mesh_path


def _cleanup(paths):
    for p in paths or []:
        if p and os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass


def load_mesh_layer(mesh_path, name):
    """
    Load a 2DM mesh file as a ``QgsMeshLayer``.

    Historical note: previous versions also applied an automatic scalar
    renderer via ``_style_mesh_terrain``. That path was dropped because
    calling ``QgsMeshRendererScalarSettings`` APIs from Python triggers
    a segfault on several QGIS builds (the signatures are unstable
    across minor versions). The caller is responsible for styling the
    mesh, or — preferably — for visualising the DEM directly via the
    matplotlib 3D fallback without ever creating a mesh layer.
    """
    try:
        layer = QgsMeshLayer(mesh_path, name, 'mdal')
    except Exception:
        return None
    if layer is None or not layer.isValid():
        return None
    return layer


def _style_mesh_terrain(mesh_layer):
    """
    Apply a scalar renderer on the first dataset group (Bed Elevation)
    of ``mesh_layer`` using a terrain color ramp. Fails silently when
    the QGIS mesh API is not available in the running QGIS version.
    """
    from qgis.core import (
        QgsMeshDatasetIndex,
        QgsMeshRendererScalarSettings,
    )
    # Find a dataset group to render (bed elevation is usually index 0)
    provider = mesh_layer.dataProvider()
    group_count = provider.datasetGroupCount()
    if group_count == 0:
        return
    group_idx = 0

    # Determine scalar min / max
    dataset_index = QgsMeshDatasetIndex(group_idx, 0)
    meta = provider.datasetGroupMetadata(group_idx)
    try:
        mn = meta.minimum()
        mx = meta.maximum()
    except Exception:
        mn = 0.0
        mx = 1.0
    if mn == mx:
        mx = mn + 1.0

    # Build a color ramp shader (terrain-ish gradient)
    stops = [
        (0.00, '#006837'),
        (0.25, '#1a9850'),
        (0.50, '#fdae61'),
        (0.75, '#d73027'),
        (1.00, '#7f3b08'),
    ]
    items = []
    for frac, color in stops:
        val = mn + frac * (mx - mn)
        items.append(
            QgsColorRampShader.ColorRampItem(val, QColor(color), f"{val:.2f}")
        )

    ramp_shader = QgsColorRampShader()
    try:
        ramp_shader.setColorRampType(QgsColorRampShader.Type.Interpolated)
    except AttributeError:
        try:
            ramp_shader.setColorRampType(QgsColorRampShader.Interpolated)
        except Exception:
            pass
    ramp_shader.setColorRampItemList(items)
    try:
        ramp_shader.setMinimumValue(mn)
        ramp_shader.setMaximumValue(mx)
    except Exception:
        pass

    shader = QgsRasterShader()
    shader.setRasterShaderFunction(ramp_shader)
    # Some API versions expose min/max on the shader itself
    try:
        shader.setMinimumValue(mn)
        shader.setMaximumValue(mx)
    except Exception:
        pass

    # Configure the mesh scalar renderer
    scalar = QgsMeshRendererScalarSettings()
    try:
        scalar.setColorRampShader(ramp_shader)
    except Exception:
        pass
    try:
        scalar.setClassificationMinimumMaximum(mn, mx)
    except Exception:
        pass

    # Apply to the layer's renderer settings
    renderer_settings = mesh_layer.rendererSettings()
    try:
        renderer_settings.setActiveScalarDatasetGroup(group_idx)
    except Exception:
        pass
    try:
        renderer_settings.setScalarSettings(group_idx, scalar)
    except Exception:
        pass
    try:
        mesh_layer.setRendererSettings(renderer_settings)
    except Exception:
        pass

    # Also try to set the current active dataset
    try:
        mesh_layer.setStaticScalarDatasetIndex(dataset_index)
    except Exception:
        pass
    try:
        mesh_layer.triggerRepaint()
    except Exception:
        pass
