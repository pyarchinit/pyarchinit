"""I due bottoni della verifica rapporti ci stanno dentro (2026-10-10).

Enzo: «i bottoni correggi e annulla non si leggono bene, allargali» — nel
suo schermo si leggeva «orreg» e «hiud». Il `.ui` concedeva **56 px** di
larghezza massima, e misurato con le font del `.ui` **ogni** lingua in cui
il plugin è tradotto ne chiede di più: il testo più lungo è il tedesco
«schließen» a 64 px, e Qt per un bottone ne vuole comunque 80.
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

UI = _ROOT / "gui" / "ui" / "US_USM.ui"

#: Le traduzioni di «Fix» e «close» nei dieci .ts, più il tedesco, che è la
#: più lunga. Se si aggiunge una lingua con una parola più lunga di così, è
#: questo test a dirlo.
ETICHETTE = ("Fix", "close", "Correggi", "chiudi", "Corregir", "cerrar",
             "Corriger", "fermer", "Beheben", "schließen", "tancar",
             "aproape")


def _bottone(nome):
    radice = ET.parse(UI).getroot()
    for w in radice.iter("widget"):
        if w.get("class") == "QPushButton" and w.get("name") == nome:
            return w
    raise AssertionError("bottone %s non trovato in US_USM.ui" % nome)


def _larghezza(widget, proprieta):
    for p in widget.findall("property"):
        if p.get("name") == proprieta:
            return int(p.find("size").find("width").text)
    return None


def test_the_two_buttons_are_wide_enough_for_every_language():
    for nome in ("pushButton_fix", "pushButton_cancel"):
        w = _bottone(nome)
        massima = _larghezza(w, "maximumSize")
        minima = _larghezza(w, "minimumSize")
        assert massima is None or massima >= 110, \
            "%s: tetto a %s px, le etichette tradotte non ci stanno" % (nome, massima)
        assert minima is not None and minima >= 80, \
            "%s: senza un pavimento il layout può stringerlo" % nome


def test_the_longest_label_fits_in_the_cap():
    """Misurato con le font del `.ui`, non a occhio. Salta se Qt non c'è."""
    try:
        from qgis.PyQt.QtGui import QFont
        from qgis.PyQt.QtWidgets import QApplication, QPushButton
    except Exception:                               # pragma: no cover
        import pytest
        pytest.skip("Qt non disponibile")
    app = QApplication.instance() or QApplication([])
    font = QFont("Damascus", 11)
    serve = 0
    for testo in ETICHETTE:
        b = QPushButton(testo)
        b.setFont(font)
        serve = max(serve, b.sizeHint().width())
    tetto = _larghezza(_bottone("pushButton_fix"), "maximumSize")
    assert serve <= tetto, \
        "l'etichetta più lunga chiede %d px, il tetto ne dà %d" % (serve, tetto)
