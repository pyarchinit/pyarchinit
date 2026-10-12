"""Pannello GeoArchaeo e algoritmi Processing, headless (serve il Python di QGIS).

Copia adattata dei test di GeoArchaeo 1.3.1 (repository enzococca/GeoArchaeo,
`tests/test_dock_headless.py`): il modulo `modules/geoarchaeo/` e' una copia fedele di quel
plugin, e questi test vanno tenuti allineati a ogni aggiornamento.
Cambiano solo gli import (il pacchetto qui e' `modules.geoarchaeo`) e la
fixture di QgsApplication, condivisa con gli altri test di pyArchInit.
"""
import os
import sys
import time
from pathlib import Path

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if sys.platform == "darwin" and os.path.isdir("/Applications/QGIS.app/Contents/Resources/proj"):
    os.environ.setdefault("PROJ_LIB", "/Applications/QGIS.app/Contents/Resources/proj")   # riproiezioni
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
for _cand in ('/Applications/QGIS.app/Contents/Resources/python/plugins',
              '/usr/share/qgis/python/plugins'):
    if os.path.isdir(_cand) and _cand not in sys.path:
        sys.path.append(_cand)       # modulo `processing` di QGIS
qgis_core = pytest.importorskip('qgis.core')
from qgis.core import (  # noqa: E402
    QgsApplication, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsProject,
    QgsRasterLayer, QgsProcessingContext, QgsProcessingFeedback)
from qgis.PyQt.QtCore import QDateTime  # noqa: E402

import modules.geoarchaeo.gui.main_dock as main_dock  # noqa: E402
from modules.geoarchaeo.gui.main_dock import GeoArchaeoDockWidget  # noqa: E402
from modules.geoarchaeo.i18n import set_language, tr  # noqa: E402
from modules.geoarchaeo.compat import attribute_to_float  # noqa: E402


@pytest.fixture(scope='module')
def app():
    """QgsApplication condivisa con il resto della suite: mai exitQgis() qui."""
    application = QgsApplication.instance()
    if application is None:
        QgsApplication.setPrefixPath(
            os.environ.get('QGIS_PREFIX_PATH', '/Applications/QGIS.app/Contents/MacOS'), True)
        application = QgsApplication([], False)
        application.initQgis()
    return application


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """Nessuna finestra modale nei test."""
    messages = []
    monkeypatch.setattr(main_dock.QMessageBox, 'warning', lambda *a, **k: messages.append(('warning', a[2])))
    monkeypatch.setattr(main_dock.QMessageBox, 'critical', lambda *a, **k: messages.append(('critical', a[2])))
    monkeypatch.setattr(main_dock, 'question_yes_no', lambda *a, **k: True)
    return messages


@pytest.fixture
def project():
    QgsProject.instance().removeAllMapLayers()
    yield QgsProject.instance()
    QgsProject.instance().removeAllMapLayers()


def make_layer(name='pts', n=120, seed=0, nulls=5, value_fn=None):
    rng = np.random.default_rng(seed)
    layer = QgsVectorLayer("Point?crs=EPSG:32633&field=v:double&field=cat:string&field=w:integer", name, "memory")
    provider = layer.dataProvider()
    feats = []
    for i in range(n):
        x, y = rng.uniform(0, 100, 2)
        feat = QgsFeature(layer.fields())
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
        if i < nulls:
            value = None
        elif value_fn is not None:
            value = float(value_fn(x, y))
        else:
            value = float(10 + 0.05 * x + rng.normal())
        feat.setAttributes([value, 'a' if x < 50 else 'b', int(i)])
        feats.append(feat)
    provider.addFeatures(feats)
    layer.updateExtents()
    return layer


def make_polygon_layer():
    layer = QgsVectorLayer("Polygon?crs=EPSG:32633", "area", "memory")
    feat = QgsFeature()
    feat.setGeometry(QgsGeometry.fromWkt("POLYGON((20 20, 80 20, 80 80, 20 80, 20 20))"))
    layer.dataProvider().addFeatures([feat])
    layer.updateExtents()
    return layer


def wait_thread(app, dock, timeout=180):
    start = time.time()
    while dock.analysis_thread is not None and dock.analysis_thread.isRunning():
        app.processEvents()
        time.sleep(0.02)
        if time.time() - start > timeout:
            raise TimeoutError('analysis did not finish')
    for _ in range(30):
        app.processEvents()
        time.sleep(0.005)


def make_dock(app, layer, field='v'):
    dock = GeoArchaeoDockWidget(None)
    app.processEvents()
    dock.layer_combo.setLayer(layer)
    dock.field_combo.setField(field)
    app.processEvents()
    return dock


# ----------------------------------------------------------------------
def test_attribute_to_float_handles_null(app, project):
    layer = make_layer(n=3, nulls=1)
    values = [attribute_to_float(f['v']) for f in layer.getFeatures()]
    assert values[0] is None and all(isinstance(v, float) for v in values[1:])
    assert attribute_to_float('12,5') == 12.5
    assert attribute_to_float('abc') is None


def test_dock_full_workflow(app, project, no_modal_dialogs):
    set_language('it')
    layer = make_layer(n=150, value_fn=lambda x, y: 100 + y)   # valore cresce verso nord
    project.addMapLayer(layer)
    dock = make_dock(app, layer)

    # intestazione: riepilogo del layer e valori di default suggeriti
    assert '145' in dock.layer_summary_label.text() and '150' in dock.layer_summary_label.text()
    assert dock.max_dist_spin.value() > 0
    assert 0 < dock.resolution_spin.value() <= 2
    assert tr('variogram_status_none')[:20] in dock.variogram_status_label.text()

    # 1. statistiche (NULL esclusi, nessun crash)
    dock._run_eda()
    stats = dock.current_results['stats']['stats']
    assert stats['n'] == 145 and stats['missing'] == 5
    assert 'stats' in dock.current_results
    assert dock.report_checks['stats'].isEnabled()
    assert not dock.report_checks['kriging'].isEnabled()

    # 2. variogramma
    dock.anisotropy_check.setChecked(True)
    dock._calculate_variogram()
    wait_thread(app, dock)
    vg = dock.current_results['variogram']
    assert vg['model_params']['range'] > 0 and vg['anisotropy'] is not None
    assert dock.variogram_result_label.isVisible() or dock.variogram_result_label.text()
    assert '✓' in dock.variogram_status_label.text()
    if not main_dock.WEBENGINE_AVAILABLE:
        assert dock.variogram_plot._pixmap is not None
    assert dock.variogram_plot.browser_btn.isEnabled()

    # 3. kriging (usa il variogramma, crea i raster)
    dock.resolution_spin.setValue(2.0)
    assert '50 × 50' in dock.grid_info_label.text()
    dock._run_kriging()
    wait_thread(app, dock)
    kr = dock.current_results['kriging']
    assert kr['predictions'].shape == (50, 50)
    assert kr['cv_results'] is not None and kr['cv_results']['r2'] > 0.9
    names = [l.name() for l in project.mapLayers().values()]
    assert 'Kriging_v' in names and 'Kriging_v_incertezza' in names
    raster = [l for l in project.mapLayers().values() if l.name() == 'Kriging_v'][0]
    assert isinstance(raster, QgsRasterLayer) and raster.isValid()
    assert raster.width() == 50 and raster.height() == 50
    # orientamento: il valore a nord deve essere maggiore di quello a sud
    south = raster.dataProvider().sample(QgsPointXY(50, 5), 1)[0]
    north = raster.dataProvider().sample(QgsPointXY(50, 95), 1)[0]
    assert north > south + 50
    assert abs(raster.extent().xMinimum() - layer.extent().xMinimum()) < 1e-6
    assert 'R²' in dock.kriging_result_label.text()

    # 4. report con tutte le sezioni disponibili
    html = dock.build_report_html(['stats', 'variogram', 'kriging'], embed_plots=True)
    assert tr('section_stats') in html and tr('section_kriging') in html
    assert 'plotly' in html.lower()
    preview = dock.build_report_html(['stats', 'variogram', 'kriging'], embed_plots=False)
    assert 'plotly' not in preview.lower()

    # cambio lingua: etichette aggiornate, risultati mantenuti
    dock._change_language(1)
    assert dock.tabs.tabText(0) == 'Data'
    assert 'Kriging completed' in dock.kriging_result_label.text()
    dock._change_language(0)
    assert dock.tabs.tabText(0) == 'Dati'
    assert not [m for m in no_modal_dialogs if m[0] == 'critical']
    dock.cleanup()


def test_dock_ml_and_sampling(app, project, no_modal_dialogs):
    set_language('en')
    layer = make_layer(n=100, nulls=0, seed=3)
    polygon = make_polygon_layer()
    project.addMapLayers([layer, polygon])
    dock = make_dock(app, layer)

    # il layer corrente e' preselezionato nella lista ML
    assert any(dock.ml_layers.item(i).isSelected() for i in range(dock.ml_layers.count()))
    dock.ml_method.setCurrentIndex(0)
    dock.ml_clusters_spin.setValue(3)
    dock._run_ml()
    wait_thread(app, dock)
    ml = dock.current_results['ml']
    assert ml['n_clusters'] == 3
    ml_layer = [l for l in project.mapLayers().values() if l.name() == tr('ml_clusters_layer')][0]
    assert ml_layer.featureCount() == 100
    assert 'cluster_name' in [f.name() for f in ml_layer.fields()]

    dock.ml_method.setCurrentIndex(2)   # isolation forest
    dock._run_ml()
    wait_thread(app, dock)
    assert tr('ml_anomalies_layer') in [l.name() for l in project.mapLayers().values()]

    # campionamento con area di studio
    dock.boundary_combo.setLayer(polygon)
    dock.n_points_spin.setValue(8)
    for idx in range(dock.sampling_combo.count()):
        dock.sampling_combo.setCurrentIndex(idx)
        dock._run_sampling_design()
        wait_thread(app, dock)
        pts = dock.current_results['sampling']['points']
        assert pts.shape == (8, 2), dock.sampling_combo.currentText()
        assert np.all((pts >= 20) & (pts <= 80)), dock.sampling_combo.currentText()
    sampling_layer = [l for l in project.mapLayers().values() if l.name() == tr('sampling_points_layer')]
    assert sampling_layer and sampling_layer[-1].featureCount() == 8
    assert not [m for m in no_modal_dialogs if m[0] == 'critical']
    dock.cleanup()


def test_dock_warnings_without_data(app, project, no_modal_dialogs):
    set_language('en')
    dock = GeoArchaeoDockWidget(None)
    app.processEvents()
    assert tr('no_layer_selected') in dock.layer_summary_label.text()
    dock._run_eda()
    dock._calculate_variogram()
    dock._run_kriging()
    assert len(no_modal_dialogs) == 3 and all(m[0] == 'warning' for m in no_modal_dialogs)
    layer = make_layer(n=10, nulls=10)
    project.addMapLayer(layer)
    dock.layer_combo.setLayer(layer)
    dock.field_combo.setField('v')
    dock._run_eda()
    assert no_modal_dialogs[-1][0] == 'warning'
    dock.cleanup()


def test_example_data_available(app, project, no_modal_dialogs):
    set_language('en')
    dock = GeoArchaeoDockWidget(None)
    files = dock._example_files(dock.example_dir)
    assert any(f.endswith('villa_ceramica.gpkg') for f in files)
    loaded = dock.load_example_files([f for f in files if f.endswith('villa_ceramica.gpkg')])
    assert len(loaded) == 1
    layer = loaded[0]
    numeric = [f.name() for f in layer.fields() if f.isNumeric()]
    assert 'ceramic_count' in numeric, "example GPKG must have numeric fields"
    assert dock.layer_combo.currentLayer() is not None and dock.layer_combo.currentLayer().id() == layer.id()
    dock.cleanup()


# ----------------------------------------------------------------------
# Processing
# ----------------------------------------------------------------------
@pytest.fixture(scope='module')
def processing_ready(app):
    try:
        from processing.core.Processing import Processing
    except ImportError:
        pytest.skip('QGIS processing framework not importable')
    Processing.initialize()
    from modules.geoarchaeo.processing_provider import GeoArchaeoProvider
    from modules.geoarchaeo.core.geostat_engine import GeostatEngine
    provider = GeoArchaeoProvider(GeostatEngine())
    QgsApplication.processingRegistry().addProvider(provider)
    return provider


def run_alg(alg_id, params):
    import processing
    return processing.run(alg_id, params, context=QgsProcessingContext(), feedback=QgsProcessingFeedback())


def test_processing_variogram_and_kriging(app, project, processing_ready, tmp_path):
    layer = make_layer(n=120, nulls=3, value_fn=lambda x, y: 100 + y)
    project.addMapLayer(layer)
    vg_path = str(tmp_path / 'vg.json')
    res = run_alg('geoarchaeo:variogram', {'INPUT': layer, 'FIELD': 'v', 'MAX_DISTANCE': 0, 'MODEL': 0,
                                           'ANISOTROPY': True, 'OUTPUT': vg_path})
    assert os.path.exists(res['OUTPUT']) and res['RANGE'] > 0
    import json
    data = json.load(open(vg_path))
    assert data['model_params']['sill'] > 0 and data['anisotropy'] is not None

    out = str(tmp_path / 'ok.tif')
    var = str(tmp_path / 'ok_std.tif')
    res = run_alg('geoarchaeo:ordinarykriging', {'INPUT': layer, 'FIELD': 'v', 'PIXEL_SIZE': 2.0,
                                                 'VARIOGRAM': vg_path, 'OUTPUT': out, 'OUTPUT_VARIANCE': var})
    raster = QgsRasterLayer(res['OUTPUT'], 'ok')
    assert raster.isValid() and raster.width() == 50 and raster.height() == 50
    south = raster.dataProvider().sample(QgsPointXY(50, 5), 1)[0]
    north = raster.dataProvider().sample(QgsPointXY(50, 95), 1)[0]
    assert north > south + 50
    assert QgsRasterLayer(var, 'std').isValid()
    assert res['CV_R2'] > 0.9


def test_processing_cokriging_st_batch_compositional(app, project, processing_ready, tmp_path):
    primary = make_layer('primary', n=40, nulls=0, seed=5, value_fn=lambda x, y: 5 + 0.2 * x)
    secondary = make_layer('secondary', n=400, nulls=0, seed=6, value_fn=lambda x, y: 0.1 * x)
    project.addMapLayers([primary, secondary])
    res = run_alg('geoarchaeo:cokriging', {'PRIMARY': primary, 'PRIMARY_FIELD': 'v', 'SECONDARY': [secondary],
                                           'SECONDARY_FIELDS': 'v', 'PIXEL_SIZE': 5.0,
                                           'OUTPUT': str(tmp_path / 'ck.tif')})
    assert QgsRasterLayer(res['OUTPUT'], 'ck').isValid() and res['REGRESSION_R2'] > 0.95

    res = run_alg('geoarchaeo:batchkriging', {'INPUT': secondary, 'FIELD': 'v', 'PIXEL_SIZE': 2.0,
                                              'TILE_SIZE': 40, 'OVERLAP': 20, 'MAX_POINTS_PER_TILE': 500,
                                              'OUTPUT': str(tmp_path / 'batch.tif')})
    assert QgsRasterLayer(res['OUTPUT'], 'batch').isValid()

    # composizionale: 3 campi che sommano a 100
    comp = QgsVectorLayer("Point?crs=EPSG:32633&field=sand:double&field=silt:double&field=clay:double", "comp", "memory")
    rng = np.random.default_rng(7)
    feats = []
    for _ in range(40):
        x, y = rng.uniform(0, 100, 2)
        sand = 30 + 0.4 * x
        silt = 70 - 0.4 * x - 10
        feat = QgsFeature(comp.fields())
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
        feat.setAttributes([sand, silt, 100 - sand - silt])
        feats.append(feat)
    comp.dataProvider().addFeatures(feats)
    comp.updateExtents()
    project.addMapLayer(comp)
    res = run_alg('geoarchaeo:compositional', {'INPUT': comp, 'COMP_FIELDS': ['sand', 'silt', 'clay'], 'TRANSFORM': 1,
                                               'PIXEL_SIZE': 5.0, 'OUTPUT': str(tmp_path / 'comp.tif')})
    raster = QgsRasterLayer(res['OUTPUT'], 'comp')
    assert raster.isValid() and raster.bandCount() == 2

    # spazio-temporale con campo datetime
    st = QgsVectorLayer("Point?crs=EPSG:32633&field=v:double&field=t:datetime", "st", "memory")
    feats = []
    for day in (-10, -5, 0, 5, 10):
        for _ in range(25):
            x, y = rng.uniform(0, 100, 2)
            feat = QgsFeature(st.fields())
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
            feat.setAttributes([10 + 0.5 * day + 0.05 * x, QDateTime(2024, 1, 15 + day, 12, 0)])
            feats.append(feat)
    st.dataProvider().addFeatures(feats)
    st.updateExtents()
    project.addMapLayer(st)
    res = run_alg('geoarchaeo:spatiotemporal', {'INPUT': st, 'VALUE_FIELD': 'v', 'TIME_FIELD': 't',
                                                'TARGET_TIME': QDateTime(2024, 1, 15, 12, 0), 'TIME_RANGE': 0,
                                                'PIXEL_SIZE': 10.0, 'OUTPUT': str(tmp_path / 'st.tif')})
    raster = QgsRasterLayer(res['OUTPUT'], 'st')
    assert raster.isValid()
    west = raster.dataProvider().sample(QgsPointXY(5, 50), 1)[0]
    east = raster.dataProvider().sample(QgsPointXY(95, 50), 1)[0]
    assert east > west + 2


def test_processing_ml_and_sampling(app, project, processing_ready):
    layer = make_layer(n=80, nulls=0, seed=8)
    polygon = make_polygon_layer()
    project.addMapLayers([layer, polygon])
    res = run_alg('geoarchaeo:mlpattern', {'INPUTS': [layer], 'ML_METHOD': 0, 'N_CLUSTERS': 2,
                                           'LABEL_FIELD': '', 'OUTPUT': 'memory:'})
    out = res['OUTPUT'] if isinstance(res['OUTPUT'], QgsVectorLayer) else QgsProcessingContext().getMapLayer(res['OUTPUT'])
    assert res['N_GROUPS'] == 2
    res = run_alg('geoarchaeo:mlpattern', {'INPUTS': [layer], 'ML_METHOD': 3, 'N_CLUSTERS': 0,
                                           'LABEL_FIELD': 'cat', 'OUTPUT': 'memory:'})
    assert res['N_GROUPS'] == 2
    res = run_alg('geoarchaeo:optimalsampling', {'EXISTING': layer, 'BOUNDARY': polygon, 'N_NEW': 6, 'METHOD': 1,
                                                 'OUTPUT': 'memory:'})
    assert res['N_POINTS'] == 6
    res = run_alg('geoarchaeo:optimalsampling', {'EXISTING': layer, 'BOUNDARY': None, 'N_NEW': 6, 'METHOD': 2,
                                                 'OUTPUT': 'memory:'})
    assert res['N_POINTS'] == 6


def test_example_boundary_in_other_crs(app, project, no_modal_dialogs):
    """area_studio.geojson (EPSG:4326) deve funzionare con i punti UTM (EPSG:32633)."""
    set_language('it')
    dock = GeoArchaeoDockWidget(None)
    files = dock._example_files(dock.example_dir)
    loaded = dock.load_example_files([f for f in files if f.endswith(('villa_ceramica.gpkg', 'area_studio.geojson'))])
    assert len(loaded) == 2
    points_layer = [l for l in loaded if l.name() == 'villa_ceramica'][0]
    area_utm = [l for l in loaded if l.name() == 'area_studio'][0]
    # versione del poligono riproiettata in WGS84 (come spesso accade con dati esterni)
    from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform
    area_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "area_wgs84", "memory")
    transform = QgsCoordinateTransform(area_utm.crs(), QgsCoordinateReferenceSystem('EPSG:4326'), project)
    feats = []
    for f in area_utm.getFeatures():
        geom = QgsGeometry(f.geometry())
        geom.transform(transform)
        nf = QgsFeature()
        nf.setGeometry(geom)
        feats.append(nf)
    area_layer.dataProvider().addFeatures(feats)
    area_layer.updateExtents()
    project.addMapLayer(area_layer)
    assert area_layer.crs().authid() == 'EPSG:4326'
    dock.layer_combo.setLayer(points_layer)
    dock.field_combo.setField('ceramic_count')
    dock.boundary_combo.setLayer(area_layer)
    dock.n_points_spin.setValue(5)
    dock.sampling_combo.setCurrentIndex(0)
    dock._run_sampling_design()
    wait_thread(app, dock)
    pts = dock.current_results['sampling']['points']
    assert pts.shape == (5, 2)
    ext = area_utm.extent()
    assert np.all(pts[:, 0] >= ext.xMinimum()) and np.all(pts[:, 0] <= ext.xMaximum())
    assert np.all(pts[:, 1] >= ext.yMinimum()) and np.all(pts[:, 1] <= ext.yMaximum())
    dock.cleanup()
