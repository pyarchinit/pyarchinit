"""
Bridge module for optional Rust acceleration.

Usage:
    from modules._rust_bridge import rust_bridge

    if rust_bridge.is_available():
        result = rust_bridge.topological_sort_with_levels(edges, reverse_order=True)
    else:
        # fallback to Python implementation

Geostat usage:
    if rust_bridge.is_available():
        distances, semivariances = rust_bridge.calculate_variogram(
            points_x, points_y, values, n_lags=20, max_lag=500.0
        )
"""


class _RustBridge:
    """Lazy-loading bridge to pyarchinit_core Rust module."""

    def __init__(self):
        self._module = None
        self._checked = False
        self._available = False

    def _load(self):
        if self._checked:
            return
        self._checked = True
        try:
            import pyarchinit_core
            self._module = pyarchinit_core
            self._available = True
        except ImportError:
            self._available = False

    def is_available(self):
        self._load()
        return self._available

    @property
    def version(self):
        self._load()
        if self._available:
            return self._module.__version__
        return None

    # ---------------------------------------------------------------
    # Graph functions
    # ---------------------------------------------------------------
    def topological_sort_with_levels(self, edges, reverse_order=True):
        self._load()
        if not self._available:
            raise RuntimeError("Rust module not available")
        return self._module.graph.topological_sort_with_levels(edges, reverse_order)

    def detect_and_remove_cycles(self, edges):
        self._load()
        if not self._available:
            raise RuntimeError("Rust module not available")
        return self._module.graph.detect_and_remove_cycles(edges)

    def transitive_reduction(self, edges):
        self._load()
        if not self._available:
            raise RuntimeError("Rust module not available")
        return self._module.graph.transitive_reduction(edges)

    # ---------------------------------------------------------------
    # Geostatistics functions
    # ---------------------------------------------------------------
    def calculate_variogram(self, points_x, points_y, values,
                            n_lags=20, max_lag=None):
        """Compute empirical variogram.

        Returns (lag_centers, semivariances) as two lists of equal length.
        """
        self._load()
        if not self._available:
            raise RuntimeError("Rust module not available")
        return self._module.geostat.calculate_variogram(
            list(points_x), list(points_y), list(values),
            n_lags, max_lag
        )

    def ordinary_kriging(self, points_x, points_y, values,
                         grid_x, grid_y,
                         variogram_model='spherical',
                         nugget=0.0, sill=1.0, range_param=100.0,
                         max_nearby=20):
        """Ordinary kriging on a regular grid.

        Returns (predictions_flat, variances_flat, ny, nx).
        """
        self._load()
        if not self._available:
            raise RuntimeError("Rust module not available")
        return self._module.geostat.ordinary_kriging(
            list(points_x), list(points_y), list(values),
            list(grid_x), list(grid_y),
            variogram_model,
            float(nugget), float(sill), float(range_param),
            int(max_nearby)
        )

    def idw_interpolation(self, points_x, points_y, values,
                          grid_x, grid_y,
                          power=2.0, search_radius=None):
        """Inverse Distance Weighting on a regular grid.

        Returns (predictions_flat, ny, nx).
        """
        self._load()
        if not self._available:
            raise RuntimeError("Rust module not available")
        return self._module.geostat.idw_interpolation(
            list(points_x), list(points_y), list(values),
            list(grid_x), list(grid_y),
            float(power), search_radius
        )

    def maximin_design(self, existing_x, existing_y,
                       n_new, n_candidates=1000):
        """Maximin sampling design.

        Returns (new_x, new_y).
        """
        self._load()
        if not self._available:
            raise RuntimeError("Rust module not available")
        return self._module.geostat.maximin_design(
            list(existing_x), list(existing_y),
            int(n_new), int(n_candidates)
        )

    def cross_validate_kriging(self, points_x, points_y, values,
                               variogram_model='spherical',
                               nugget=0.0, sill=1.0, range_param=100.0,
                               max_cv_points=50, max_nearby=30):
        """Leave-one-out cross-validation for kriging.

        Returns (rmse, mae).
        """
        self._load()
        if not self._available:
            raise RuntimeError("Rust module not available")
        return self._module.geostat.cross_validate_kriging(
            list(points_x), list(points_y), list(values),
            variogram_model,
            float(nugget), float(sill), float(range_param),
            int(max_cv_points), int(max_nearby)
        )

    # ---------------------------------------------------------------
    # Matrix layout functions
    # ---------------------------------------------------------------
    def harris_matrix_layout(self, edges, node_labels,
                             phase_groups=None,
                             layer_spacing=80.0,
                             node_spacing=60.0,
                             crossing_iterations=6):
        """Sugiyama-style layered layout for Harris Matrix visualization.

        Args:
            edges: list of (from_id, to_id) directed edges
            node_labels: list of all node identifiers
            phase_groups: optional list of (phase_name, [node_ids...]) for clustering
            layer_spacing: vertical distance between layers in px (default 80)
            node_spacing: horizontal distance between nodes in px (default 60)
            crossing_iterations: number of barycenter sweeps (default 6)

        Returns:
            dict with:
                'node_positions': list of (node_id, x, y)
                'edge_paths': list of (from_id, to_id, [(x, y), ...])
        """
        self._load()
        if not self._available:
            raise RuntimeError("Rust module not available")
        return self._module.matrix.harris_matrix_layout(
            edges, node_labels,
            phase_groups,
            float(layer_spacing),
            float(node_spacing),
            int(crossing_iterations)
        )


# Singleton instance
rust_bridge = _RustBridge()
