"""La scena Qt disegna davvero i pittogrammi: si guarda l'immagine.

Un disegno non si prova leggendo il sorgente. Qui la scena si costruisce
e si **rende**, poi si contano i pixel dei colori canonici
dell'Extended Matrix: se il tracciato non fosse arrivato a Qt, quei
colori nell'immagine non ci sarebbero.

Nessun widget: ``QGraphicsScene`` è un oggetto, non una finestra, ed è
la stessa strada che l'anteprima PNG percorre già
(``matrix_preview_png.matrix_image``). Costruire un ``QWidget`` qui
farebbe cadere il processo.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("qgis.core")

from qgis.core import QgsApplication  # noqa: E402

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.em_matrix_layout import layout  # noqa: E402
from modules.utility.em_matrix_model import (  # noqa: E402
    Epoch,
    MatrixModel,
    Unit,
)


@pytest.fixture(scope="module")
def qgs():
    app = QgsApplication.instance()
    if app is None:
        QgsApplication.setPrefixPath(
            os.environ.get("QGIS_PREFIX_PATH",
                           "/Applications/QGIS.app/Contents/MacOS"), True)
        app = QgsApplication([], False)
        app.initQgis()
    return app


def _immagine(tipi, scala: float = 4.0):
    from qgis.PyQt.QtGui import QColor, QImage, QPainter
    from qgis.PyQt.QtWidgets import QGraphicsScene

    from modules.utility.em_matrix_view import build_scene

    unita = [Unit(node_id=n, label=n, node_type=t, epoch_id="e")
             for n, t in tipi.items()]
    modello = MatrixModel(
        units=unita, epochs=[Epoch("e", "XV secolo", 1451, 1499, "#FFF0F5")],
        relations=[], title="prova")
    impaginato = layout(modello)
    scena = QGraphicsScene()
    elementi = build_scene(impaginato, scena)
    riquadro = scena.sceneRect()
    immagine = QImage(int(riquadro.width() * scala),
                      int(riquadro.height() * scala),
                      QImage.Format.Format_ARGB32)
    immagine.fill(QColor("#FBFCFE"))
    pittore = QPainter(immagine)
    pittore.setRenderHint(QPainter.RenderHint.Antialiasing)
    scena.render(pittore)
    pittore.end()
    # la scena torna indietro viva: se la raccogliesse il
    # garbage collector, Qt cancellerebbe anche i suoi elementi
    return immagine, impaginato, elementi, scena


def _quanti(immagine, esadecimale: str) -> int:
    """Quanti pixel di quel colore esatto ci sono nell'immagine."""
    from qgis.PyQt.QtGui import QColor

    voluto = QColor(esadecimale).rgb()
    conto = 0
    for y in range(immagine.height()):
        for x in range(immagine.width()):
            if immagine.pixel(x, y) & 0x00FFFFFF == voluto & 0x00FFFFFF:
                conto += 1
    return conto


def test_the_scene_paints_the_extractor_and_the_combiner(qgs):
    """I grigi canonici dell'Extended Matrix finiscono nell'immagine: il
    tracciato è arrivato a Qt, non solo all'SVG."""
    immagine = _immagine({"E1": "extractor", "C1": "combiner"})[0]
    assert _quanti(immagine, "#888687") > 200     # il corpo dell'estrattore
    assert _quanti(immagine, "#868384") > 200     # le frecce del combinatore


def test_the_scene_paints_the_property_field(qgs):
    immagine = _immagine({"P1": "property"})[0]
    assert _quanti(immagine, "#DEDDDE") > 200


def test_the_scene_paints_the_document_sheet(qgs):
    """Il foglio è bianco su carta chiara: si guarda il contorno nero."""
    immagine = _immagine({"D1": "document"})[0]
    assert _quanti(immagine, "#FFFFFF") > 100     # la carta del foglio
    assert _quanti(immagine, "#000000") > 20      # il bordo e la piega


def test_every_node_still_answers_with_its_id(qgs):
    """Un pittogramma è fatto di più elementi: cliccarne uno qualunque
    deve dire quale unità è, se no la matrice smette di rispondere al
    clic proprio sui paradati."""
    from modules.utility.em_matrix_view import NODE_ID_ROLE

    _im, _lay, elementi, _scena = _immagine(
        {"E1": "extractor", "P1": "property", "U1": "US"})
    assert set(elementi) == {"E1", "P1", "U1"}
    for node_id, item in elementi.items():
        assert item.data(NODE_ID_ROLE) == node_id
