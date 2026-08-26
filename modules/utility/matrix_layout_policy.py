"""Size-aware layout/render policy for the Harris-matrix graphviz exports.

Measured 2026-08 on a real DB (1311 US, 2039 edges, two hubs with ~545
relations each):

* ``dot`` layout with ``splines=ortho``: 1 s at 400 edges, 12 s at 800,
  **more than 15 min** at 2039 — the ortho router is super-linear —
  while ``polyline`` / ``spline`` lay out the same graph in about 1 s;
* the laid-out graph was 79 873 pt (~1109 in) wide: at 300 dpi cairo
  refuses the bitmap (the JPG is silently written as 0 bytes, the PNG is
  scaled by 0.098 and unreadable).

Pure functions (no Qt/QGIS imports) so they are unit-testable;
``pyarchinit_matrix_exp`` wires them into every export path.
"""
from __future__ import annotations

import re
from typing import Optional, Tuple

#: Above this many edges ``splines=ortho`` is swapped for ``polyline``.
LARGE_MATRIX_EDGES = 600
#: cairo refuses bitmaps wider/taller than 32767 px; keep a margin.
MAX_RASTER_PX = 32000
#: Never render below this dpi (vector copies are produced instead).
MIN_RASTER_DPI = 12
#: Graph attributes applied to large graphs (fast router, tighter spacing).
LARGE_GRAPH_ATTRS = {'splines': 'polyline', 'nodesep': '0.3', 'ranksep': '1'}

_BB_RE = re.compile(
    r'\bbb="\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*"')
_DPI_RE = re.compile(r'\bdpi=("?)[\d.]+\1')


def is_large_matrix(n_edges: int, threshold: int = LARGE_MATRIX_EDGES) -> bool:
    return n_edges > threshold


def apply_large_graph_policy(graph_attr, n_edges: int,
                             threshold: int = LARGE_MATRIX_EDGES) -> bool:
    """Mutate a graphviz ``graph_attr`` mapping for big graphs.

    Returns True when the policy was applied (caller may inform the user).
    """
    if not is_large_matrix(n_edges, threshold):
        return False
    graph_attr.update(LARGE_GRAPH_ATTRS)
    return True


def laid_out_size_points(dot_text: str) -> Optional[Tuple[float, float]]:
    """``(width, height)`` in points from the root ``bb`` of a laid-out DOT."""
    m = _BB_RE.search(dot_text)
    if not m:
        return None
    x0, y0, x1, y1 = (float(v) for v in m.groups())
    return abs(x1 - x0), abs(y1 - y0)


def safe_raster_dpi(dot_text: str, requested_dpi, max_px: int = MAX_RASTER_PX,
                    min_dpi: int = MIN_RASTER_DPI) -> int:
    """Largest dpi <= *requested_dpi* whose bitmap stays within *max_px*."""
    try:
        requested = int(float(requested_dpi))
    except (TypeError, ValueError):
        requested = 150
    size = laid_out_size_points(dot_text)
    if not size or max(size) <= 0:
        return requested
    fit = int(max_px / (max(size) / 72.0))
    return max(min_dpi, min(requested, fit))


def set_dot_dpi(dot_text: str, dpi: int) -> str:
    """Rewrite (or add) the root ``dpi`` attribute of a DOT source."""
    new = 'dpi=%d' % int(dpi)
    text, n = _DPI_RE.subn(new, dot_text, count=1)
    if n:
        return text
    return re.sub(r'\{', '{\n\tgraph [%s];' % new, dot_text, count=1)
