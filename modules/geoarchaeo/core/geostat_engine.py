"""
Motore geostatistico principale di GeoArchaeo.

Tutte le routine numeriche sono vettorializzate (numpy/scipy) e indipendenti da
QGIS: l'unico oggetto QGIS accettato e' l'"extent", di cui vengono usati solo i
metodi xMinimum()/xMaximum()/yMinimum()/yMaximum() (in alternativa una tupla
(xmin, ymin, xmax, ymax)).
"""

import contextlib
import io
import warnings

import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree
from scipy.spatial.distance import pdist

# Compatibilita' numpy >= 1.24 per codice di terze parti che usa gli alias rimossi
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    for _alias, _type in (('float', float), ('int', int), ('bool', bool), ('str', str)):
        if not hasattr(np, _alias):
            setattr(np, _alias, _type)

# Import opzionali per ML - se falliscono, disabilitiamo le funzionalita' ML
ML_AVAILABLE = False
try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.decomposition import PCA
    from sklearn.neighbors import NearestNeighbors
    ML_AVAILABLE = True
except ImportError as e:  # pragma: no cover - dipende dall'ambiente
    print(f"Warning: Machine Learning features disabled. {e}")
    StandardScaler = RandomForestClassifier = IsolationForest = None
    KMeans = DBSCAN = PCA = NearestNeighbors = None

# Import opzionali per visualizzazione interattiva
PLOTLY_AVAILABLE = False
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:  # pragma: no cover
    print("Warning: Plotly visualization features disabled.")
    go = None
    make_subplots = None

# Import opzionale per grafici statici (fallback senza QtWebEngine)
MATPLOTLIB_AVAILABLE = False
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:  # pragma: no cover
    Figure = None
    FigureCanvasAgg = None


try:
    from threadpoolctl import threadpool_limits
except ImportError:  # pragma: no cover
    threadpool_limits = None


@contextlib.contextmanager
def limit_native_threads(limit=1):
    """
    Limita i thread di BLAS/OpenMP durante calcoli eseguiti fuori dal thread
    principale: il pool di thread di OpenBLAS usato da un thread secondario
    puo' far crashare QGIS (SIGBUS su macOS). I sistemi lineari del kriging
    sono piccoli, quindi il costo e' nullo.
    """
    if threadpool_limits is None:
        yield
        return
    try:
        with threadpool_limits(limits=limit):
            yield
    except Exception:
        yield


VARIOGRAM_MODELS = ('spherical', 'exponential', 'gaussian', 'matern')
SAMPLING_METHODS = ('maximin', 'variance', 'stratified', 'adaptive')
ML_METHODS = ('kmeans', 'dbscan', 'isolation_forest', 'random_forest')

# Lato massimo della griglia di kriging (celle). 500x500 = 250k celle:
# con 20 vicini per cella il calcolo resta nell'ordine dei secondi.
MAX_GRID_SIDE = 500
DEFAULT_MAX_NEIGHBORS = 20
# Rapporto range maggiore/minore oltre il quale si segnala anisotropia. Con
# poche centinaia di punti i variogrammi direzionali sono rumorosi (rapporti
# fino a ~1.7 anche su campi isotropi), quindi la soglia e' prudente.
ANISOTROPY_THRESHOLD = 2.0

# Etichette dei grafici (il motore non dipende dal modulo i18n della GUI)
_PLOT_LABELS = {
    'it': {
        'empirical': 'Empirico', 'model': 'Modello', 'distance': 'Distanza',
        'semivariance': 'Semivarianza', 'pairs': 'Coppie', 'variogram_title': 'Variogramma sperimentale e modello',
        'nugget': 'Nugget', 'sill': 'Sill', 'range': 'Range', 'predicted': 'Valori predetti',
        'uncertainty': 'Incertezza (dev. standard)', 'samples': 'Punti campione', 'value': 'Valore',
        'kriging_title': 'Risultati kriging', 'cluster': 'Gruppo', 'ml_title': 'Pattern recognition',
        'variance_pct': 'varianza', 'histogram_title': 'Distribuzione dei valori', 'count': 'Frequenza',
        'anisotropy': 'Anisotropia', 'direction': 'direzione',
    },
    'en': {
        'empirical': 'Empirical', 'model': 'Model', 'distance': 'Distance',
        'semivariance': 'Semivariance', 'pairs': 'Pairs', 'variogram_title': 'Experimental variogram and model',
        'nugget': 'Nugget', 'sill': 'Sill', 'range': 'Range', 'predicted': 'Predicted values',
        'uncertainty': 'Uncertainty (std. dev.)', 'samples': 'Sample points', 'value': 'Value',
        'kriging_title': 'Kriging results', 'cluster': 'Group', 'ml_title': 'Pattern recognition',
        'variance_pct': 'variance', 'histogram_title': 'Value distribution', 'count': 'Count',
        'anisotropy': 'Anisotropy', 'direction': 'direction',
    },
}


def _lang():
    """Lingua corrente della GUI (fallback 'en' fuori da QGIS)."""
    try:
        from ..i18n import get_language
        return get_language()
    except Exception:
        return 'en'


def _L(key):
    labels = _PLOT_LABELS.get(_lang(), _PLOT_LABELS['en'])
    return labels.get(key, key)


class PolygonRegion:
    """
    Area di studio come liste di anelli numpy (indipendente da QGIS e sicura nei
    thread). polygons: lista di (anello_esterno (n,2), [buchi (m,2), ...]).
    """

    def __init__(self, polygons):
        self.polygons = []
        for outer, holes in polygons:
            outer = np.asarray(outer, dtype=float).reshape(-1, 2)
            if len(outer) < 3:
                continue
            self.polygons.append((outer, [np.asarray(h, dtype=float).reshape(-1, 2) for h in holes
                                          if len(h) >= 3]))
        if not self.polygons:
            raise ValueError("PolygonRegion needs at least one ring with 3 vertices")
        allv = np.vstack([o for o, _ in self.polygons])
        self._bounds = (float(allv[:, 0].min()), float(allv[:, 1].min()),
                        float(allv[:, 0].max()), float(allv[:, 1].max()))

    def bounds(self):
        return self._bounds

    @staticmethod
    def _in_ring(x, y, ring):
        """Ray casting (regola pari/dispari) vettorializzato sui punti."""
        xs, ys = ring[:, 0], ring[:, 1]
        xe, ye = np.roll(xs, -1), np.roll(ys, -1)
        inside = np.zeros(len(x), dtype=bool)
        for i in range(len(xs)):
            if ys[i] == ye[i]:
                continue
            crosses = (ys[i] > y) != (ye[i] > y)
            x_int = (xe[i] - xs[i]) * (y - ys[i]) / (ye[i] - ys[i]) + xs[i]
            inside ^= crosses & (x < x_int)
        return inside

    def contains_many(self, points):
        points = np.asarray(points, dtype=float).reshape(-1, 2)
        x, y = points[:, 0], points[:, 1]
        result = np.zeros(len(points), dtype=bool)
        for outer, holes in self.polygons:
            inside = self._in_ring(x, y, outer)
            for hole in holes:
                inside &= ~self._in_ring(x, y, hole)
            result |= inside
        return result

    def contains_xy(self, x, y):
        return bool(self.contains_many(np.array([[x, y]]))[0])


def extent_bounds(extent):
    """Restituisce (xmin, ymin, xmax, ymax) da un QgsRectangle o da una tupla."""
    if hasattr(extent, 'xMinimum'):
        return (float(extent.xMinimum()), float(extent.yMinimum()),
                float(extent.xMaximum()), float(extent.yMaximum()))
    xmin, ymin, xmax, ymax = extent
    return float(xmin), float(ymin), float(xmax), float(ymax)


def nice_number(x, digits=2):
    """Arrotonda a `digits` cifre significative (per valori di default leggibili)."""
    x = float(x)
    if x == 0 or not np.isfinite(x):
        return x
    magnitude = 10 ** (np.floor(np.log10(abs(x))) - digits + 1)
    return float(np.round(x / magnitude) * magnitude)


def to_native(obj):
    """Converte ricorsivamente array/scalari numpy in tipi Python (per JSON)."""
    if isinstance(obj, dict):
        return {str(k): to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_native(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return to_native(obj.tolist())
    if isinstance(obj, np.generic):
        return obj.item()
    return obj


class GeostatEngine:
    """Motore geostatistico: variogrammi, kriging, ML, campionamento, grafici."""

    def __init__(self):
        self.ml_available = ML_AVAILABLE
        self.plotly_available = PLOTLY_AVAILABLE
        self.matplotlib_available = MATPLOTLIB_AVAILABLE

    # ------------------------------------------------------------------
    # Utilita'
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_points(points, values, min_points=3):
        points = np.asarray(points, dtype=float)
        values = np.asarray(values, dtype=float).ravel()
        if points.ndim != 2:
            raise ValueError("points must be a 2D array (n, dim)")
        if points.shape[0] != values.shape[0]:
            raise ValueError("points and values must have the same length")
        finite = np.all(np.isfinite(points), axis=1) & np.isfinite(values)
        points, values = points[finite], values[finite]
        if len(points) < min_points:
            raise ValueError(f"At least {min_points} valid points are required (got {len(points)})")
        return points, values

    @staticmethod
    def suggest_max_distance(points):
        """Distanza massima consigliata per il variogramma: 1/3 della diagonale."""
        points = np.asarray(points, dtype=float)
        if len(points) < 2:
            return 100.0
        span = points.max(axis=0) - points.min(axis=0)
        diag = float(np.hypot(*span[:2]))
        return nice_number(diag / 3.0) if diag > 0 else 100.0

    @staticmethod
    def suggest_pixel_size(extent, target_cells=100):
        """Risoluzione consigliata: circa `target_cells` celle sul lato maggiore."""
        xmin, ymin, xmax, ymax = extent_bounds(extent)
        side = max(xmax - xmin, ymax - ymin)
        if side <= 0:
            return 1.0
        return nice_number(side / float(target_cells))

    @staticmethod
    def grid_shape(extent, pixel_size, max_side=MAX_GRID_SIDE):
        """Dimensioni (nx, ny, pixel_size_effettivo, limitata) della griglia."""
        xmin, ymin, xmax, ymax = extent_bounds(extent)
        w = max(xmax - xmin, 1e-12)
        h = max(ymax - ymin, 1e-12)
        ps = float(pixel_size)
        if not ps > 0:
            raise ValueError("pixel_size must be positive")
        capped = False
        min_ps = max(w, h) / float(max_side)
        if ps < min_ps:
            ps = min_ps
            capped = True
        nx = max(1, int(np.ceil(w / ps - 1e-9)))
        ny = max(1, int(np.ceil(h / ps - 1e-9)))
        return nx, ny, ps, capped

    def _build_grid(self, extent, pixel_size, max_side=MAX_GRID_SIDE):
        xmin, ymin, _, _ = extent_bounds(extent)
        nx, ny, ps, capped = self.grid_shape(extent, pixel_size, max_side)
        x_grid = xmin + ps * (np.arange(nx) + 0.5)
        y_grid = ymin + ps * (np.arange(ny) + 0.5)
        return x_grid, y_grid, ps, capped

    # ------------------------------------------------------------------
    # Variogramma
    # ------------------------------------------------------------------
    def calculate_variogram(self, points, values, max_distance, model_type='spherical',
                            check_anisotropy=False, n_lags=15, fixed_params=None,
                            max_points=3000, random_state=42):
        """
        Variogramma sperimentale (omnidirezionale) + fit del modello teorico.

        - points: array (n, 2) (o (n, 3) per lo spazio-tempo)
        - fixed_params: dict con eventuali 'nugget'/'sill'/'range' da tenere fissi
        - max_points: oltre questa soglia si usa un sottocampione casuale per il
          calcolo delle coppie (il numero di coppie cresce con n^2)
        """
        points, values = self._validate_points(points, values, min_points=3)
        if model_type not in VARIOGRAM_MODELS:
            raise ValueError(f"Unknown variogram model '{model_type}'")
        max_distance = float(max_distance)
        if not max_distance > 0:
            raise ValueError("max_distance must be positive")
        n_lags = int(max(2, n_lags))

        n = len(points)
        if n > max_points:
            rng = np.random.default_rng(random_state)
            keep = np.sort(rng.choice(n, int(max_points), replace=False))
            pts, vals = points[keep], values[keep]
        else:
            pts, vals = points, values

        d = pdist(pts)
        gamma = 0.5 * pdist(vals[:, None], metric='sqeuclidean')
        mask = (d > 0) & (d <= max_distance)
        if not mask.any():
            raise ValueError(
                "No point pairs within the maximum distance: increase the maximum distance "
                f"(largest pair distance is {float(d.max()):.2f})")

        edges = np.linspace(0.0, max_distance, n_lags + 1)
        emp = self._bin_semivariance(d[mask], gamma[mask], edges)
        if len(emp['distances']) < 2:
            raise ValueError("Too few lag classes with data: reduce the number of lags or increase the maximum distance")

        model_params = self._fit_variogram_model(
            emp['distances'], emp['semivariances'], model_type, emp['n_pairs'], fixed_params)

        anisotropy = None
        if check_anisotropy and pts.shape[1] == 2:
            anisotropy = self._check_anisotropy(pts, d, gamma, mask, edges, model_type, model_params)

        return {
            'distances': [float(v) for v in emp['distances']],
            'semivariances': [float(v) for v in emp['semivariances']],
            'n_pairs': [int(v) for v in emp['n_pairs']],
            'model_type': model_type,
            'model_params': model_params,
            'anisotropy': anisotropy,
            'max_distance': max_distance,
            'n_lags': n_lags,
            'n_points': int(n),
            'n_points_used': int(len(pts)),
            'sample_variance': float(np.var(vals)),
        }

    @staticmethod
    def _bin_semivariance(d, gamma, edges):
        idx = np.clip(np.searchsorted(edges, d, side='right') - 1, 0, len(edges) - 2)
        n_bins = len(edges) - 1
        counts = np.bincount(idx, minlength=n_bins)
        sums = np.bincount(idx, weights=gamma, minlength=n_bins)
        dsum = np.bincount(idx, weights=d, minlength=n_bins)
        valid = counts > 0
        return {
            'distances': dsum[valid] / counts[valid],
            'semivariances': sums[valid] / counts[valid],
            'n_pairs': counts[valid],
        }

    def _check_anisotropy(self, pts, d, gamma, mask, edges, model_type, omni_params,
                          directions=(0, 45, 90, 135), tolerance=22.5):
        """
        Variogrammi direzionali (angoli in gradi da Est, antiorari).

        Modello di anisotropia geometrica: nugget e sill sono quelli del
        variogramma omnidirezionale, per ogni direzione si stima solo il range.
        """
        fixed = {'nugget': omni_params['nugget'], 'sill': omni_params['sill']}
        n = len(pts)
        iu = np.triu_indices(n, 1)
        dx = pts[iu[1], 0] - pts[iu[0], 0]
        dy = pts[iu[1], 1] - pts[iu[0], 1]
        angle = np.degrees(np.arctan2(dy, dx)) % 180.0
        del dx, dy

        results = {}
        for direction in directions:
            diff = np.abs(angle - direction)
            diff = np.minimum(diff, 180.0 - diff)
            sel = mask & (diff <= tolerance)
            if sel.sum() < 10:
                continue
            emp = self._bin_semivariance(d[sel], gamma[sel], edges)
            if len(emp['distances']) < 3:
                continue
            try:
                params = self._fit_variogram_model(
                    emp['distances'], emp['semivariances'], model_type, emp['n_pairs'], fixed)
            except (ValueError, ArithmeticError):
                params = None
            if params is None:
                continue
            results[int(direction)] = {
                'range': params['range'], 'sill': params['sill'], 'nugget': params['nugget'],
                'n_pairs': int(sel.sum()),
                'distances': [float(v) for v in emp['distances']],
                'semivariances': [float(v) for v in emp['semivariances']],
            }

        if len(results) < 2:
            return {'ratio': 1.0, 'is_anisotropic': False, 'directions': results,
                    'note': 'insufficient pairs for directional variograms'}

        ranges = {k: v['range'] for k, v in results.items()}
        major = max(ranges, key=ranges.get)
        minor = min(ranges, key=ranges.get)
        ratio = ranges[major] / ranges[minor] if ranges[minor] > 0 else 1.0
        return {
            'ratio': float(ratio),
            'major_direction': int(major),
            'minor_direction': int(minor),
            'major_range': float(ranges[major]),
            'minor_range': float(ranges[minor]),
            'is_anisotropic': bool(ratio > ANISOTROPY_THRESHOLD),
            'directions': results,
        }

    def _fit_variogram_model(self, distances, semivariances, model_type, n_pairs=None, fixed=None):
        """Fit ai minimi quadrati pesati (peso = numero di coppie), multi-start."""
        h = np.asarray(distances, dtype=float)
        g = np.asarray(semivariances, dtype=float)
        if len(h) == 0:
            raise ValueError("Empty empirical variogram")
        w = np.asarray(n_pairs, dtype=float) if n_pairs is not None else np.ones_like(h)
        w = w / w.sum()
        fixed = {k: float(v) for k, v in (fixed or {}).items() if v is not None}

        sill0 = max(float(g.max()), 1e-12)
        nugget0 = float(min(max(g[0], 0.0), sill0 * 0.5))
        h_max = float(h[-1])

        def unpack(x):
            nugget = fixed.get('nugget', x[0])
            sill = fixed['sill'] if 'sill' in fixed else nugget + x[1]
            rng = fixed.get('range', x[2])
            return nugget, sill, rng

        def objective(x):
            nugget, sill, rng = unpack(x)
            if nugget < 0 or sill < nugget or rng <= 0:
                return 1e30
            pred = self._evaluate_model(h, nugget, sill, rng, model_type)
            return float(np.sum(w * (g - pred) ** 2))

        bounds = [(0.0, sill0 * 2.0), (0.0, sill0 * 3.0), (h_max * 1e-3, h_max * 3.0)]
        range_starts = [h[len(h) // 3], h_max * 0.5, h_max, h[max(0, len(h) // 6)]]
        starts = []
        for r0 in range_starts:
            for ng0 in (0.0, nugget0):
                starts.append([ng0, max(sill0 - ng0, 1e-12), float(max(r0, bounds[2][0]))])

        best_x, best_f = None, np.inf
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            for x0 in starts:
                try:
                    res = minimize(objective, x0, method='L-BFGS-B', bounds=bounds)
                except (ValueError, FloatingPointError, ArithmeticError):
                    res = None      # punto di partenza non valido: prova il successivo
                if res is not None and np.isfinite(res.fun) and res.fun < best_f:
                    best_f, best_x = float(res.fun), np.array(res.x, dtype=float)
        if best_x is None:
            best_x = np.array(starts[0], dtype=float)
            best_f = objective(best_x)

        nugget, sill, rng = unpack(best_x)
        return {
            'nugget': float(nugget),
            'sill': float(sill),
            'range': float(rng),
            'rmse': float(np.sqrt(max(best_f, 0.0))),
            'fixed': sorted(fixed.keys()),
        }

    @staticmethod
    def _evaluate_model(h, nugget, sill, range_val, model_type):
        """
        Semivariogramma teorico gamma(h). Per h == 0 restituisce 0 (il nugget e'
        la discontinuita' per h -> 0+), cosi' il kriging onora i dati osservati.
        Il "range" e' sempre il range pratico (95% del sill).
        """
        h = np.asarray(h, dtype=float)
        psill = float(sill) - float(nugget)
        r = max(float(range_val), 1e-12)
        if model_type == 'spherical':
            hr = np.minimum(h / r, 1.0)
            gam = nugget + psill * (1.5 * hr - 0.5 * hr ** 3)
        elif model_type == 'exponential':
            gam = nugget + psill * (1.0 - np.exp(-3.0 * h / r))
        elif model_type == 'gaussian':
            gam = nugget + psill * (1.0 - np.exp(-3.0 * (h / r) ** 2))
        elif model_type == 'matern':
            # Matern con nu = 1.5 in forma chiusa: corr = (1 + t) exp(-t),
            # t scalato in modo che corr(range) ~= 0.05 (range pratico)
            t = 4.744 * h / r
            gam = nugget + psill * (1.0 - (1.0 + t) * np.exp(-t))
        else:
            gam = np.full_like(h, float(sill))
        return np.where(h > 0, gam, 0.0)

    # ------------------------------------------------------------------
    # Kriging
    # ------------------------------------------------------------------
    def _auto_variogram(self, points, values, max_distance, model_type='spherical', **kwargs):
        """Variogramma automatico: se non ci sono coppie entro max_distance
        (dati molto sparsi) riprova usando la distanza massima tra i punti."""
        try:
            return self.calculate_variogram(points, values, max_distance, model_type, **kwargs)
        except ValueError:
            span = np.asarray(points, dtype=float).max(axis=0) - np.asarray(points, dtype=float).min(axis=0)
            widest = float(np.linalg.norm(span)) * 1.01
            if widest <= max_distance:
                raise
            return self.calculate_variogram(points, values, widest, model_type, **kwargs)

    @staticmethod
    def _sanitize_model_params(variogram_params, values, fallback_range):
        mp = dict(variogram_params.get('model_params', {}) or {})
        model_type = variogram_params.get('model_type', 'spherical')
        if model_type not in VARIOGRAM_MODELS:
            model_type = 'spherical'
        var = float(np.var(values))
        sill = float(mp.get('sill', var))
        if not np.isfinite(sill) or sill <= 0:
            sill = var if var > 0 else 1.0
        nugget = float(mp.get('nugget', 0.0))
        if not np.isfinite(nugget) or nugget < 0:
            nugget = 0.0
        nugget = min(nugget, sill)
        rng = float(mp.get('range', fallback_range))
        if not np.isfinite(rng) or rng <= 0:
            rng = float(fallback_range)
        return {'nugget': nugget, 'sill': sill, 'range': rng}, model_type

    def _krige_targets(self, points, values, targets, model_params, model_type,
                       max_neighbors=DEFAULT_MAX_NEIGHBORS, self_index=None,
                       chunk_size=2000, progress=None):
        """
        Ordinary kriging su target arbitrari (qualsiasi dimensione), risolto a
        blocchi con sistemi lineari vettorializzati sui k vicini piu' prossimi.

        self_index: per la cross-validation, indice del punto dati che coincide
        con ciascun target (viene escluso dai vicini).
        progress: callable(frazione) -> bool; se restituisce False il calcolo
        viene interrotto con RuntimeError('cancelled').
        """
        points = np.asarray(points, dtype=float)
        values = np.asarray(values, dtype=float)
        targets = np.asarray(targets, dtype=float)
        n = len(points)
        exclude = self_index is not None
        k = int(min(max_neighbors, n - (1 if exclude else 0)))
        if k < 1:
            raise ValueError("Not enough points for kriging")
        nugget = float(model_params['nugget'])
        sill = max(float(model_params['sill']), 1e-12)
        rng = float(model_params['range'])

        tree = cKDTree(points)
        m = len(targets)
        preds = np.full(m, np.nan)
        variances = np.full(m, np.nan)
        kq = k + 1 if exclude else k
        diag = np.arange(k)

        for start in range(0, m, chunk_size):
            tg = targets[start:start + chunk_size]
            c = len(tg)
            dist, idx = tree.query(tg, k=kq)
            if kq == 1:
                dist, idx = dist[:, None], idx[:, None]
            if exclude:
                own = np.asarray(self_index[start:start + c]).reshape(-1, 1)
                keep = idx != own
                # se il punto stesso non e' tra i vicini (duplicati), scarta l'ultimo
                no_self = keep.all(axis=1)
                keep[no_self, -1] = False
                idx = idx[keep].reshape(c, k)
                dist = dist[keep].reshape(c, k)

            nb = points[idx]                                    # (c, k, dim)
            D = np.sqrt(((nb[:, :, None, :] - nb[:, None, :, :]) ** 2).sum(-1))
            C = sill - self._evaluate_model(D, nugget, sill, rng, model_type)
            C[:, diag, diag] = sill * (1.0 + 1e-8)              # jitter numerico
            A = np.zeros((c, k + 1, k + 1))
            A[:, :k, :k] = C
            A[:, k, :k] = 1.0
            A[:, :k, k] = 1.0
            b = np.zeros((c, k + 1))
            b[:, :k] = sill - self._evaluate_model(dist, nugget, sill, rng, model_type)
            b[:, k] = 1.0
            try:
                sol = np.linalg.solve(A, b[..., None])[..., 0]
            except np.linalg.LinAlgError:
                sol = np.empty_like(b)
                for i in range(c):
                    sol[i] = np.linalg.lstsq(A[i], b[i], rcond=None)[0]
            w = sol[:, :k]
            mu = sol[:, k]
            preds[start:start + c] = (w * values[idx]).sum(axis=1)
            var = sill - (w * b[:, :k]).sum(axis=1) - mu
            variances[start:start + c] = np.maximum(var, 0.0)

            if progress is not None and not progress(min(start + c, m) / float(m)):
                raise RuntimeError('cancelled')

        return preds, variances

    def ordinary_kriging(self, points, values, extent, pixel_size, variogram_params=None,
                         max_neighbors=DEFAULT_MAX_NEIGHBORS, compute_cv=True,
                         max_cv_points=200, progress=None, max_grid_side=MAX_GRID_SIDE):
        """
        Ordinary Kriging su griglia regolare.

        Restituisce predizioni, varianze, coordinate dei centri cella, la
        risoluzione effettiva (puo' essere maggiore di quella richiesta se la
        griglia supera max_grid_side), il variogramma usato e la cross-validation.
        """
        points, values = self._validate_points(points, values, min_points=3)
        xmin, ymin, xmax, ymax = extent_bounds(extent)
        diag = float(np.hypot(xmax - xmin, ymax - ymin))
        if diag <= 0:
            diag = float(np.hypot(*(points.max(axis=0) - points.min(axis=0))[:2])) or 1.0

        if not variogram_params or not variogram_params.get('model_params'):
            variogram_params = self._auto_variogram(points, values, diag / 3.0)
        mp, model_type = self._sanitize_model_params(variogram_params, values, diag / 3.0)

        x_grid, y_grid, ps, capped = self._build_grid(extent, pixel_size, max_grid_side)
        xx, yy = np.meshgrid(x_grid, y_grid)
        targets = np.column_stack([xx.ravel(), yy.ravel()])

        cv_share = 0.15 if compute_cv else 0.0
        grid_progress = None
        if progress is not None:
            grid_progress = lambda f: progress(f * (1.0 - cv_share))

        preds, variances = self._krige_targets(
            points, values, targets, mp, model_type, max_neighbors, progress=grid_progress)

        cv_results = None
        if compute_cv:
            cv_results = self.cross_validate_kriging(
                points, values, {'model_params': mp, 'model_type': model_type},
                max_cv_points=max_cv_points, max_neighbors=max_neighbors)
            if progress is not None and not progress(1.0):
                raise RuntimeError('cancelled')

        ny, nx = len(y_grid), len(x_grid)
        return {
            'predictions': preds.reshape(ny, nx),
            'variances': variances.reshape(ny, nx),
            'x_grid': x_grid,
            'y_grid': y_grid,
            'pixel_size': float(ps),
            'grid_capped': bool(capped),
            'cv_results': cv_results,
            'variogram': {'model_params': mp, 'model_type': model_type},
            'n_points': int(len(points)),
            'max_neighbors': int(min(max_neighbors, len(points))),
        }

    def cross_validate_kriging(self, points, values, variogram_params, max_cv_points=200,
                               max_neighbors=DEFAULT_MAX_NEIGHBORS, random_state=42):
        """Leave-one-out su (al massimo) max_cv_points punti scelti a caso."""
        points, values = self._validate_points(points, values, min_points=4)
        n = len(points)
        if n > max_cv_points:
            rng = np.random.default_rng(random_state)
            idx = np.sort(rng.choice(n, int(max_cv_points), replace=False))
        else:
            idx = np.arange(n)
        span = points.max(axis=0) - points.min(axis=0)
        mp, model_type = self._sanitize_model_params(
            variogram_params, values, max(float(np.linalg.norm(span)) / 3.0, 1e-9))

        preds, variances = self._krige_targets(
            points, values, points[idx], mp, model_type, max_neighbors, self_index=idx)
        observed = values[idx]
        errors = preds - observed
        valid = np.isfinite(errors)
        n_valid = int(valid.sum())
        if n_valid < 2:
            return None
        e = errors[valid]
        o = observed[valid]
        ss_tot = float(np.sum((o - o.mean()) ** 2))
        r2 = float(1.0 - np.sum(e ** 2) / ss_tot) if ss_tot > 0 else 0.0
        v = variances[valid]
        with np.errstate(divide='ignore', invalid='ignore'):
            std_err = np.where(v > 0, e ** 2 / v, np.nan)
        msdr = float(np.nanmean(std_err)) if np.isfinite(std_err).any() else None
        return {
            'mae': float(np.mean(np.abs(e))),
            'rmse': float(np.sqrt(np.mean(e ** 2))),
            'me': float(np.mean(e)),
            'r2': r2,
            'msdr': msdr,
            'n_valid': n_valid,
            'n_total': int(len(idx)),
            'predictions': [float(p) for p in preds],
            'observed': [float(v) for v in observed],
            'errors': [float(x) for x in errors],
            'indices': [int(i) for i in idx],
        }

    def co_kriging(self, primary_points, primary_values, secondary_data, extent, pixel_size,
                   variogram_params=None, **kwargs):
        """
        Co-kriging semplificato (regression kriging con covariate collocate):
        1. per ogni punto primario si prende il valore secondario piu' vicino;
        2. regressione lineare primario ~ secondari;
        3. ordinary kriging dei residui;
        4. predizione = trend (dai secondari sulla griglia) + residuo interpolato.
        secondary_data: lista di tuple (points, values).
        """
        pp, pv = self._validate_points(primary_points, primary_values, min_points=3)
        sec = []
        for sp, sv in secondary_data or []:
            sp = np.asarray(sp, dtype=float)
            sv = np.asarray(sv, dtype=float).ravel()
            ok = np.all(np.isfinite(sp), axis=1) & np.isfinite(sv)
            if ok.sum() >= 1:
                sec.append((sp[ok], sv[ok]))
        if not sec:
            result = self.ordinary_kriging(pp, pv, extent, pixel_size, variogram_params, **kwargs)
            result['regression'] = None
            return result

        trees = [cKDTree(sp) for sp, _ in sec]

        def covariates(targets):
            cols = [np.ones(len(targets))]
            for tree, (_, sv) in zip(trees, sec):
                cols.append(sv[tree.query(targets)[1]])
            return np.column_stack(cols)

        X = covariates(pp)
        beta = np.linalg.lstsq(X, pv, rcond=None)[0]
        trend = X @ beta
        resid = pv - trend
        ss_res = float(np.sum(resid ** 2))
        ss_tot = float(np.sum((pv - pv.mean()) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

        result = self.ordinary_kriging(pp, resid, extent, pixel_size, None, **kwargs)
        xx, yy = np.meshgrid(result['x_grid'], result['y_grid'])
        grid_trend = (covariates(np.column_stack([xx.ravel(), yy.ravel()])) @ beta)
        grid_trend = grid_trend.reshape(result['predictions'].shape)
        result['trend'] = grid_trend
        result['predictions'] = result['predictions'] + grid_trend
        result['regression'] = {
            'coefficients': [float(b) for b in beta],
            'r2': float(r2),
            'n_secondary': [int(len(sv)) for _, sv in sec],
        }
        return result

    def spatiotemporal_kriging(self, space_time_data, target_time=None, extent=None,
                               pixel_size=None, time_scale=None, max_neighbors=DEFAULT_MAX_NEIGHBORS,
                               grid_side=100, progress=None):
        """
        Kriging spazio-temporale con metrica "metrica" (tempo convertito in
        distanza equivalente): 1 unita' di tempo = time_scale unita' spaziali.
        space_time_data: lista di dict {'x','y','t','value'} con t relativo al
        tempo target (t = 0 e' il tempo di predizione).
        """
        if len(space_time_data) < 3:
            raise ValueError("At least 3 space-time observations are required")
        coords = np.array([[d['x'], d['y'], d['t']] for d in space_time_data], dtype=float)
        values = np.array([d['value'] for d in space_time_data], dtype=float)
        coords, values = self._validate_points(coords, values, min_points=3)

        if extent is None:
            extent = (coords[:, 0].min(), coords[:, 1].min(), coords[:, 0].max(), coords[:, 1].max())
        xmin, ymin, xmax, ymax = extent_bounds(extent)
        diag = float(np.hypot(xmax - xmin, ymax - ymin)) or 1.0
        t_span = float(np.max(np.abs(coords[:, 2]))) or 1.0
        if time_scale is None:
            time_scale = 0.5 * diag / t_span
        xyz = coords.copy()
        xyz[:, 2] *= float(time_scale)

        diag3 = float(np.linalg.norm(xyz.max(axis=0) - xyz.min(axis=0))) or diag
        variogram = self.calculate_variogram(xyz, values, diag3 / 3.0, 'exponential')
        mp, model_type = self._sanitize_model_params(variogram, values, diag3 / 3.0)

        if pixel_size is None:
            pixel_size = max(xmax - xmin, ymax - ymin) / float(grid_side)
        x_grid, y_grid, ps, capped = self._build_grid(extent, pixel_size)
        xx, yy = np.meshgrid(x_grid, y_grid)
        targets = np.column_stack([xx.ravel(), yy.ravel(), np.zeros(xx.size)])
        preds, variances = self._krige_targets(
            xyz, values, targets, mp, model_type, max_neighbors, progress=progress)
        ny, nx = len(y_grid), len(x_grid)
        return {
            'predictions': preds.reshape(ny, nx),
            'variances': variances.reshape(ny, nx),
            'x_grid': x_grid,
            'y_grid': y_grid,
            'pixel_size': float(ps),
            'grid_capped': bool(capped),
            'target_time': target_time,
            'time_scale': float(time_scale),
            'variogram': variogram,
            'n_points': int(len(values)),
            'cv_results': None,
        }

    # ------------------------------------------------------------------
    # Batch kriging (tiling)
    # ------------------------------------------------------------------
    def create_tiles(self, extent, tile_size, overlap_percent):
        """Crea tiles con overlap per il batch processing."""
        xmin, ymin, xmax, ymax = extent_bounds(extent)
        tile_size = float(tile_size)
        if not tile_size > 0:
            raise ValueError("tile_size must be positive")
        overlap = tile_size * min(max(float(overlap_percent), 0.0), 90.0) / 100.0
        step = tile_size - overlap
        tiles = []
        y = ymin
        while y < ymax:
            x = xmin
            while x < xmax:
                tiles.append({'xmin': x, 'ymin': y,
                              'xmax': min(x + tile_size, xmax), 'ymax': min(y + tile_size, ymax)})
                x += step
            y += step
        return tiles

    def extract_points_in_tile_with_field(self, layer, tile, field_name, max_points):
        """Estrae punti QGIS in un tile (usato dal batch kriging via Processing)."""
        points, values = [], []
        xmin, ymin, xmax, ymax = tile['xmin'], tile['ymin'], tile['xmax'], tile['ymax']
        for feature in layer.getFeatures():
            if len(points) >= max_points:
                break
            geom = feature.geometry()
            if geom is None or geom.isEmpty():
                continue
            point = geom.centroid().asPoint() if geom.isMultipart() else geom.asPoint()
            if xmin <= point.x() <= xmax and ymin <= point.y() <= ymax:
                try:
                    value = float(feature[field_name])
                except (TypeError, ValueError):
                    continue
                points.append([point.x(), point.y()])
                values.append(value)
        return {'points': np.array(points), 'values': np.array(values)}

    def batch_kriging(self, points, values, extent, pixel_size, tile_size, overlap_percent=10.0,
                      max_points_per_tile=1000, variogram_params=None,
                      max_neighbors=DEFAULT_MAX_NEIGHBORS, progress=None, random_state=42,
                      max_grid_side=3000):
        """
        Ordinary kriging a tile per dataset grandi. Il variogramma e' stimato una
        volta (su un sottocampione) e ogni tile usa solo i punti nel tile piu' un
        margine; le celle nelle zone di overlap sono mediate.
        """
        points, values = self._validate_points(points, values, min_points=3)
        xmin, ymin, xmax, ymax = extent_bounds(extent)
        rng = np.random.default_rng(random_state)
        if not variogram_params or not variogram_params.get('model_params'):
            diag = float(np.hypot(xmax - xmin, ymax - ymin)) or 1.0
            variogram_params = self._auto_variogram(
                points, values, min(float(tile_size), diag / 3.0), random_state=random_state)
        mp, model_type = self._sanitize_model_params(variogram_params, values, float(tile_size) / 3.0)

        x_grid, y_grid, ps, capped = self._build_grid(extent, pixel_size, max_grid_side)
        ny, nx = len(y_grid), len(x_grid)
        pred_sum = np.zeros((ny, nx))
        var_sum = np.zeros((ny, nx))
        count = np.zeros((ny, nx))

        tiles = self.create_tiles(extent, tile_size, overlap_percent)
        margin = max(float(tile_size) * float(overlap_percent) / 100.0, 2.0 * ps, mp['range'] * 0.5)
        for i, tile in enumerate(tiles):
            ix = np.where((x_grid >= tile['xmin']) & (x_grid <= tile['xmax']))[0]
            iy = np.where((y_grid >= tile['ymin']) & (y_grid <= tile['ymax']))[0]
            if len(ix) == 0 or len(iy) == 0:
                continue
            sel = np.where(
                (points[:, 0] >= tile['xmin'] - margin) & (points[:, 0] <= tile['xmax'] + margin) &
                (points[:, 1] >= tile['ymin'] - margin) & (points[:, 1] <= tile['ymax'] + margin))[0]
            if len(sel) < 3:
                continue
            if len(sel) > max_points_per_tile:
                sel = rng.choice(sel, int(max_points_per_tile), replace=False)
            xx, yy = np.meshgrid(x_grid[ix], y_grid[iy])
            p, v = self._krige_targets(points[sel], values[sel],
                                       np.column_stack([xx.ravel(), yy.ravel()]),
                                       mp, model_type, max_neighbors)
            block = np.ix_(iy, ix)
            pred_sum[block] += p.reshape(len(iy), len(ix))
            var_sum[block] += v.reshape(len(iy), len(ix))
            count[block] += 1
            if progress is not None and not progress((i + 1) / float(len(tiles))):
                raise RuntimeError('cancelled')

        with np.errstate(divide='ignore', invalid='ignore'):
            predictions = np.where(count > 0, pred_sum / count, np.nan)
            variances = np.where(count > 0, var_sum / count, np.nan)
        return {
            'predictions': predictions,
            'variances': variances,
            'x_grid': x_grid,
            'y_grid': y_grid,
            'pixel_size': float(ps),
            'grid_capped': bool(capped),
            'cv_results': None,
            'variogram': {'model_params': mp, 'model_type': model_type},
            'n_points': int(len(points)),
            'n_tiles': int(len(tiles)),
        }

    # ------------------------------------------------------------------
    # Analisi composizionale
    # ------------------------------------------------------------------
    def compositional_analysis(self, points, compositions, transform_type='clr'):
        """Trasformazioni log-ratio (CLR / ILR / ALR) per dati composizionali."""
        compositions = np.asarray(compositions, dtype=float)
        if compositions.ndim != 2 or compositions.shape[1] < 2:
            raise ValueError("compositions must be a 2D array with at least 2 components")
        compositions = np.where(compositions > 0, compositions, 1e-10)
        compositions = compositions / compositions.sum(axis=1, keepdims=True)
        log_comp = np.log(compositions)

        if transform_type == 'clr':
            transformed = log_comp - log_comp.mean(axis=1, keepdims=True)
        elif transform_type == 'ilr':
            psi = self._build_ilr_matrix(compositions.shape[1])
            transformed = log_comp @ psi.T
        elif transform_type == 'alr':
            transformed = log_comp[:, :-1] - log_comp[:, -1:]
        else:
            raise ValueError(f"Unknown transform '{transform_type}'")

        return {
            'original': compositions,
            'transformed': transformed,
            'transform_type': transform_type,
            'points': np.asarray(points, dtype=float),
        }

    @staticmethod
    def _build_ilr_matrix(n):
        """Base ortonormale (Helmert) per la trasformazione ILR."""
        psi = np.zeros((n - 1, n))
        for i in range(n - 1):
            psi[i, :i + 1] = 1.0 / (i + 1)
            psi[i, i + 1] = -1.0
            psi[i] *= np.sqrt((i + 1) / (i + 2))
        return psi

    # ------------------------------------------------------------------
    # Machine learning
    # ------------------------------------------------------------------
    def ml_pattern_recognition(self, layers_data, method='kmeans', n_clusters=None,
                               labels=None, contamination=0.1, random_state=42):
        """
        Pattern recognition su punti + attributi numerici.

        layers_data: lista di dict {'name', 'points': [[x, y], ...], 'features': [[...], ...]}
        method: 'kmeans' | 'dbscan' | 'isolation_forest' | 'random_forest'
        n_clusters: numero di gruppi per K-Means (None = automatico)
        labels: etichette di training (per 'random_forest'), allineate ai punti;
                None/NaN/'' = punto da classificare
        """
        if not self.ml_available:
            raise NotImplementedError("Machine Learning features not available. Please install scikit-learn.")
        if method not in ML_METHODS:
            raise ValueError(f"Unknown ML method '{method}'")

        max_features = 0
        for layer_data in layers_data:
            for row in layer_data.get('features') or []:
                max_features = max(max_features, len(row))

        all_points, all_features = [], []
        for layer_data in layers_data:
            pts = layer_data['points']
            feats = layer_data.get('features') or []
            for i, point in enumerate(pts):
                row = list(feats[i]) if i < len(feats) else []
                row = [float(v) if v is not None and np.isfinite(float(v)) else np.nan for v in row]
                row += [np.nan] * (max_features - len(row))
                all_points.append([float(point[0]), float(point[1])])
                all_features.append(row[:max_features])

        all_points = np.asarray(all_points, dtype=float)
        n_samples = len(all_points)
        if n_samples < 3:
            raise ValueError("At least 3 points are required")
        if max_features > 0:
            feats = np.asarray(all_features, dtype=float)
            col_mean = np.nanmean(np.where(np.isfinite(feats), feats, np.nan), axis=0)
            col_mean = np.where(np.isfinite(col_mean), col_mean, 0.0)
            feats = np.where(np.isfinite(feats), feats, col_mean)
            combined = np.hstack([all_points, feats])
        else:
            combined = all_points
        X = StandardScaler().fit_transform(combined)
        X = np.where(np.isfinite(X), X, 0.0)

        class_names = None
        params = {}
        if method == 'kmeans':
            k = int(n_clusters) if n_clusters else max(2, min(5, n_samples // 10))
            k = int(min(max(k, 2), n_samples))
            model = KMeans(n_clusters=k, random_state=random_state, n_init=10)
            out = model.fit_predict(X)
            params = {'n_clusters': k}
        elif method == 'dbscan':
            min_samples = max(3, min(5, n_samples // 20))
            nn = NearestNeighbors(n_neighbors=min(min_samples, n_samples)).fit(X)
            k_dist = np.sort(nn.kneighbors(X)[0][:, -1])
            eps = max(float(np.percentile(k_dist, 90)), 0.3)
            model = DBSCAN(eps=eps, min_samples=min_samples)
            out = model.fit_predict(X)
            params = {'eps': eps, 'min_samples': min_samples}
        elif method == 'isolation_forest':
            model = IsolationForest(contamination=contamination, random_state=random_state)
            out = (model.fit_predict(X) == -1).astype(int)   # 1 = anomalia, 0 = normale
            params = {'contamination': contamination}
        else:  # random_forest (supervisionato)
            if labels is None:
                raise ValueError("Random Forest requires training labels (a label field)")
            raw = list(labels)
            if len(raw) != n_samples:
                raise ValueError("labels must be aligned with the input points")
            train_mask = np.array([
                not (lab is None or (isinstance(lab, float) and np.isnan(lab)) or str(lab).strip() == '')
                for lab in raw])
            y = np.array([str(lab) for lab in raw], dtype=object)
            classes = sorted(set(y[train_mask]))
            if train_mask.sum() < 2 or len(classes) < 2:
                raise ValueError("Random Forest needs at least 2 labelled classes in the training data")
            model = RandomForestClassifier(n_estimators=200, random_state=random_state)
            model.fit(X[train_mask], y[train_mask])
            pred = model.predict(X)
            class_names = {i: name for i, name in enumerate(classes)}
            code = {name: i for i, name in class_names.items()}
            out = np.array([code[p] for p in pred], dtype=int)
            params = {'n_training': int(train_mask.sum()), 'classes': classes,
                      'feature_importances': [float(v) for v in model.feature_importances_]}

        out = np.asarray(out, dtype=int)
        return {
            'features': X,
            'labels': out,
            'coordinates': all_points,
            'model': model,
            'method': method,
            'n_clusters': int(len(np.unique(out))),
            'class_names': class_names,
            'params': params,
        }

    # ------------------------------------------------------------------
    # Campionamento ottimale
    # ------------------------------------------------------------------
    @staticmethod
    def _point_in_boundary(boundary_geom, x, y):
        if boundary_geom is None:
            return True
        if hasattr(boundary_geom, 'contains_xy'):      # oggetti semplici / test
            return bool(boundary_geom.contains_xy(x, y))
        from qgis.core import QgsGeometry, QgsPointXY
        return bool(boundary_geom.contains(QgsGeometry.fromPointXY(QgsPointXY(x, y))))

    def _random_points_in_boundary(self, boundary_geom, bbox, n, rng, max_batches=200):
        """Punti casuali uniformi dentro il boundary (a blocchi vettorializzati)."""
        xmin, ymin, xmax, ymax = bbox
        found = []
        count = 0
        for _ in range(max_batches):
            batch = np.column_stack([rng.uniform(xmin, xmax, n), rng.uniform(ymin, ymax, n)])
            if boundary_geom is None:
                mask = np.ones(n, dtype=bool)
            elif hasattr(boundary_geom, 'contains_many'):
                mask = boundary_geom.contains_many(batch)
            else:
                mask = np.array([self._point_in_boundary(boundary_geom, x, y) for x, y in batch])
            kept = batch[mask]
            if len(kept):
                found.append(kept)
                count += len(kept)
            if count >= n:
                break
        if not found:
            return np.empty((0, 2))
        return np.vstack(found)[:n]

    @staticmethod
    def _boundary_bbox(existing_points, boundary_geom):
        if boundary_geom is None:
            if len(existing_points) == 0:
                raise ValueError("Without a study area at least one existing point is required")
            xmin, ymin = existing_points.min(axis=0)
            xmax, ymax = existing_points.max(axis=0)
            bx = max((xmax - xmin) * 0.2, 1.0)
            by = max((ymax - ymin) * 0.2, 1.0)
            return xmin - bx, ymin - by, xmax + bx, ymax + by
        if hasattr(boundary_geom, 'boundingBox'):
            bbox = boundary_geom.boundingBox()
            return bbox.xMinimum(), bbox.yMinimum(), bbox.xMaximum(), bbox.yMaximum()
        if hasattr(boundary_geom, 'bounds'):
            return tuple(boundary_geom.bounds())
        raise AttributeError("boundary_geom must provide boundingBox() or bounds()")

    def optimal_sampling_design(self, existing_points, boundary_geom, n_new, method='maximin',
                                variogram_params=None, random_state=None, n_candidates=None):
        """
        Propone n_new nuove posizioni di campionamento.

        boundary_geom: None, un PolygonRegion (consigliato: thread-safe) oppure un
        oggetto con boundingBox()/contains() come QgsGeometry.

        - maximin: massimizza la distanza minima dai punti esistenti/selezionati
        - variance: sceglie iterativamente dove la varianza di kriging e' massima
        - stratified: griglia regolare (con jitter) dentro l'area di studio
        - adaptive: campionamento casuale pesato verso le zone meno dense
        """
        existing = np.asarray(existing_points, dtype=float).reshape(-1, 2)
        existing = existing[np.all(np.isfinite(existing), axis=1)]
        n_new = int(n_new)
        if n_new < 1:
            raise ValueError("n_new must be >= 1")
        if method not in SAMPLING_METHODS:
            raise ValueError(f"Unknown sampling method '{method}'")
        rng = np.random.default_rng(random_state)
        xmin, ymin, xmax, ymax = self._boundary_bbox(existing, boundary_geom)

        if method == 'stratified':
            selected = self._stratified_design((xmin, ymin, xmax, ymax), boundary_geom, n_new, rng)
            return np.asarray(selected, dtype=float).reshape(-1, 2)

        n_candidates = int(n_candidates or min(max(500, n_new * 100), 20000))
        candidates = self._random_points_in_boundary(boundary_geom, (xmin, ymin, xmax, ymax), n_candidates, rng)
        if len(candidates) < n_new:
            raise ValueError("Could not generate enough candidate points inside the study area")

        if method == 'maximin':
            selected = self._maximin_design(existing, candidates, n_new)
        elif method == 'variance':
            selected = self._variance_reduction_design(existing, candidates, n_new, variogram_params)
        else:
            selected = self._adaptive_design(existing, candidates, n_new, rng,
                                             bandwidth=0.1 * float(np.hypot(xmax - xmin, ymax - ymin)))
        return np.asarray(selected, dtype=float).reshape(-1, 2)

    @staticmethod
    def _maximin_design(existing, candidates, n_new):
        if len(existing) > 0:
            dmin = cKDTree(existing).query(candidates)[0]
        else:
            dmin = np.full(len(candidates), np.inf)
        selected = []
        for _ in range(min(n_new, len(candidates))):
            if len(selected) == 0 and not np.isfinite(dmin).any():
                best = 0
            else:
                best = int(np.argmax(dmin))
            chosen = candidates[best]
            selected.append(chosen)
            dmin = np.minimum(dmin, np.linalg.norm(candidates - chosen, axis=1))
            dmin[best] = -np.inf
        return np.array(selected)

    def _variance_reduction_design(self, existing, candidates, n_new, variogram_params=None):
        """Greedy: ad ogni passo aggiunge il candidato con varianza di kriging massima."""
        if len(existing) == 0:
            return self._maximin_design(existing, candidates, n_new)
        if variogram_params and variogram_params.get('model_params'):
            mp = dict(variogram_params['model_params'])
            model_type = variogram_params.get('model_type', 'spherical')
        else:
            nn_dist = cKDTree(existing).query(existing, k=min(2, len(existing)))[0]
            typical = float(np.median(nn_dist[:, -1])) if len(existing) > 1 else 1.0
            mp = {'nugget': 0.0, 'sill': 1.0, 'range': max(typical * 4.0, 1e-6)}
            model_type = 'exponential'
        known = existing.copy()
        remaining = candidates.copy()
        selected = []
        for _ in range(min(n_new, len(candidates))):
            _, var = self._krige_targets(known, np.zeros(len(known)), remaining, mp, model_type,
                                         max_neighbors=DEFAULT_MAX_NEIGHBORS)
            best = int(np.nanargmax(var))
            chosen = remaining[best]
            selected.append(chosen)
            known = np.vstack([known, chosen])
            remaining = np.delete(remaining, best, axis=0)
            if len(remaining) == 0:
                break
        return np.array(selected)

    def _stratified_design(self, bbox, boundary_geom, n_new, rng):
        xmin, ymin, xmax, ymax = bbox
        w = max(xmax - xmin, 1e-9)
        h = max(ymax - ymin, 1e-9)
        nx = max(1, int(np.ceil(np.sqrt(n_new * w / h))))
        ny = max(1, int(np.ceil(n_new / nx)))
        x_step, y_step = w / nx, h / ny
        ii, jj = np.meshgrid(np.arange(nx), np.arange(ny))
        xs = xmin + (ii.ravel() + 0.5 + rng.uniform(-0.4, 0.4, ii.size)) * x_step
        ys = ymin + (jj.ravel() + 0.5 + rng.uniform(-0.4, 0.4, jj.size)) * y_step
        cells = np.column_stack([xs, ys])
        if boundary_geom is not None:
            if hasattr(boundary_geom, 'contains_many'):
                cells = cells[boundary_geom.contains_many(cells)]
            else:
                cells = cells[[self._point_in_boundary(boundary_geom, x, y) for x, y in cells]]
        if len(cells) > n_new:
            cells = cells[rng.choice(len(cells), n_new, replace=False)]
        if len(cells) < n_new:
            # area irregolare: completa con punti maximin dentro il boundary
            extra = self._random_points_in_boundary(boundary_geom, bbox, n_new * 50, rng)
            if len(extra):
                fill = self._maximin_design(cells, extra, n_new - len(cells))
                cells = np.vstack([cells, fill]) if len(cells) else fill
        return cells

    @staticmethod
    def _adaptive_design(existing, candidates, n_new, rng, bandwidth):
        if len(existing) == 0 or bandwidth <= 0:
            return candidates[rng.choice(len(candidates), min(n_new, len(candidates)), replace=False)]
        tree = cKDTree(existing)
        k = min(50, len(existing))
        d = tree.query(candidates, k=k)[0].reshape(len(candidates), -1)
        density = np.exp(-d ** 2 / (2 * bandwidth ** 2)).sum(axis=1)
        prob = 1.0 / (density + 1e-6)
        prob /= prob.sum()
        idx = rng.choice(len(candidates), min(n_new, len(candidates)), replace=False, p=prob)
        return candidates[idx]

    # ------------------------------------------------------------------
    # Grafici interattivi (Plotly)
    # ------------------------------------------------------------------
    def _require_plotly(self):
        if not self.plotly_available:
            raise NotImplementedError("Plotly visualization not available. Please install plotly.")

    def create_histogram(self, values, field_name=''):
        """Istogramma + box plot dei valori del campo selezionato."""
        self._require_plotly()
        values = np.asarray(values, dtype=float)
        values = values[np.isfinite(values)]
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2],
                            vertical_spacing=0.03)
        fig.add_trace(go.Histogram(x=values, nbinsx=min(50, max(10, int(np.sqrt(len(values))) * 2)),
                                   marker=dict(color='#1976D2'), name=field_name or _L('value')),
                      row=1, col=1)
        fig.add_trace(go.Box(x=values, name='', marker=dict(color='#F57C00'), boxmean=True,
                             showlegend=False), row=2, col=1)
        fig.update_layout(title=f"{_L('histogram_title')}: {field_name}" if field_name else _L('histogram_title'),
                          showlegend=False, margin=dict(l=40, r=20, t=50, b=40), bargap=0.05)
        fig.update_yaxes(title_text=_L('count'), row=1, col=1)
        fig.update_xaxes(title_text=field_name or _L('value'), row=2, col=1)
        return fig

    def create_interactive_variogram(self, variogram_data):
        """Grafico variogramma sperimentale + modello (+ direzionali se presenti)."""
        self._require_plotly()
        dist = np.asarray(variogram_data['distances'], dtype=float)
        semi = np.asarray(variogram_data['semivariances'], dtype=float)
        n_pairs = np.asarray(variogram_data.get('n_pairs', np.ones_like(dist)), dtype=float)
        sizes = 6 + 14 * (n_pairs / n_pairs.max()) if n_pairs.max() > 0 else np.full_like(dist, 10)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dist, y=semi, mode='markers', name=_L('empirical'),
            marker=dict(size=sizes, color='#1976D2', opacity=0.75, line=dict(color='white', width=1)),
            text=[f"{_L('distance')}: {d:.2f}<br>{_L('semivariance')}: {s:.4g}<br>{_L('pairs')}: {int(n)}"
                  for d, s, n in zip(dist, semi, n_pairs)],
            hovertemplate='%{text}<extra></extra>'))

        params = variogram_data.get('model_params')
        max_x = float(dist.max()) if len(dist) else 1.0
        max_y = float(semi.max()) if len(semi) else 1.0
        if params:
            x_model = np.linspace(0, max_x * 1.05, 200)
            y_model = self._evaluate_model(x_model, params['nugget'], params['sill'],
                                           params['range'], variogram_data.get('model_type', 'spherical'))
            fig.add_trace(go.Scatter(x=x_model, y=y_model, mode='lines',
                                     name=f"{_L('model')} {variogram_data.get('model_type', '')}",
                                     line=dict(color='#D32F2F', width=2.5)))
            max_y = max(max_y, params['sill']) * 1.1
            fig.add_shape(type='line', x0=0, x1=max_x * 1.05, y0=params['nugget'], y1=params['nugget'],
                          line=dict(color='#388E3C', width=1.5, dash='dash'))
            fig.add_shape(type='line', x0=0, x1=max_x * 1.05, y0=params['sill'], y1=params['sill'],
                          line=dict(color='#F57C00', width=1.5, dash='dash'))
            fig.add_shape(type='line', x0=params['range'], x1=params['range'], y0=0, y1=max_y,
                          line=dict(color='#7B1FA2', width=1.5, dash='dash'))
            fig.add_annotation(x=0, y=params['nugget'], text=f"{_L('nugget')} = {params['nugget']:.3g}",
                               showarrow=False, xanchor='left', yanchor='bottom', font=dict(color='#388E3C'))
            fig.add_annotation(x=0, y=params['sill'], text=f"{_L('sill')} = {params['sill']:.3g}",
                               showarrow=False, xanchor='left', yanchor='bottom', font=dict(color='#F57C00'))
            fig.add_annotation(x=params['range'], y=max_y, text=f"{_L('range')} = {params['range']:.3g}",
                               showarrow=False, xanchor='left', yanchor='top', font=dict(color='#7B1FA2'))

        aniso = variogram_data.get('anisotropy') or {}
        for direction, info in sorted((aniso.get('directions') or {}).items(), key=lambda kv: int(kv[0])):
            fig.add_trace(go.Scatter(
                x=info['distances'], y=info['semivariances'], mode='lines+markers',
                name=f"{int(direction)}°", visible='legendonly',
                marker=dict(size=5), line=dict(width=1, dash='dot')))

        fig.update_layout(title=_L('variogram_title'), xaxis_title=_L('distance'),
                          yaxis_title=_L('semivariance'), hovermode='closest', showlegend=True,
                          legend=dict(orientation='h', y=-0.2), margin=dict(l=50, r=20, t=50, b=50),
                          yaxis=dict(range=[0, max_y]))
        return fig

    def create_interactive_kriging_map(self, x, y, predictions, variances, data_points=None):
        """Mappa kriging interattiva: predizioni e incertezza impilate verticalmente."""
        self._require_plotly()
        predictions = np.asarray(predictions, dtype=float)
        variances = np.asarray(variances, dtype=float)
        pred_clean = np.where(np.isfinite(predictions), predictions, None)
        std = np.sqrt(np.where(np.isfinite(variances) & (variances >= 0), variances, np.nan))
        std_clean = np.where(np.isfinite(std), std, None)

        fig = make_subplots(rows=2, cols=1, subplot_titles=(_L('predicted'), _L('uncertainty')),
                            vertical_spacing=0.12)
        fig.add_trace(go.Heatmap(z=pred_clean, x=x, y=y, colorscale='Viridis',
                                 colorbar=dict(y=0.78, len=0.45, title=_L('value')),
                                 hovertemplate='X: %{x:.2f}<br>Y: %{y:.2f}<br>' + _L('value') + ': %{z:.3g}<extra></extra>'),
                      row=1, col=1)
        fig.add_trace(go.Heatmap(z=std_clean, x=x, y=y, colorscale='YlOrRd',
                                 colorbar=dict(y=0.22, len=0.45, title='σ'),
                                 hovertemplate='X: %{x:.2f}<br>Y: %{y:.2f}<br>σ: %{z:.3g}<extra></extra>'),
                      row=2, col=1)
        if data_points is not None and len(data_points):
            dp = np.asarray(data_points, dtype=float)
            for row in (1, 2):
                fig.add_trace(go.Scatter(x=dp[:, 0], y=dp[:, 1], mode='markers',
                                         marker=dict(size=4, color='black', opacity=0.6),
                                         name=_L('samples'), showlegend=(row == 1),
                                         hoverinfo='skip'), row=row, col=1)
        fig.update_layout(title=_L('kriging_title'), showlegend=True,
                          legend=dict(orientation='h', y=-0.05), margin=dict(l=50, r=20, t=60, b=40))
        for row in (1, 2):
            fig.update_yaxes(scaleanchor=f"x{'' if row == 1 else row}", scaleratio=1, row=row, col=1)
        return fig

    def create_ml_visualization(self, features, labels, method_name, class_names=None):
        """Scatter dei gruppi nello spazio delle prime due componenti principali."""
        self._require_plotly()
        if not self.ml_available:
            raise NotImplementedError("Machine Learning features not available. Please install scikit-learn.")
        features = np.asarray(features, dtype=float)
        labels = np.asarray(labels)
        if features.shape[1] > 2:
            pca = PCA(n_components=2)
            f2 = pca.fit_transform(features)
            var_exp = pca.explained_variance_ratio_
        else:
            f2 = features
            var_exp = [1.0, 0.0]
        palette = ['#E53935', '#43A047', '#1E88E5', '#FDD835', '#8E24AA',
                   '#00ACC1', '#FB8C00', '#6D4C41', '#546E7A', '#D81B60']
        fig = go.Figure()
        for i, lab in enumerate(np.unique(labels)):
            m = labels == lab
            if class_names and int(lab) in class_names:
                name = str(class_names[int(lab)])
            elif int(lab) == -1:
                name = 'noise'
            else:
                name = f"{_L('cluster')} {chr(ord('A') + int(lab) % 26)}"
            color = '#9E9E9E' if int(lab) == -1 else palette[i % len(palette)]
            fig.add_trace(go.Scatter(x=f2[m, 0], y=f2[m, 1], mode='markers',
                                     name=f"{name} (n={int(m.sum())})",
                                     marker=dict(size=7, color=color, line=dict(width=0.5, color='white'))))
        fig.update_layout(title=f"{_L('ml_title')} - {method_name}",
                          xaxis_title=f"PC1 ({var_exp[0]:.1%} {_L('variance_pct')})",
                          yaxis_title=f"PC2 ({var_exp[1]:.1%} {_L('variance_pct')})",
                          legend=dict(orientation='h', y=-0.2), margin=dict(l=50, r=20, t=50, b=50))
        return fig

    # ------------------------------------------------------------------
    # Grafici statici (matplotlib) - fallback senza QtWebEngine
    # ------------------------------------------------------------------
    @staticmethod
    def _fig_to_png(fig, dpi=110):
        FigureCanvasAgg(fig)
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
        return buf.getvalue()

    def _require_matplotlib(self):
        if not self.matplotlib_available:
            raise NotImplementedError("matplotlib not available")

    def render_histogram_png(self, values, field_name='', size=(6.0, 4.0)):
        self._require_matplotlib()
        values = np.asarray(values, dtype=float)
        values = values[np.isfinite(values)]
        fig = Figure(figsize=size)
        ax = fig.add_subplot(111)
        ax.hist(values, bins=min(50, max(10, int(np.sqrt(len(values))) * 2)), color='#1976D2', alpha=0.85)
        ax.set_xlabel(field_name or _L('value'))
        ax.set_ylabel(_L('count'))
        ax.set_title(_L('histogram_title'))
        ax.grid(alpha=0.3)
        return self._fig_to_png(fig)

    def render_variogram_png(self, variogram_data, size=(6.0, 4.2)):
        self._require_matplotlib()
        dist = np.asarray(variogram_data['distances'], dtype=float)
        semi = np.asarray(variogram_data['semivariances'], dtype=float)
        n_pairs = np.asarray(variogram_data.get('n_pairs', np.ones_like(dist)), dtype=float)
        sizes = 20 + 120 * (n_pairs / n_pairs.max()) if n_pairs.max() > 0 else 40
        fig = Figure(figsize=size)
        ax = fig.add_subplot(111)
        ax.scatter(dist, semi, s=sizes, color='#1976D2', alpha=0.75, edgecolor='white', label=_L('empirical'))
        params = variogram_data.get('model_params')
        max_x = float(dist.max()) if len(dist) else 1.0
        if params:
            xm = np.linspace(1e-9, max_x * 1.05, 200)
            ym = self._evaluate_model(xm, params['nugget'], params['sill'], params['range'],
                                      variogram_data.get('model_type', 'spherical'))
            ax.plot(xm, ym, color='#D32F2F', lw=2, label=f"{_L('model')} {variogram_data.get('model_type', '')}")
            ax.axhline(params['nugget'], color='#388E3C', ls='--', lw=1, label=f"{_L('nugget')} = {params['nugget']:.3g}")
            ax.axhline(params['sill'], color='#F57C00', ls='--', lw=1, label=f"{_L('sill')} = {params['sill']:.3g}")
            ax.axvline(params['range'], color='#7B1FA2', ls='--', lw=1, label=f"{_L('range')} = {params['range']:.3g}")
        aniso = variogram_data.get('anisotropy') or {}
        for direction, info in sorted((aniso.get('directions') or {}).items(), key=lambda kv: int(kv[0])):
            ax.plot(info['distances'], info['semivariances'], ls=':', lw=1, marker='.', label=f"{int(direction)}°")
        ax.set_xlabel(_L('distance'))
        ax.set_ylabel(_L('semivariance'))
        ax.set_title(_L('variogram_title'))
        ax.set_ylim(bottom=0)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8, loc='lower right')
        return self._fig_to_png(fig)

    def render_kriging_png(self, x, y, predictions, variances, data_points=None, size=(6.0, 7.5)):
        self._require_matplotlib()
        predictions = np.asarray(predictions, dtype=float)
        std = np.sqrt(np.where(np.isfinite(variances) & (np.asarray(variances) >= 0), variances, np.nan))
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        dx = (x[1] - x[0]) / 2 if len(x) > 1 else 0.5
        dy = (y[1] - y[0]) / 2 if len(y) > 1 else 0.5
        extent = [x.min() - dx, x.max() + dx, y.min() - dy, y.max() + dy]
        fig = Figure(figsize=size)
        for i, (data, cmap, title) in enumerate(((predictions, 'viridis', _L('predicted')),
                                                 (std, 'YlOrRd', _L('uncertainty')))):
            ax = fig.add_subplot(2, 1, i + 1)
            im = ax.imshow(data, origin='lower', extent=extent, cmap=cmap, aspect='equal', interpolation='nearest')
            if data_points is not None and len(data_points):
                dp = np.asarray(data_points, dtype=float)
                ax.scatter(dp[:, 0], dp[:, 1], s=4, color='black', alpha=0.5)
            ax.set_title(title)
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
        fig.suptitle(_L('kriging_title'))
        return self._fig_to_png(fig)

    def render_ml_png(self, features, labels, method_name, class_names=None, size=(6.0, 4.5)):
        self._require_matplotlib()
        features = np.asarray(features, dtype=float)
        labels = np.asarray(labels)
        if features.shape[1] > 2 and self.ml_available:
            pca = PCA(n_components=2)
            f2 = pca.fit_transform(features)
            var_exp = pca.explained_variance_ratio_
        else:
            f2 = features[:, :2]
            var_exp = [1.0, 0.0]
        palette = ['#E53935', '#43A047', '#1E88E5', '#FDD835', '#8E24AA',
                   '#00ACC1', '#FB8C00', '#6D4C41', '#546E7A', '#D81B60']
        fig = Figure(figsize=size)
        ax = fig.add_subplot(111)
        for i, lab in enumerate(np.unique(labels)):
            m = labels == lab
            if class_names and int(lab) in class_names:
                name = str(class_names[int(lab)])
            elif int(lab) == -1:
                name = 'noise'
            else:
                name = f"{_L('cluster')} {chr(ord('A') + int(lab) % 26)}"
            color = '#9E9E9E' if int(lab) == -1 else palette[i % len(palette)]
            ax.scatter(f2[m, 0], f2[m, 1], s=18, color=color, edgecolor='white', lw=0.3,
                       label=f"{name} (n={int(m.sum())})")
        ax.set_xlabel(f"PC1 ({var_exp[0]:.1%} {_L('variance_pct')})")
        ax.set_ylabel(f"PC2 ({var_exp[1]:.1%} {_L('variance_pct')})")
        ax.set_title(f"{_L('ml_title')} - {method_name}")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
        return self._fig_to_png(fig)
