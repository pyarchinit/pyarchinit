"""Unit tests for modules/utility/matrix_layout_policy.py (2026-08)."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.matrix_layout_policy import (  # noqa: E402
    LARGE_MATRIX_EDGES, apply_large_graph_policy, laid_out_size_points,
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
    assert safe_raster_dpi(BIG, '300', max_px=1) == 12  # floor
    assert safe_raster_dpi('no bb here', 'garbage') == 150  # fallback


def test_set_dot_dpi_rewrites_root_attribute_or_adds_it():
    out = set_dot_dpi(BIG, 28)
    assert 'dpi=28' in out and 'dpi=300' not in out
    assert 'dpi=28' in set_dot_dpi('digraph { graph [dpi="150"]; }', 28)
    added = set_dot_dpi('digraph {\n a -> b\n}', 40)
    assert 'dpi=40' in added and added.count('dpi=') == 1
