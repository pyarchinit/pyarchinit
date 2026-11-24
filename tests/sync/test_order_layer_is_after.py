"""The stratigraphic order counts '>' — s3dgraphy's voice for is_after.

Since s3dgraphy 1.6.0.dev139 (MICRO-LG7) a temporal precedence synced from
an Extended Matrix graph reaches us_table.rapporti as '>' / '<' (until then
it was a spurious «Copre»). Order_layer_graph built the order from the
covers/fills/cuts/abuts groups and '>>' only, so those precedences left the
order (24 Nov 2026, agreed with E.D.). '>' points like «Copre»: the unit
holding the row is the later one; '<' is the reciprocal row and, like
«Coperto da», adds no edge of its own.
"""
from __future__ import annotations

import pytest


class _Bar:
    def setValue(self, *a):
        pass

    def setFormat(self, *a):
        pass

    def setStyleSheet(self, *a):
        pass


def _graph(us_data):
    from modules.gis.pyarchinit_pyqgis import Order_layer_graph

    ol = Order_layer_graph(None, "X", "1")
    ol.progress_bar = _Bar()
    ol.us_data = dict(us_data)
    ol.all_us = set(us_data)
    assert ol._build_graph()
    return ol


def _level_of(ol):
    levels = ol._topological_sort_with_levels(reverse_order=True)
    items = levels.items() if isinstance(levels, dict) else enumerate(levels)
    return {str(us): int(lvl) for lvl, uss in items for us in uss}


def test_is_after_arrow_is_an_edge_like_copre():
    ol = _graph({
        "3": "[['>', '2', '1', 'X']]",
        "2": "[['Copre', '1', '1', 'X'], ['<', '3', '1', 'X']]",
        "1": "[['Coperto da', '2', '1', 'X']]",
    })
    assert "2" in ol.graph_edges["3"]          # 3 is after 2
    assert "1" in ol.graph_edges["2"]          # 2 covers 1
    assert not ol.graph_edges.get("2", set()) & {"3"}   # '<' adds no edge


def test_is_after_chain_gives_three_levels():
    ol = _graph({
        "3": "[['>', '2', '1', 'X']]",
        "2": "[['>', '1', '1', 'X']]",
        "1": "[]",
    })
    level = _level_of(ol)
    assert level["1"] != level["2"] != level["3"]
    assert len(set(level.values())) == 3


@pytest.mark.parametrize("token", [">>", "Copre"])
def test_existing_precedences_unchanged(token):
    ol = _graph({
        "2": f"[['{token}', '1', '1', 'X']]",
        "1": "[]",
    })
    assert "1" in ol.graph_edges["2"]
