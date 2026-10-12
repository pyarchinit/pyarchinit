"""Motore geostatistico di GeoArchaeo (indipendente da QGIS).

Copia adattata dei test di GeoArchaeo 1.3.1 (repository enzococca/GeoArchaeo,
`tests/test_engine.py`): il modulo `modules/geoarchaeo/` e' una copia fedele di quel
plugin, e questi test vanno tenuti allineati a ogni aggiornamento.
Cambiano solo gli import (il pacchetto qui e' `modules.geoarchaeo`) e la
fixture di QgsApplication, condivisa con gli altri test di pyArchInit.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
pytest.importorskip("scipy")
from modules.geoarchaeo.core.geostat_engine import (  # noqa: E402
    GeostatEngine, PolygonRegion, to_native, nice_number, MAX_GRID_SIDE, VARIOGRAM_MODELS, SAMPLING_METHODS)


class Extent:
    """Mock minimale di QgsRectangle."""
    def __init__(self, xmin, ymin, xmax, ymax):
        self._b = (xmin, ymin, xmax, ymax)

    def xMinimum(self): return self._b[0]
    def yMinimum(self): return self._b[1]
    def xMaximum(self): return self._b[2]
    def yMaximum(self): return self._b[3]
    def width(self): return self._b[2] - self._b[0]
    def height(self): return self._b[3] - self._b[1]


class Circle:
    """Boundary fittizio: cerchio (espone boundingBox() e contains_xy())."""
    def __init__(self, cx, cy, r):
        self.cx, self.cy, self.r = cx, cy, r

    def boundingBox(self):
        return Extent(self.cx - self.r, self.cy - self.r, self.cx + self.r, self.cy + self.r)

    def contains_xy(self, x, y):
        return (x - self.cx) ** 2 + (y - self.cy) ** 2 <= self.r ** 2


@pytest.fixture
def engine():
    return GeostatEngine()


def gaussian_field(n=150, seed=0, rng_len=30.0, anisotropy=1.0, angle_deg=0.0):
    """Campo casuale con correlazione spaziale nota (per test realistici)."""
    rng = np.random.default_rng(seed)
    pts = rng.uniform(0, 100, size=(n, 2))
    a = np.radians(angle_deg)
    rot = np.array([[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]])
    local = pts @ rot.T
    local[:, 1] *= anisotropy
    d = np.linalg.norm(local[:, None, :] - local[None, :, :], axis=-1)
    cov = np.exp(-3 * d / rng_len)
    vals = rng.multivariate_normal(np.zeros(n), cov + 1e-8 * np.eye(n))
    return pts, 10 + 3 * vals


def brute_force_variogram(points, values, max_distance, n_lags):
    edges = np.linspace(0, max_distance, n_lags + 1)
    sums = np.zeros(n_lags)
    counts = np.zeros(n_lags)
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            d = np.hypot(*(points[i] - points[j]))
            if d <= 0 or d > max_distance:
                continue
            k = min(int(np.searchsorted(edges, d, side='right') - 1), n_lags - 1)
            sums[k] += 0.5 * (values[i] - values[j]) ** 2
            counts[k] += 1
    valid = counts > 0
    return sums[valid] / counts[valid], counts[valid]


# ----------------------------------------------------------------------
# Variogramma
# ----------------------------------------------------------------------
def test_variogram_matches_brute_force(engine):
    pts, vals = gaussian_field(n=60, seed=1)
    res = engine.calculate_variogram(pts, vals, 50.0, 'spherical', n_lags=10)
    ref_semi, ref_counts = brute_force_variogram(pts, vals, 50.0, 10)
    assert np.allclose(res['semivariances'], ref_semi)
    assert res['n_pairs'] == [int(c) for c in ref_counts]
    assert all(isinstance(v, float) for v in res['distances'])
    assert all(isinstance(v, int) for v in res['n_pairs'])


@pytest.mark.parametrize('model', VARIOGRAM_MODELS)
def test_variogram_fit_recovers_parameters(engine, model):
    pts, vals = gaussian_field(n=300, seed=2, rng_len=30.0)
    res = engine.calculate_variogram(pts, vals, 60.0, model)
    p = res['model_params']
    assert 0 <= p['nugget'] <= p['sill']
    assert p['range'] > 0
    assert np.isfinite(p['rmse'])
    # il sill deve essere dell'ordine della varianza campionaria
    assert 0.3 * res['sample_variance'] < p['sill'] < 3 * res['sample_variance']
    if model in ('spherical', 'exponential'):
        assert 10 < p['range'] < 90


def test_variogram_fixed_params(engine):
    pts, vals = gaussian_field(n=100, seed=3)
    res = engine.calculate_variogram(pts, vals, 50.0, 'spherical',
                                     fixed_params={'nugget': 0.5, 'range': 25.0})
    assert res['model_params']['nugget'] == pytest.approx(0.5)
    assert res['model_params']['range'] == pytest.approx(25.0)
    assert res['model_params']['fixed'] == ['nugget', 'range']


def test_variogram_errors(engine):
    pts, vals = gaussian_field(n=20, seed=4)
    with pytest.raises(ValueError):
        engine.calculate_variogram(pts, vals, 0.0001)        # nessuna coppia
    with pytest.raises(ValueError):
        engine.calculate_variogram(pts, vals, -5)
    with pytest.raises(ValueError):
        engine.calculate_variogram(pts, vals, 50, 'cubic')
    with pytest.raises(ValueError):
        engine.calculate_variogram(pts[:2], vals[:2], 50)


def test_variogram_subsampling_large_dataset(engine):
    rng = np.random.default_rng(5)
    pts = rng.uniform(0, 100, size=(5000, 2))
    vals = rng.normal(size=5000)
    res = engine.calculate_variogram(pts, vals, 40.0, max_points=800)
    assert res['n_points'] == 5000
    assert res['n_points_used'] == 800


def test_variogram_handles_nan_values(engine):
    pts, vals = gaussian_field(n=50, seed=6)
    vals = vals.copy()
    vals[:5] = np.nan
    res = engine.calculate_variogram(pts, vals, 50.0)
    assert res['n_points'] == 45


def test_anisotropy_detected_on_anisotropic_field(engine):
    # correlazione 3 volte piu' lunga lungo x (0 gradi) che lungo y
    pts, vals = gaussian_field(n=700, seed=12, rng_len=12.0, anisotropy=3.0, angle_deg=0.0)
    res = engine.calculate_variogram(pts, vals, 30.0, 'exponential', check_anisotropy=True)
    an = res['anisotropy']
    assert an is not None and len(an['directions']) == 4
    assert an['ratio'] > 1.8
    assert an['major_direction'] == 0
    assert an['is_anisotropic'] is True
    # anisotropia geometrica: sill e nugget comuni, cambia solo il range
    assert all(d['sill'] == pytest.approx(res['model_params']['sill']) for d in an['directions'].values())


def test_anisotropy_isotropic_field(engine):
    pts, vals = gaussian_field(n=700, seed=8, rng_len=12.0)
    res = engine.calculate_variogram(pts, vals, 30.0, 'exponential', check_anisotropy=True)
    assert res['anisotropy']['ratio'] < 2.0
    assert res['anisotropy']['is_anisotropic'] is False


def test_evaluate_model_zero_is_zero_and_practical_range(engine):
    for model in VARIOGRAM_MODELS:
        g = engine._evaluate_model(np.array([0.0, 1e-6, 50.0, 500.0]), 1.0, 5.0, 50.0, model)
        assert g[0] == 0.0
        assert g[1] >= 1.0 - 1e-6          # salto del nugget
        assert g[2] >= 0.9 * 5.0            # ~95% del sill al range pratico
        assert g[3] <= 5.0 + 1e-9


# ----------------------------------------------------------------------
# Kriging
# ----------------------------------------------------------------------
def test_kriging_grid_shape_and_values(engine):
    pts, vals = gaussian_field(n=120, seed=9)
    ext = Extent(0, 0, 100, 50)
    res = engine.ordinary_kriging(pts, vals, ext, 5.0)
    assert res['predictions'].shape == (10, 20)
    assert res['variances'].shape == (10, 20)
    assert res['pixel_size'] == pytest.approx(5.0)
    assert res['grid_capped'] is False
    assert np.all(np.isfinite(res['predictions']))
    assert np.all(res['variances'] >= 0)
    assert res['x_grid'][0] == pytest.approx(2.5) and res['y_grid'][-1] == pytest.approx(47.5)
    # le predizioni restano nell'intervallo plausibile dei dati
    assert res['predictions'].min() > vals.min() - 3 * vals.std()
    assert res['predictions'].max() < vals.max() + 3 * vals.std()


def test_kriging_honours_data_points(engine):
    pts, vals = gaussian_field(n=80, seed=10)
    vg = engine.calculate_variogram(pts, vals, 50.0)
    preds, variances = engine._krige_targets(pts, vals, pts, vg['model_params'], vg['model_type'])
    assert np.allclose(preds, vals, atol=1e-6)
    assert np.allclose(variances, 0.0, atol=1e-6)


def test_kriging_grid_is_capped(engine):
    pts, vals = gaussian_field(n=50, seed=11)
    res = engine.ordinary_kriging(pts, vals, Extent(0, 0, 1000, 1000), 0.5, compute_cv=False)
    assert res['grid_capped'] is True
    assert max(res['predictions'].shape) == MAX_GRID_SIDE
    assert res['pixel_size'] == pytest.approx(2.0)


def test_kriging_with_duplicate_points_is_stable(engine):
    pts, vals = gaussian_field(n=60, seed=12)
    pts = np.vstack([pts, pts[:10]])
    vals = np.concatenate([vals, vals[:10] + 0.1])
    res = engine.ordinary_kriging(pts, vals, Extent(0, 0, 100, 100), 10.0)
    assert np.all(np.isfinite(res['predictions']))


def test_kriging_cross_validation(engine):
    pts, vals = gaussian_field(n=200, seed=13, rng_len=40.0)
    res = engine.ordinary_kriging(pts, vals, Extent(0, 0, 100, 100), 10.0)
    cv = res['cv_results']
    assert cv is not None
    assert cv['n_valid'] == cv['n_total'] == 200
    assert cv['rmse'] > 0 and cv['mae'] > 0
    assert cv['rmse'] < vals.std()            # meglio della media
    assert 0.2 < cv['r2'] <= 1.0
    assert 0.2 < cv['msdr'] < 5.0
    assert len(cv['predictions']) == 200
    json.dumps(to_native(cv))


def test_cross_validation_sampling(engine):
    pts, vals = gaussian_field(n=300, seed=14)
    cv = engine.cross_validate_kriging(pts, vals, engine.calculate_variogram(pts, vals, 50), max_cv_points=50)
    assert cv['n_total'] == 50


def test_kriging_progress_and_cancel(engine):
    pts, vals = gaussian_field(n=50, seed=15)
    calls = []
    res = engine.ordinary_kriging(pts, vals, Extent(0, 0, 100, 100), 5.0,
                                  progress=lambda f: calls.append(f) or True)
    assert calls and calls[-1] == pytest.approx(1.0)
    assert all(0 <= c <= 1 for c in calls)
    with pytest.raises(RuntimeError):
        engine.ordinary_kriging(pts, vals, Extent(0, 0, 100, 100), 5.0, progress=lambda f: False)


def test_kriging_uses_given_variogram(engine):
    pts, vals = gaussian_field(n=50, seed=16)
    vg = {'model_type': 'gaussian', 'model_params': {'nugget': 0.1, 'sill': 9.0, 'range': 30.0}}
    res = engine.ordinary_kriging(pts, vals, Extent(0, 0, 100, 100), 10.0, vg, compute_cv=False)
    assert res['variogram']['model_type'] == 'gaussian'
    assert res['variogram']['model_params']['range'] == 30.0


def test_kriging_sanitizes_bad_variogram(engine):
    pts, vals = gaussian_field(n=50, seed=17)
    vg = {'model_type': 'weird', 'model_params': {'nugget': -1, 'sill': 0, 'range': -5}}
    res = engine.ordinary_kriging(pts, vals, Extent(0, 0, 100, 100), 10.0, vg, compute_cv=False)
    assert np.all(np.isfinite(res['predictions']))
    assert res['variogram']['model_params']['sill'] > 0


def test_kriging_few_points(engine):
    pts = np.array([[0, 0], [10, 0], [0, 10], [10, 10]], dtype=float)
    vals = np.array([1.0, 2.0, 3.0, 4.0])
    res = engine.ordinary_kriging(pts, vals, Extent(0, 0, 10, 10), 1.0)
    assert res['predictions'].shape == (10, 10)
    assert np.all(np.isfinite(res['predictions']))


def test_co_kriging_uses_secondary_trend(engine):
    rng = np.random.default_rng(18)
    sec_pts = rng.uniform(0, 100, size=(2000, 2))
    sec_vals = sec_pts[:, 0] * 0.1            # covariata = gradiente lungo x
    pri_pts = rng.uniform(0, 100, size=(40, 2))
    pri_vals = 5 + 2 * (pri_pts[:, 0] * 0.1) + rng.normal(scale=0.1, size=40)
    res = engine.co_kriging(pri_pts, pri_vals, [(sec_pts, sec_vals)], Extent(0, 0, 100, 100), 10.0)
    assert res['regression']['r2'] > 0.95
    assert res['regression']['coefficients'][1] == pytest.approx(2.0, abs=0.2)
    assert res['predictions'].shape == (10, 10)
    # il trend lungo x deve riflettersi nella mappa
    assert res['predictions'][:, -1].mean() > res['predictions'][:, 0].mean() + 10


def test_co_kriging_without_secondary_falls_back(engine):
    pts, vals = gaussian_field(n=50, seed=19)
    res = engine.co_kriging(pts, vals, [], Extent(0, 0, 100, 100), 10.0)
    assert res['regression'] is None
    assert res['predictions'].shape == (10, 10)


def test_spatiotemporal_kriging(engine):
    rng = np.random.default_rng(20)
    data = []
    for t in (-10, -5, 0, 5, 10):
        for _ in range(30):
            x, y = rng.uniform(0, 100, 2)
            data.append({'x': x, 'y': y, 't': t, 'value': 10 + 0.5 * t + 0.05 * x + rng.normal(scale=0.2)})
    res = engine.spatiotemporal_kriging(data, target_time='2024-01-01', extent=Extent(0, 0, 100, 100), pixel_size=10)
    assert res['predictions'].shape == (10, 10)
    assert np.all(np.isfinite(res['predictions']))
    # al tempo target (t=0) il valore medio deve essere ~10 + 0.05*x
    assert abs(res['predictions'].mean() - 12.5) < 1.5
    assert res['target_time'] == '2024-01-01'


def test_batch_kriging_matches_direct_kriging(engine):
    pts, vals = gaussian_field(n=300, seed=21, rng_len=30)
    ext = Extent(0, 0, 100, 100)
    vg = engine.calculate_variogram(pts, vals, 40.0)
    direct = engine.ordinary_kriging(pts, vals, ext, 5.0, vg, compute_cv=False)
    batch = engine.batch_kriging(pts, vals, ext, 5.0, tile_size=40, overlap_percent=20, variogram_params=vg)
    assert batch['predictions'].shape == direct['predictions'].shape
    assert batch['n_tiles'] > 1
    assert np.all(np.isfinite(batch['predictions']))
    diff = np.abs(batch['predictions'] - direct['predictions'])
    assert np.nanmedian(diff) < 0.2 * vals.std()


def test_create_tiles_cover_extent(engine):
    tiles = engine.create_tiles(Extent(0, 0, 95, 50), 40, 10)
    assert tiles[0]['xmin'] == 0 and tiles[-1]['xmax'] == 95 and tiles[-1]['ymax'] == 50
    assert all(t['xmax'] - t['xmin'] <= 40 + 1e-9 for t in tiles)


def test_grid_helpers(engine):
    nx, ny, ps, capped = engine.grid_shape(Extent(0, 0, 100, 40), 2.0)
    assert (nx, ny, ps, capped) == (50, 20, 2.0, False)
    assert engine.suggest_pixel_size(Extent(0, 0, 123, 40)) == pytest.approx(1.2)
    assert engine.suggest_max_distance(np.array([[0, 0], [300, 400]])) == pytest.approx(170.0)
    assert nice_number(0.0123456) == pytest.approx(0.012)
    assert nice_number(98765) == 99000


# ----------------------------------------------------------------------
# Composizionale
# ----------------------------------------------------------------------
def test_compositional_transforms(engine):
    comp = np.array([[60, 30, 10], [20, 50, 30], [0, 70, 30]], dtype=float)
    pts = np.zeros((3, 2))
    clr = engine.compositional_analysis(pts, comp, 'clr')
    assert np.allclose(clr['transformed'].sum(axis=1), 0)
    ilr = engine.compositional_analysis(pts, comp, 'ilr')
    assert ilr['transformed'].shape == (3, 2)
    psi = engine._build_ilr_matrix(4)
    assert np.allclose(psi @ psi.T, np.eye(3))
    alr = engine.compositional_analysis(pts, comp, 'alr')
    assert alr['transformed'].shape == (3, 2)
    assert np.all(np.isfinite(alr['transformed']))
    with pytest.raises(ValueError):
        engine.compositional_analysis(pts, comp, 'foo')


# ----------------------------------------------------------------------
# Machine learning
# ----------------------------------------------------------------------
def two_blobs(n=60, seed=22):
    rng = np.random.default_rng(seed)
    a = rng.normal((10, 10), 1.0, size=(n, 2))
    b = rng.normal((50, 50), 1.0, size=(n, 2))
    pts = np.vstack([a, b])
    feats = np.vstack([rng.normal(1, 0.1, (n, 1)), rng.normal(5, 0.1, (n, 1))])
    return pts, feats


@pytest.mark.skipif(not GeostatEngine().ml_available, reason='scikit-learn missing')
def test_ml_methods(engine):
    pts, feats = two_blobs()
    layers = [{'name': 'l', 'points': pts.tolist(), 'features': feats.tolist()}]
    km = engine.ml_pattern_recognition(layers, 'kmeans', n_clusters=2)
    assert km['n_clusters'] == 2
    assert len(set(km['labels'][:60])) == 1 and len(set(km['labels'][60:])) == 1
    db = engine.ml_pattern_recognition(layers, 'dbscan')
    assert db['n_clusters'] >= 2
    iso = engine.ml_pattern_recognition(layers, 'isolation_forest', contamination=0.1)
    assert set(np.unique(iso['labels'])) <= {0, 1}
    assert 0 < iso['labels'].sum() < len(pts)


@pytest.mark.skipif(not GeostatEngine().ml_available, reason='scikit-learn missing')
def test_ml_random_forest_supervised(engine):
    pts, feats = two_blobs()
    layers = [{'name': 'l', 'points': pts.tolist(), 'features': feats.tolist()}]
    labels = ['a'] * 10 + [None] * 50 + ['b'] * 10 + [''] * 50
    rf = engine.ml_pattern_recognition(layers, 'random_forest', labels=labels)
    assert rf['class_names'] == {0: 'a', 1: 'b'}
    assert np.all(rf['labels'][:60] == 0) and np.all(rf['labels'][60:] == 1)
    with pytest.raises(ValueError):
        engine.ml_pattern_recognition(layers, 'random_forest')


@pytest.mark.skipif(not GeostatEngine().ml_available, reason='scikit-learn missing')
def test_ml_mixed_layers_and_missing_features(engine):
    pts, feats = two_blobs(n=20)
    layers = [{'name': 'a', 'points': pts[:20].tolist(), 'features': feats[:20].tolist()},
              {'name': 'b', 'points': pts[20:].tolist(), 'features': [[None]] * 20}]
    res = engine.ml_pattern_recognition(layers, 'kmeans')
    assert len(res['labels']) == 40 and np.all(np.isfinite(res['features']))


# ----------------------------------------------------------------------
# Campionamento
# ----------------------------------------------------------------------
@pytest.mark.parametrize('method', SAMPLING_METHODS)
def test_sampling_methods_without_boundary(engine, method):
    rng = np.random.default_rng(23)
    existing = rng.uniform(0, 100, size=(30, 2))
    new = engine.optimal_sampling_design(existing, None, 12, method, random_state=1)
    assert new.shape == (12, 2)
    assert np.all(new[:, 0] >= -21) and np.all(new[:, 0] <= 121)


@pytest.mark.parametrize('method', SAMPLING_METHODS)
def test_sampling_methods_with_boundary(engine, method):
    rng = np.random.default_rng(24)
    existing = rng.uniform(30, 70, size=(20, 2))
    circle = Circle(50, 50, 40)
    new = engine.optimal_sampling_design(existing, circle, 15, method, random_state=2)
    assert new.shape == (15, 2)
    assert all(circle.contains_xy(x, y) for x, y in new)


def test_maximin_prefers_empty_regions(engine):
    existing = np.array([[10.0, 10.0], [15.0, 12.0], [12.0, 8.0]])
    new = engine.optimal_sampling_design(existing, Extent(0, 0, 100, 100) and Circle(50, 50, 70), 3, 'maximin', random_state=3)
    assert np.all(np.linalg.norm(new - existing.mean(axis=0), axis=1) > 30)


def test_variance_design_spreads_points(engine):
    existing = np.array([[10.0, 10.0]])
    new = engine.optimal_sampling_design(existing, Circle(50, 50, 50), 6, 'variance', random_state=4)
    d = np.linalg.norm(new[:, None, :] - new[None, :, :], axis=-1)
    assert d[np.triu_indices(6, 1)].min() > 10


def test_sampling_errors(engine):
    with pytest.raises(ValueError):
        engine.optimal_sampling_design(np.zeros((3, 2)), None, 0, 'maximin')
    with pytest.raises(ValueError):
        engine.optimal_sampling_design(np.zeros((3, 2)), None, 3, 'random')
    with pytest.raises(ValueError):
        engine.optimal_sampling_design(np.empty((0, 2)), None, 3, 'maximin')


# ----------------------------------------------------------------------
# Grafici
# ----------------------------------------------------------------------
@pytest.mark.skipif(not GeostatEngine().plotly_available, reason='plotly missing')
def test_plotly_figures(engine):
    pts, vals = gaussian_field(n=80, seed=25)
    vg = engine.calculate_variogram(pts, vals, 50.0, check_anisotropy=True)
    kr = engine.ordinary_kriging(pts, vals, Extent(0, 0, 100, 100), 10.0, vg, compute_cv=False)
    assert engine.create_interactive_variogram(vg).to_html(include_plotlyjs=False)
    assert engine.create_interactive_kriging_map(kr['x_grid'], kr['y_grid'], kr['predictions'],
                                                 kr['variances'], pts).to_html(include_plotlyjs=False)
    assert engine.create_histogram(vals, 'v').to_html(include_plotlyjs=False)
    if engine.ml_available:
        p2, f2 = two_blobs()
        ml = engine.ml_pattern_recognition([{'name': 'l', 'points': p2.tolist(), 'features': f2.tolist()}], 'kmeans')
        assert engine.create_ml_visualization(ml['features'], ml['labels'], 'K-Means').to_html(include_plotlyjs=False)


@pytest.mark.skipif(not GeostatEngine().matplotlib_available, reason='matplotlib missing')
def test_png_renderers(engine):
    pts, vals = gaussian_field(n=80, seed=26)
    vg = engine.calculate_variogram(pts, vals, 50.0, check_anisotropy=True)
    kr = engine.ordinary_kriging(pts, vals, Extent(0, 0, 100, 100), 10.0, vg, compute_cv=False)
    for png in (engine.render_variogram_png(vg),
                engine.render_kriging_png(kr['x_grid'], kr['y_grid'], kr['predictions'], kr['variances'], pts),
                engine.render_histogram_png(vals, 'v')):
        assert png[:8] == b'\x89PNG\r\n\x1a\n'
    if engine.ml_available:
        p2, f2 = two_blobs()
        ml = engine.ml_pattern_recognition([{'name': 'l', 'points': p2.tolist(), 'features': f2.tolist()}], 'kmeans')
        assert engine.render_ml_png(ml['features'], ml['labels'], 'K-Means')[:4] == b'\x89PNG'


def test_variogram_result_is_json_serializable(engine):
    pts, vals = gaussian_field(n=80, seed=27)
    vg = engine.calculate_variogram(pts, vals, 50.0, check_anisotropy=True)
    text = json.dumps(to_native(vg))
    assert json.loads(text)['model_params']['range'] == pytest.approx(vg['model_params']['range'])


def test_polygon_region_contains():
    square_with_hole = PolygonRegion([([[0, 0], [10, 0], [10, 10], [0, 10]], [[[4, 4], [6, 4], [6, 6], [4, 6]]])])
    assert square_with_hole.bounds() == (0, 0, 10, 10)
    assert square_with_hole.contains_xy(1, 1)
    assert not square_with_hole.contains_xy(5, 5)          # nel buco
    assert not square_with_hole.contains_xy(11, 5)
    multi = PolygonRegion([([[0, 0], [1, 0], [1, 1], [0, 1]], []), ([[5, 5], [6, 5], [6, 6], [5, 6]], [])])
    mask = multi.contains_many([[0.5, 0.5], [5.5, 5.5], [3, 3]])
    assert mask.tolist() == [True, True, False]
    with pytest.raises(ValueError):
        PolygonRegion([([[0, 0], [1, 1]], [])])


@pytest.mark.parametrize('method', SAMPLING_METHODS)
def test_sampling_with_polygon_region(engine, method):
    region = PolygonRegion([([[0, 0], [100, 0], [100, 100], [0, 100]], [[[40, 40], [60, 40], [60, 60], [40, 60]]])])
    existing = np.array([[10.0, 10.0], [90.0, 90.0], [10.0, 90.0]])
    new = engine.optimal_sampling_design(existing, region, 20, method, random_state=5)
    assert new.shape == (20, 2)
    assert region.contains_many(new).all()
