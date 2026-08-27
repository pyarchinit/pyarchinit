"""Unit tests for modules/utility/matrix_layout_policy.py (2026-08)."""
from __future__ import annotations

import sys

import pytest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.matrix_layout_policy import (  # noqa: E402
    LARGE_MATRIX_EDGES, MIN_RASTER_DPI, apply_large_graph_policy,
    laid_out_size_points,
    safe_raster_dpi, set_dot_dpi,
)

# root bb of the real 1311-US matrix laid out with splines=line
BIG = 'digraph {\n\tgraph [bb="0,0,79873,9612",\n\t\tdpi=300,\n\t\tnodesep=1\n\t];\n}'
SMALL = 'digraph {\n\tgraph [bb="0,0,720,540", dpi=300];\n\tsubgraph cluster_a { graph [bb="10,10,50,50"]; }\n}'


def test_small_graph_keeps_ortho():
    attrs = {'splines': 'ortho', 'nodesep': '1', 'ranksep': '3'}
    assert apply_large_graph_policy(attrs, LARGE_MATRIX_EDGES) is False
    assert attrs['splines'] == 'ortho'


def test_large_graph_switches_to_polyline_and_tightens_spacing():
    attrs = {'splines': 'ortho', 'nodesep': '1', 'ranksep': '3', 'dpi': '300'}
    assert apply_large_graph_policy(attrs, 2039) is True
    assert attrs['splines'] == 'polyline'
    assert float(attrs['nodesep']) < 1 and float(attrs['ranksep']) < 3
    assert attrs['dpi'] == '300'  # untouched here; clamped at render time


def test_bb_uses_root_graph_not_cluster():
    assert laid_out_size_points(SMALL) == (720.0, 540.0)
    assert laid_out_size_points('digraph { a -> b }') is None


def test_safe_dpi_clamps_only_when_bitmap_would_overflow():
    assert safe_raster_dpi(SMALL, '300') == 300
    dpi = safe_raster_dpi(BIG, '300')
    assert dpi < 300
    assert (79873 / 72.0) * dpi <= 32000
    assert safe_raster_dpi(BIG, '300', max_px=1) == MIN_RASTER_DPI  # floor
    assert safe_raster_dpi('no bb here', 'garbage') == 150  # fallback


def test_set_dot_dpi_rewrites_root_attribute_or_adds_it():
    out = set_dot_dpi(BIG, 28)
    assert 'dpi=28' in out and 'dpi=300' not in out
    assert 'dpi=28' in set_dot_dpi('digraph { graph [dpi="150"]; }', 28)
    added = set_dot_dpi('digraph {\n a -> b\n}', 40)
    assert 'dpi=40' in added and added.count('dpi=') == 1


# --- 2026-08-27: period export on the same DB -------------------------------
# dot writes the root bb of very wide layouts in exponent notation.
BIG_EXP = ('digraph {\n\tgraph [bb="0,0,2.5335e+05,7785",\n\t\tdpi=300,'
           '\n\t\tsplines=polyline\n\t];\n}')


def test_bb_in_exponent_notation_is_parsed_and_clamped():
    assert laid_out_size_points(BIG_EXP) == (253350.0, 7785.0)
    dpi = safe_raster_dpi(BIG_EXP, 300)
    # 253 350 pt = 3519 in → must go below 12 dpi to stay under 32 000 px
    assert dpi * 253350 / 72 <= 32000
    assert dpi >= 1


def test_stderr_guard_makes_graphviz_render_survive_sys_stderr_none(
        monkeypatch, tmp_path):
    """graphviz-python echoes dot's warnings with ``sys.stderr.write()``;
    under a GUI python (QGIS without the Python console open) sys.stderr
    is None and the period export died with
    "'NoneType' object has no attribute 'write'"."""
    import sys as _sys
    graphviz = pytest.importorskip("graphviz")
    from modules.utility.matrix_layout_policy import graphviz_stderr_guard
    # fixed-size node too small for its label → dot prints a Warning
    src = graphviz.Source(
        'digraph { a [shape=box, width=0.1, fixedsize=true, '
        'label="a rather long node label"] }')
    monkeypatch.setattr(_sys, "stderr", None)
    with pytest.raises(AttributeError):
        src.render(directory=str(tmp_path), filename="bare", format="dot")
    with graphviz_stderr_guard("dot") as captured:
        out = src.render(directory=str(tmp_path), filename="guarded",
                         format="dot")
    assert Path(out).is_file()
    assert "size too small for label" in captured.getvalue()


# --- 2026-08-27: vector copies must open in every PDF viewer ---------------
def test_vector_dot_source_caps_page_at_200_inches_and_uses_72_dpi():
    from modules.utility.matrix_layout_policy import (
        MAX_VECTOR_PT, vector_dot_source)
    # small layout: only the dpi changes (1 pt = 1 pt in the PDF)
    small = vector_dot_source(SMALL)
    assert 'dpi=72' in small and 'size=' not in small
    # 253 350 pt wide (the 1311-US period matrix): Acrobat/Preview clip
    # pages beyond 200 in → ask graphviz to scale the drawing down
    assert MAX_VECTOR_PT == 14400
    big = vector_dot_source(BIG_EXP)
    assert 'dpi=72' in big and 'dpi=300' not in big
    assert 'size="199,199"' in big
    # an existing root size= is replaced, not duplicated
    again = vector_dot_source(big.replace('size="199,199"', 'size="500,500"'))
    assert again.count('size=') == 1 and 'size="199,199"' in again
