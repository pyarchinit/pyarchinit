"""Che cosa inquadrare nella tavola, e a che scala.

Enzo, guardando le prime stampe buone (2026-10-09): «non credo la scala
sia giusta, dovresti far in modo che il disegno, a seconda del layout
usato, riempia la pagina e si scali in automatico, e la scala deve essere
corretta».

Tre cose diverse, e qui c'è la parte che si può decidere senza QGIS:
quale delle mappe del layout è quella grande, su che rettangolo
inquadrarla, e a quale scala **vera** arrotondare. 1:18,6 non è una scala
da disegno archeologico: si sale alla prima della serie che contiene
ancora tutto, perché arrotondare in giù taglierebbe fuori una parte dello
scavo.
"""
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

#: Le scale che un disegno archeologico porta scritte sotto. Si sale alla
#: prima che basta; oltre l'ultima si arrotonda al migliaio.
NICE_SCALES = (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500,
               1000, 2000, 2500, 5000, 10000, 20000, 25000, 50000, 100000)


def nice_scale(denominatore) -> int:
    """La prima scala vera che contiene ancora tutto il disegno."""
    try:
        valore = float(denominatore)
    except (TypeError, ValueError):
        return NICE_SCALES[0]
    if not (valore > 0) or valore != valore:        # <= 0, o NaN
        return NICE_SCALES[0]
    for scala in NICE_SCALES:
        if scala >= valore - 1e-9:
            return scala
    import math
    return int(math.ceil(valore / 1000.0)) * 1000


def main_map_index(misure: Sequence[Tuple[float, float]]) -> Optional[int]:
    """Quale mappa del layout è quella grande, per area del telaio.

    Il modello del Time Manager ne ha due: quella del disegno e
    l'inserto panoramico, che serve a dire dove si è nel mondo e che
    quindi **non** va inquadrato sullo scavo.
    """
    migliore, area_migliore = None, -1.0
    for i, misura in enumerate(misure or ()):
        try:
            area = float(misura[0]) * float(misura[1])
        except (TypeError, ValueError, IndexError):
            continue
        if area > area_migliore:
            migliore, area_migliore = i, area
    return migliore


def fitting_extent(box, margin: float = 0.06,
                   minimum: float = 1.0) -> Optional[tuple]:
    """Il rettangolo da inquadrare: i dati, più un po' d'aria.

    Dove è piatto — una sola US, una quota sola — si allarga di
    ``minimum`` invece di moltiplicare per zero: inquadrare un rettangolo
    di larghezza nulla è uno zoom infinito.
    """
    if not box:
        return None
    try:
        x1, y1, x2, y2 = (float(v) for v in box)
    except (TypeError, ValueError):
        return None
    larghezza, altezza = x2 - x1, y2 - y1
    dx = larghezza * margin if larghezza > 0 else minimum / 2.0
    dy = altezza * margin if altezza > 0 else minimum / 2.0
    return (x1 - dx, y1 - dy, x2 + dx, y2 + dy)
