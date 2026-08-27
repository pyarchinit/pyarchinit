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

import contextlib
import io
import re
from typing import Optional, Tuple

#: Above this many edges ``splines=ortho`` is swapped for ``polyline``.
LARGE_MATRIX_EDGES = 600
#: cairo refuses bitmaps wider/taller than 32767 px; keep a margin.
MAX_RASTER_PX = 32000
#: Never render below this dpi.  The period export of the 1311-US DB lays
#: out 253 350 pt (~88 m) wide: even 12 dpi overflows cairo, so the floor is
#: 1 — the raster then is only an overview, the .svg/.pdf copies are the
#: readable output.
MIN_RASTER_DPI = 1
#: Graph attributes applied to large graphs (fast router, tighter spacing).
LARGE_GRAPH_ATTRS = {'splines': 'polyline', 'nodesep': '0.3', 'ranksep': '1'}
#: Acrobat/Preview show only a window of pages larger than 200 in per side
#: (the 1311-US period matrix PDF was 428 x 76 in: "vedo solo una parte").
MAX_VECTOR_PT = 14400
#: graphviz ``size`` (inches) used to keep vector output under MAX_VECTOR_PT.
VECTOR_SIZE_INCHES = 199

# dot prints big coordinates in exponent notation ("2.5335e+05").
_NUM = r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?'
_BB_RE = re.compile(
    r'\bbb="\s*(%s)\s*,\s*(%s)\s*,\s*(%s)\s*,\s*(%s)\s*"' % ((_NUM,) * 4))
_DPI_RE = re.compile(r'\bdpi=("?)[\d.]+\1')
_SIZE_RE = re.compile(r'\bsize=("?)[\d.,!]+\1')


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


def _set_root_attr(dot_text: str, pattern, assignment: str) -> str:
    text, n = pattern.subn(assignment, dot_text, count=1)
    if n:
        return text
    return re.sub(r'\{', '{\n\tgraph [%s];' % assignment, dot_text, count=1)


def set_dot_dpi(dot_text: str, dpi: int) -> str:
    """Rewrite (or add) the root ``dpi`` attribute of a DOT source."""
    return _set_root_attr(dot_text, _DPI_RE, 'dpi=%d' % int(dpi))


def vector_dot_source(dot_text: str, max_pt: int = MAX_VECTOR_PT,
                      size_inches: int = VECTOR_SIZE_INCHES) -> str:
    """DOT source for the .svg/.pdf copies: 1 pt = 1 pt (``dpi=72``) and,
    when the laid-out graph exceeds *max_pt* on a side, a root ``size``
    so graphviz scales the (lossless, zoomable) drawing to a page every
    viewer can open."""
    text = set_dot_dpi(dot_text, 72)
    size = laid_out_size_points(dot_text)
    if size and max(size) > max_pt:
        text = _set_root_attr(text, _SIZE_RE,
                              'size="%d,%d"' % (size_inches, size_inches))
    return text


@contextlib.contextmanager
def graphviz_stderr_guard(label: str = 'graphviz'):
    """Make ``graphviz.render()`` safe when ``sys.stderr`` is None.

    graphviz-python echoes whatever ``dot`` printed on stderr with
    ``sys.stderr.write()``.  Under a GUI python (QGIS on Windows without the
    Python console open, pythonw) ``sys.stderr`` is None, so any dot
    warning — e.g. "Two clusters named cluster_cont" in the period export —
    became ``AttributeError: 'NoneType' object has no attribute 'write'``
    and the export aborted (2026-08-27).  stderr is redirected into a
    buffer for the duration; the text is re-emitted with ``print()`` (a
    no-op when stdout is None) and is also available on the yielded buffer.
    """
    buf = io.StringIO()
    try:
        with contextlib.redirect_stderr(buf):
            yield buf
    finally:
        text = buf.getvalue().strip()
        if text:
            print(f"{label}: {text}")
