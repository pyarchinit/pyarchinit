"""La sopravvivenza di un'unità nelle epoche intermedie (5.13.122-alpha):
le epoche si mettono in fila per periodo e fase, non per data — un periodo
senza data esce dalla libreria con inizio 0.0, e contarlo come anno zero
faceva sopravvivere l'unità in un periodo che non la riguarda (revisione del
16-10-2026)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

pytest.importorskip("s3dgraphy")


def _grafo(epoche, prima, ultima):
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.epoch_node import EpochNode
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    g = Graph("prova")
    for eid, inizio in epoche:
        g.add_node(EpochNode(node_id=eid, name=eid, start_time=inizio, end_time=inizio))
    g.add_node(StratigraphicUnit(node_id="u1", name="US1"))
    g.add_edge("f1", "u1", prima, "has_first_epoch")
    g.add_edge("s1", "u1", ultima, "survive_in_epoch")
    return g


def _sopravvive(g):
    from modules.s3dgraphy.sync.graph_projector import _close_epoch_spans
    _close_epoch_spans(g)
    return {e.edge_target for e in g.edges if e.edge_source == "u1" and e.edge_type == "survive_in_epoch"}


def test_un_periodo_senza_data_non_e_l_anno_zero():
    g = _grafo([("epoch_1_1", -100.0), ("epoch_2_1", 200.0), ("epoch_3_1", 0.0)], "epoch_1_1", "epoch_2_1")
    assert _sopravvive(g) == {"epoch_2_1"}


def test_le_fasi_con_la_stessa_data_contano():
    g = _grafo([("epoch_1_1", 100.0), ("epoch_1_2", 100.0), ("epoch_2_1", 200.0)], "epoch_1_1", "epoch_2_1")
    assert _sopravvive(g) == {"epoch_1_2", "epoch_2_1"}


def test_anche_con_i_periodi_numerati_dal_piu_recente():
    g = _grafo([("epoch_1_1", 300.0), ("epoch_2_1", 200.0), ("epoch_3_1", 100.0)], "epoch_3_1", "epoch_1_1")
    assert _sopravvive(g) == {"epoch_1_1", "epoch_2_1"}
