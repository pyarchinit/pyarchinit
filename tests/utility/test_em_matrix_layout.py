"""Dove finisce ogni casella: le fasce delle epoche e la stratigrafia.

L'impaginatore è puro — niente Qt, niente Graphviz, niente rete — così si
prova headless e la vista disegna soltanto quello che qui è già deciso.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.em_matrix_layout import layout  # noqa: E402
from modules.utility.em_matrix_model import (  # noqa: E402
    Epoch,
    MatrixModel,
    Relation,
    Unit,
)


def _unit(label, epoch_id=None, node_type="US"):
    return Unit(node_id=label, label=label, node_type=node_type,
                epoch_id=epoch_id)


def _epoch(node_id, start, end, name=None):
    return Epoch(node_id=node_id, name=name or node_id, start=start, end=end)


def test_each_unit_sits_inside_the_band_of_its_epoch():
    model = MatrixModel(
        units=[_unit("US1", "e_recente"), _unit("US2", "e_antica")],
        epochs=[_epoch("e_recente", 1800, 2022), _epoch("e_antica", 1200, 1350)],
        relations=[])
    lay = layout(model)
    per_epoca = {b.epoch.node_id: b for b in lay.bands if b.epoch}
    for box in lay.boxes:
        banda = per_epoca[box.unit.epoch_id]
        assert banda.y <= box.y
        assert box.y + box.h <= banda.y + banda.h


def test_the_most_recent_band_is_on_top():
    model = MatrixModel(
        units=[], relations=[],
        epochs=[_epoch("antica", 1200, 1350), _epoch("recente", 1800, 2022)])
    lay = layout(model)
    assert [b.epoch.node_id for b in lay.bands] == ["recente", "antica"]
    assert lay.bands[0].y < lay.bands[1].y


def test_what_overlies_is_drawn_above():
    """La stratigrafia si legge dall'alto: chi copre sta sopra chi è
    coperto, dentro la stessa fascia."""
    model = MatrixModel(
        units=[_unit("US1", "e"), _unit("US2", "e")],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation("US1", "US2", "overlies")])
    lay = layout(model)
    sopra = next(b for b in lay.boxes if b.unit.label == "US1")
    sotto = next(b for b in lay.boxes if b.unit.label == "US2")
    assert sopra.y < sotto.y


def test_a_cycle_does_not_hang_and_loses_nothing():
    """Uno scavo reale può avere un ciclo nei rapporti — la verifica
    rapporti lo segnala — e il disegno non è il posto per rifiutarlo."""
    model = MatrixModel(
        units=[_unit("A", "e"), _unit("B", "e"), _unit("C", "e")],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation("A", "B", "overlies"),
                   Relation("B", "C", "overlies"),
                   Relation("C", "A", "overlies")])
    lay = layout(model)
    assert len(lay.boxes) == 3


def test_units_without_an_epoch_get_their_own_band():
    model = MatrixModel(units=[_unit("US1"), _unit("US2", "e")],
                        epochs=[_epoch("e", 1200, 1350)],
                        relations=[])
    lay = layout(model)
    assert lay.bands[-1].epoch is None
    assert "epoca" in lay.bands[-1].label.lower()
    assert len(lay.boxes) == 2


def test_nothing_overlaps_inside_a_band():
    model = MatrixModel(
        units=[_unit("US%d" % n, "e") for n in range(1, 8)],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation("US1", "US2", "overlies")])
    lay = layout(model)
    rettangoli = [(b.x, b.y, b.w, b.h) for b in lay.boxes]
    for i, (x1, y1, w1, h1) in enumerate(rettangoli):
        for x2, y2, w2, h2 in rettangoli[i + 1:]:
            separati = (x1 + w1 <= x2 or x2 + w2 <= x1
                        or y1 + h1 <= y2 or y2 + h2 <= y1)
            assert separati, ((x1, y1, w1, h1), (x2, y2, w2, h2))


def test_every_relation_becomes_a_line_between_two_boxes():
    model = MatrixModel(
        units=[_unit("US1", "e"), _unit("US2", "e")],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation("US1", "US2", "overlies")])
    lay = layout(model)
    assert len(lay.edges) == 1
    punti = lay.edges[0].points
    assert len(punti) >= 2
    assert punti[0] != punti[-1]


def test_a_relation_towards_a_unit_that_is_not_drawn_is_dropped():
    model = MatrixModel(units=[_unit("US1", "e")],
                        epochs=[_epoch("e", 1200, 1350)],
                        relations=[Relation("US1", "fantasma", "overlies")])
    lay = layout(model)
    assert lay.edges == []


def test_the_canvas_is_big_enough_for_what_it_holds():
    model = MatrixModel(
        units=[_unit("US%d" % n, "e") for n in range(1, 6)],
        epochs=[_epoch("e", 1200, 1350)], relations=[])
    lay = layout(model)
    assert lay.width >= max(b.x + b.w for b in lay.boxes)
    assert lay.height >= max(b.y + b.h for b in lay.boxes)


def test_a_big_site_lays_out_once_and_quickly():
    """1311 US è il database Ventena: l'impaginazione è un passo solo e
    non deve bloccare la finestra."""
    unita = [_unit("US%d" % n, "e") for n in range(1311)]
    relazioni = [Relation("US%d" % n, "US%d" % (n + 1), "overlies")
                 for n in range(0, 1310, 2)]
    model = MatrixModel(units=unita, epochs=[_epoch("e", 1200, 1350)],
                        relations=relazioni)
    inizio = time.time()
    lay = layout(model)
    assert len(lay.boxes) == 1311
    assert time.time() - inizio < 5.0


def test_symmetric_relations_do_not_push_anything_down():
    """«Uguale a» non è una sovrapposizione: le due unità restano allo
    stesso livello."""
    model = MatrixModel(
        units=[_unit("US1", "e"), _unit("US2", "e")],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation("US1", "US2", "equals")])
    lay = layout(model)
    a = next(b for b in lay.boxes if b.unit.label == "US1")
    b_ = next(b for b in lay.boxes if b.unit.label == "US2")
    assert a.y == b_.y


def test_a_long_relation_leaves_its_box_before_travelling():
    """Guardando il primo disegno del sito di esempio: le linee lunghe
    scendevano in verticale attraverso le caselle sottostanti. La
    spezzata deve staccarsi dalla casella di partenza e poi spostarsi,
    non tagliare dritto per tutta la pagina."""
    model = MatrixModel(
        units=[_unit("US1", "alta"), _unit("US2", "bassa")],
        epochs=[_epoch("alta", 1800, 2022), _epoch("bassa", 1200, 1350)],
        relations=[Relation("US1", "US2", "overlies")])
    lay = layout(model)
    punti = lay.edges[0].points
    partenza = next(b for b in lay.boxes if b.unit.label == "US1")
    # il primo tratto è corto e verticale: esce dalla casella e basta
    assert punti[0][0] == punti[1][0]
    assert 0 < punti[1][1] - punti[0][1] <= 24
    assert punti[0][1] >= partenza.y + partenza.h
