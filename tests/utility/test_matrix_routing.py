"""Che nessuna linea della matrice passi sotto a un nodo, e che
un'uguaglianza si disegni come un segno di uguale.

Chiesto da Enzo l'11 ottobre 2026: «la continuity, l'edge non deve
accavallarsi o andare sotto gli altri nodi … così anche per tutti gli archi
di tutti i nodi … un nodo si connette con un nodo, non con tutti (la
questione delle ridondanze) … metti anche qualche rapporto di uguaglianza
per verificare se si inseriscono sulla stessa linea orizzontale e si
collegano con due linee orizzontali senza arrow».

Si sposta la **linea**, non il nodo: le colonne portano l'ordine
stratigrafico e la fascia porta l'epoca, quindi muovere una casella per far
passare una freccia rompe proprio quello che la matrice dice.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

from modules.utility import em_matrix_layout as LAY
from modules.utility import em_matrix_records as REC
from modules.utility import em_matrix_svg as SVG
from modules.utility.em_matrix_model import MatrixModel, Relation, Unit

RADICE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RADICE / "tests" / "fixtures"))
import realistic_site_db as RSD  # noqa: E402


def _modello(n, archi, kind="overlies"):
    return MatrixModel(
        units=[Unit(node_id=str(i), label="US %d" % i, node_type="US",
                    epoch_id=None) for i in range(1, n + 1)],
        epochs=[],
        relations=[Relation(source=str(a), target=str(b), kind=kind)
                   for a, b in archi])


def _attraversamenti(lay) -> int:
    """Quante volte un arco entra in una casella che non è la sua."""
    totale = 0
    for e in lay.edges:
        altrui = [c for c in lay.boxes
                  if c.unit.node_id not in (e.source, e.target)]
        totale += LAY.attraversa(e.points, altrui)
    return totale


# ---------------------------------------------------------------------------
# Nessun arco sotto un nodo
# ---------------------------------------------------------------------------

#: Le forme in cui una linea deve scendere oltre la propria fila e trova
#: qualcuno in mezzo. «pila con salti» è quella che il guasto l'ha mostrato:
#: le US 2…7 incolonnate, e tre archi che arrivano dall'alto nel mezzo della
#: pila — la discesa passava attraverso la US 2, la 3 e la 4.
FORME = {
    "pila con salti": (10, [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7),
                            (1, 7), (2, 6), (3, 7), (8, 3), (9, 4), (10, 5)]),
    "pila profonda": (12, [(i, i + 1) for i in range(1, 12)]
                      + [(1, 12), (1, 8), (2, 10)]),
    "ventaglio": (9, [(1, i) for i in range(2, 9)] + [(2, 9), (3, 9)]),
    "colonne intrecciate": (12, [(1, 3), (3, 5), (5, 7), (2, 4), (4, 6),
                                 (6, 8), (1, 8), (2, 7), (9, 5), (10, 6),
                                 (11, 7), (12, 8)]),
}


@pytest.mark.parametrize("nome", sorted(FORME))
def test_nessun_arco_passa_dentro_una_casella_non_sua(nome):
    n, archi = FORME[nome]
    lay = LAY.layout(_modello(n, archi))
    assert lay.edges, "il disegno deve avere archi"
    assert _attraversamenti(lay) == 0


def test_una_stratigrafia_grande_resta_pulita_e_non_costa_troppo():
    """Quattrocento unità con rapporti locali: zero attraversamenti.

    La forma è quella della stratigrafia vera — una sequenza in cui ogni
    unità si lega a una o due vicine, non un grafo casuale. Su un grafo
    casuale denso una corsia libera può non esistere affatto, e là qualche
    attraversamento resta: la cerchiatura di quel limite è il test qui
    sotto, non questo.
    """
    import random
    random.seed(11)
    archi = set()
    for i in range(1, 400):
        for _ in range(random.choice((1, 1, 2))):
            salto = random.choice((1, 1, 1, 2, 2, 3))
            if i + salto <= 400:
                archi.add((i, i + salto))
    lay = LAY.layout(_modello(400, sorted(archi)))
    assert _attraversamenti(lay) == 0


def test_la_discesa_entra_di_fianco_quando_la_colonna_e_occupata():
    """La forma della soluzione, non solo il suo effetto.

    La US 8 sta in cima e deve arrivare alla US 3, che ha la US 2 sopra di
    sé nella stessa colonna: scendere sulla verticale della 3 vorrebbe dire
    passare attraverso la 2. L'arco arriva quindi **dal fianco**, cioè il
    suo ultimo tratto è orizzontale e tocca il bordo sinistro o destro
    della casella, non il bordo di sopra.
    """
    n, archi = FORME["pila con salti"]
    lay = LAY.layout(_modello(n, archi))
    box = {b.unit.node_id: b for b in lay.boxes}
    arco = next(e for e in lay.edges if (e.source, e.target) == ("8", "3"))
    (px, py), (qx, qy) = arco.points[-2], arco.points[-1]
    assert abs(py - qy) < 0.5, "l'ultimo tratto deve essere orizzontale"
    b = box["3"]
    assert abs(qx - b.x) < 1.0 or abs(qx - (b.x + b.w)) < 1.0, \
        "deve toccare un fianco della casella"
    assert b.y < qy < b.y + b.h, "all'altezza della casella"


# ---------------------------------------------------------------------------
# Le ridondanze: un nodo si collega a uno, non a tutti
# ---------------------------------------------------------------------------

def test_un_arco_che_un_cammino_piu_lungo_gia_dice_si_toglie():
    """A copre B, B copre C: l'arco A→C non aggiunge niente e sparisce."""
    lay = LAY.layout(_modello(3, [(1, 2), (2, 3), (1, 3)]))
    assert lay.removed_redundant == 1
    coppie = {(e.source, e.target) for e in lay.edges}
    assert coppie == {("1", "2"), ("2", "3")}


def test_un_anello_non_perde_i_suoi_archi():
    """Dentro un ciclo ogni arco ha una strada alternativa — il giro — e
    toglierlo cancellerebbe un rapporto che esiste. Un ciclo è un errore
    dell'archeologo da vedere, non da far sparire."""
    lay = LAY.layout(_modello(4, [(1, 2), (2, 3), (3, 4), (4, 1)]))
    assert lay.removed_redundant == 0
    assert len(lay.edges) == 4


# ---------------------------------------------------------------------------
# L'uguaglianza: stessa riga, due linee, nessuna punta
# ---------------------------------------------------------------------------

def _scavo(tmp_path):
    """Il modello della matrice costruito dal generatore del sito di prova."""
    RSD.build_realistic_site_db(tmp_path)
    con = sqlite3.connect(tmp_path / "db.sqlite")
    con.row_factory = sqlite3.Row
    records = [dict(r) for r in con.execute(
        "SELECT * FROM us_table WHERE sito=?", (RSD.SITO,))]
    periods = [dict(r) for r in con.execute(
        "SELECT * FROM periodizzazione_table WHERE sito=?", (RSD.SITO,))]
    con.close()
    return REC.model_from_records(records, periods), records, periods


def test_il_db_di_prova_ha_rapporti_di_uguaglianza(tmp_path):
    """Caso 9 del generatore: «Uguale a» e «Si lega a», con i reciproci."""
    model, _r, _p = _scavo(tmp_path)
    simmetriche = [r for r in model.relations
                   if r.kind in LAY.SYMMETRIC_KINDS]
    assert {r.kind for r in simmetriche} == {"equals", "bonded_to"}


def test_due_unita_uguali_stanno_sulla_stessa_riga(tmp_path):
    """La US 40 e la 41 sono la stessa cosa vista in due punti: stessa
    ordinata, e accostate."""
    model, _r, _p = _scavo(tmp_path)
    lay = LAY.layout(model)
    box = {b.unit.label: b for b in lay.boxes}
    for a, b in (("1.US40", "1.US41"), ("1.US42", "1.US43")):
        assert a in box and b in box, sorted(box)
        assert abs(box[a].y - box[b].y) < 0.5, (a, b, box[a].y, box[b].y)
        assert abs(box[a].x - box[b].x) > 1.0, "non sovrapposte"


def test_un_arco_di_uguaglianza_sono_due_linee_orizzontali_senza_punta(tmp_path):
    """Il segno di uguale: due linee alla stessa altezza, nessun poligono.

    Il verso non c'è — «uguale a» non dice chi sta sopra — quindi non ci va
    la punta di freccia.
    """
    model, _r, _p = _scavo(tmp_path)
    lay = LAY.layout(model)
    uguali = [e for e in lay.edges if e.symmetric]
    assert uguali, "il disegno deve avere almeno un'uguaglianza"
    for e in uguali:
        assert e.upward is False, "una simmetrica non ha verso: mai in salita"
        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = e.points[:4]
        assert abs(y1 - y2) < 0.01 and abs(y3 - y4) < 0.01, "orizzontali"
        assert abs(y1 - y3) > 1.0, "staccate, come il segno di uguale"
        assert abs((x2 - x1) - (x4 - x3)) < 0.01, "della stessa lunghezza"

    frammento = SVG._edge_svg(uguali[0])
    assert frammento.count("<line") == 2
    assert "polygon" not in frammento, "nessuna punta di freccia"
    assert "equality" in frammento


def test_sul_sito_di_prova_nessun_arco_passa_sotto_un_nodo(tmp_path):
    """La proprietà, misurata sui dati del generatore e non su una forma
    costruita a mano."""
    model, _r, _p = _scavo(tmp_path)
    lay = LAY.layout(model)
    assert lay.edges
    assert _attraversamenti(lay) == 0
