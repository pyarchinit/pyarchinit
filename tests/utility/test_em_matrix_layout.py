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


def test_a_crowded_level_wraps_instead_of_growing_forever():
    """Misurato sul caso Ventena (1311 US quasi tutte nello stesso
    periodo): senza avvolgimento la fascia veniva larga 103.000 pixel,
    cioè illeggibile e impossibile da salvare. I livelli affollati vanno
    a capo."""
    model = MatrixModel(
        units=[_unit("US%d" % n, "e") for n in range(200)],
        epochs=[_epoch("e", 1200, 1350)], relations=[])
    lay = layout(model)
    assert lay.width < 3000, lay.width
    assert len(lay.boxes) == 200
    righe = {round(b.y) for b in lay.boxes}
    assert len(righe) > 1


def test_wrapping_does_not_make_boxes_overlap():
    model = MatrixModel(
        units=[_unit("US%d" % n, "e") for n in range(60)],
        epochs=[_epoch("e", 1200, 1350)], relations=[])
    lay = layout(model)
    rettangoli = [(b.x, b.y, b.w, b.h) for b in lay.boxes]
    for i, (x1, y1, w1, h1) in enumerate(rettangoli):
        for x2, y2, w2, h2 in rettangoli[i + 1:]:
            assert (x1 + w1 <= x2 or x2 + w2 <= x1
                    or y1 + h1 <= y2 or y2 + h2 <= y1)


def test_a_wrapped_band_is_tall_enough_for_what_it_holds():
    model = MatrixModel(
        units=[_unit("US%d" % n, "e") for n in range(60)],
        epochs=[_epoch("e", 1200, 1350)], relations=[])
    lay = layout(model)
    banda = lay.bands[0]
    for box in lay.boxes:
        assert banda.y <= box.y and box.y + box.h <= banda.y + banda.h


def test_a_relation_a_longer_path_already_says_is_not_drawn():
    """Come il «tred» di Graphviz, chiesto da Enzo: se A copre B e B copre
    C, l'arco A→C non aggiunge niente e sporca il disegno. Si toglie dal
    DISEGNO, non dai dati."""
    model = MatrixModel(
        units=[_unit("A", "e"), _unit("B", "e"), _unit("C", "e")],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation("A", "B", "overlies"),
                   Relation("B", "C", "overlies"),
                   Relation("A", "C", "overlies")])
    lay = layout(model)
    assert len(lay.edges) == 2
    assert lay.removed_redundant == 1


def test_the_redundant_relation_still_ranks_the_units():
    """Toglierla dal disegno non deve spostare nessuno: i livelli si
    calcolano su tutti i rapporti."""
    model = MatrixModel(
        units=[_unit("A", "e"), _unit("B", "e"), _unit("C", "e")],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation("A", "B", "overlies"),
                   Relation("B", "C", "overlies"),
                   Relation("A", "C", "overlies")])
    lay = layout(model)
    y = {b.unit.label: b.y for b in lay.boxes}
    assert y["A"] < y["B"] < y["C"]


def test_reduction_can_be_turned_off():
    from modules.utility.em_matrix_layout import LayoutConfig

    model = MatrixModel(
        units=[_unit("A", "e"), _unit("B", "e"), _unit("C", "e")],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation("A", "B", "overlies"),
                   Relation("B", "C", "overlies"),
                   Relation("A", "C", "overlies")])
    lay = layout(model, LayoutConfig(transitive_reduction=False))
    assert len(lay.edges) == 3
    assert lay.removed_redundant == 0


def test_a_cycle_does_not_make_the_reduction_eat_everything():
    model = MatrixModel(
        units=[_unit("A", "e"), _unit("B", "e")],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation("A", "B", "overlies"),
                   Relation("B", "A", "overlies")])
    lay = layout(model)
    assert len(lay.edges) == 2


def test_the_continuity_link_is_marked_so_it_can_be_drawn_apart():
    """Il nodo di continuità sta nel periodo più recente e scende fino
    alla US che sopravvive fin lì: quel legame racconta una durata, non
    una sovrapposizione, e va distinto a vista."""
    model = MatrixModel(
        units=[_unit("CON500", "recente", node_type="BR"),
               _unit("USM12", "antica")],
        epochs=[_epoch("recente", 1550, 1599), _epoch("antica", 1451, 1499)],
        relations=[Relation("CON500", "USM12", "is_after")])
    lay = layout(model)
    assert len(lay.edges) == 1
    assert lay.edges[0].continuity is True


def test_inside_a_loop_no_relation_is_ever_erased():
    """Trovato dalla review: dentro un ciclo ogni arco ha una strada
    alternativa — il giro stesso — quindi la riduzione li toglieva TUTTI.
    Un ciclo nei rapporti è un errore dell'archeologo da vedere, non da
    far sparire: la riduzione vale solo fra gruppi diversi."""
    anello = [Relation("c0", "c1", "overlies"),
              Relation("c1", "c2", "overlies"),
              Relation("c2", "c3", "overlies"),
              Relation("c3", "c0", "overlies")]
    model = MatrixModel(
        units=[_unit("c%d" % n, "e") for n in range(4)],
        epochs=[_epoch("e", 1200, 1350)], relations=anello)
    lay = layout(model)
    assert len(lay.edges) == 4, [e.kind for e in lay.edges]
    assert lay.removed_redundant == 0


def test_a_loop_with_extra_relations_keeps_them_all():
    relazioni = [("A", "B"), ("A", "C"), ("B", "C"), ("B", "D"),
                 ("C", "D"), ("C", "E"), ("D", "E"), ("E", "A")]
    model = MatrixModel(
        units=[_unit(l, "e") for l in "ABCDE"],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation(a, b, "overlies") for a, b in relazioni])
    lay = layout(model)
    assert len(lay.edges) == len(relazioni)


def test_outside_a_loop_the_reduction_still_works():
    """Su un grafo senza cicli la riduzione deve restare quella di prima."""
    model = MatrixModel(
        units=[_unit(l, "e") for l in "ABC"],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation("A", "B", "overlies"),
                   Relation("B", "C", "overlies"),
                   Relation("A", "C", "overlies")])
    lay = layout(model)
    assert len(lay.edges) == 2 and lay.removed_redundant == 1


def test_the_same_relation_written_twice_is_one_line():
    model = MatrixModel(
        units=[_unit("A", "e"), _unit("B", "e")],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation("A", "B", "overlies")] * 4)
    lay = layout(model)
    assert len(lay.edges) == 1


def test_a_unit_related_to_itself_is_not_drawn():
    """La verifica rapporti lo segnala come errore: disegnarlo sarebbe un
    trattino sotto la casella che non vuol dire niente."""
    model = MatrixModel(units=[_unit("A", "e")],
                        epochs=[_epoch("e", 1200, 1350)],
                        relations=[Relation("A", "A", "overlies")])
    lay = layout(model)
    assert lay.edges == []


def test_a_relation_pointing_upwards_is_still_drawn_cleanly():
    """Se i periodi e la stratigrafia si contraddicono — chi copre sta in
    una fascia più antica — la linea non deve ripiegarsi su sé stessa."""
    model = MatrixModel(
        units=[_unit("copre", "antica"), _unit("coperta", "recente")],
        epochs=[_epoch("recente", 1900, 2000), _epoch("antica", 1200, 1350)],
        relations=[Relation("copre", "coperta", "overlies")])
    lay = layout(model)
    punti = lay.edges[0].points
    assert punti[0] != punti[-1]
    assert len(set(punti)) == len(punti), punti


def test_two_units_that_are_equal_sit_on_the_same_line():
    """Regola della matrice di Harris, chiesta da Enzo: «uguale a» e «si
    lega a» non sono una sovrapposizione — le due unità stanno sulla
    stessa riga, accostate, unite da due linee orizzontali senza frecce."""
    model = MatrixModel(
        units=[_unit("US1", "e"), _unit("US2", "e"), _unit("US3", "e")],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation("US1", "US2", "equals"),
                   Relation("US1", "US3", "overlies")])
    lay = layout(model)
    a = next(b for b in lay.boxes if b.unit.label == "US1")
    b_ = next(b for b in lay.boxes if b.unit.label == "US2")
    assert a.y == b_.y, "le uguali devono stare sulla stessa riga"
    assert abs(a.x - b_.x) < 2 * (a.w + 40), "devono stare accostate"


def test_an_equality_is_drawn_as_a_double_line_without_arrows():
    model = MatrixModel(
        units=[_unit("US1", "e"), _unit("US2", "e")],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation("US1", "US2", "equals")])
    lay = layout(model)
    arco = lay.edges[0]
    assert arco.symmetric is True
    assert len(arco.points) == 4, arco.points       # due linee orizzontali
    assert arco.points[0][1] == arco.points[1][1]
    assert arco.points[2][1] == arco.points[3][1]
    assert arco.points[0][1] != arco.points[2][1]


def test_an_equality_chain_keeps_the_whole_group_on_one_line():
    model = MatrixModel(
        units=[_unit("A", "e"), _unit("B", "e"), _unit("C", "e")],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation("A", "B", "equals"), Relation("B", "C", "si lega a")
                   if False else Relation("B", "C", "bonded_to")])
    lay = layout(model)
    assert len({b.y for b in lay.boxes}) == 1


def test_what_a_unit_covers_hangs_under_it_not_beside_the_margin():
    """«Non è esploso come una matrice di Harris»: chi copre deve stare
    sopra e in mezzo a quello che copre, non incolonnato a sinistra."""
    model = MatrixModel(
        units=[_unit("padre", "e"), _unit("figlio1", "e"), _unit("figlio2", "e")],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation("padre", "figlio1", "overlies"),
                   Relation("padre", "figlio2", "overlies")])
    lay = layout(model)
    padre = next(b for b in lay.boxes if b.unit.label == "padre")
    f1 = next(b for b in lay.boxes if b.unit.label == "figlio1")
    f2 = next(b for b in lay.boxes if b.unit.label == "figlio2")
    centro_padre = padre.x + padre.w / 2
    centro_figli = ((f1.x + f1.w / 2) + (f2.x + f2.w / 2)) / 2
    assert abs(centro_padre - centro_figli) < 4.0, (centro_padre, centro_figli)


def test_a_chain_stays_in_one_column():
    """Una sequenza semplice non deve sbandare a destra: ogni unità sotto
    la precedente."""
    model = MatrixModel(
        units=[_unit("US%d" % n, "e") for n in range(1, 5)],
        epochs=[_epoch("e", 1200, 1350)],
        relations=[Relation("US%d" % n, "US%d" % (n + 1), "overlies")
                   for n in range(1, 4)])
    lay = layout(model)
    assert len({round(b.x) for b in lay.boxes}) == 1
