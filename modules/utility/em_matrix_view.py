"""La matrice a schermo, dentro QGIS, senza motori web.

Disegna quello che l'impaginatore ha deciso (``em_matrix_layout``): nessuna
rilettura del file, nessun Graphviz, nessun QtWebEngine. Quello che si
vede qui è lo stesso disegno che ``em_matrix_svg`` scrive su file, e che i
test provano senza aprire una finestra.
"""
from __future__ import annotations

from typing import Dict, Optional

from qgis.PyQt.QtCore import QPointF, QRectF, Qt, pyqtSignal
from qgis.PyQt.QtGui import (
    QBrush,
    QColor,
    QFont,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
)
from qgis.PyQt.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsPathItem,
    QGraphicsPolygonItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
)

from .em_matrix_layout import Box, Layout
from .em_matrix_svg import _polygon, _readable_on, _short, write_svg

#: Il dato in cui vive l'id del nodo sull'elemento grafico.
NODE_ID_ROLE = 0


def _pen(stroke: str, width: float, dash: str) -> QPen:
    pen = QPen(QColor(stroke or "#8C8C8C"))
    pen.setWidthF(min(float(width or 2.0), 3.0))
    if dash == "dashed":
        pen.setStyle(Qt.PenStyle.DashLine)
    elif dash == "dotted":
        pen.setStyle(Qt.PenStyle.DotLine)
    return pen


def _shape_item(box: Box):
    """L'elemento grafico della forma che il tipo dichiara."""
    stile = box.unit.style
    punti = _polygon(stile.shape, box.x, box.y, box.w, box.h)
    if punti:
        item = QGraphicsPolygonItem(
            QPolygonF([QPointF(x, y) for x, y in punti]))
    elif stile.shape in ("ellipse", "circle"):
        item = QGraphicsEllipseItem(QRectF(box.x, box.y, box.w, box.h))
    else:
        percorso = QPainterPath()
        raggio = 9.0 if "round" in stile.shape else 2.0
        percorso.addRoundedRect(QRectF(box.x, box.y, box.w, box.h),
                                raggio, raggio)
        item = QGraphicsPathItem(percorso)
    item.setBrush(QBrush(QColor(stile.fill or "#FFFFFF")))
    item.setPen(_pen(stile.stroke, stile.width, stile.dash))
    return item


def build_scene(lay: Layout, scene: QGraphicsScene) -> Dict[str, object]:
    """Riempie la scena e restituisce gli elementi per id di nodo."""
    scene.clear()
    scene.setSceneRect(0, 0, lay.width, lay.height)
    scene.setBackgroundBrush(QBrush(QColor("#FBFCFE")))

    etichetta = QFont()
    etichetta.setPointSizeF(9.0)
    titolo_banda = QFont()
    titolo_banda.setPointSizeF(9.5)
    titolo_banda.setBold(True)

    for band in lay.bands:
        sfondo = QGraphicsRectItem(QRectF(0, band.y, lay.width, band.h))
        colore = QColor(band.color or "#F5F5F5")
        colore.setAlpha(110)
        sfondo.setBrush(QBrush(colore))
        sfondo.setPen(QPen(QColor("#C8CDD4")))
        sfondo.setZValue(-20)
        scene.addItem(sfondo)

        nome = QGraphicsSimpleTextItem(_short(band.label, 26))
        nome.setFont(titolo_banda)
        nome.setBrush(QBrush(QColor("#2C4A6E")))
        nome.setPos(12, band.y + 8)
        nome.setZValue(-10)
        scene.addItem(nome)

        anni = QGraphicsSimpleTextItem(band.sublabel)
        anni.setBrush(QBrush(QColor("#5A6B80")))
        anni.setPos(12, band.y + 24)
        anni.setZValue(-10)
        scene.addItem(anni)

    for edge in lay.edges:
        percorso = QPainterPath(QPointF(*edge.points[0]))
        for x, y in edge.points[1:]:
            percorso.lineTo(QPointF(x, y))
        linea = QGraphicsPathItem(percorso)
        penna = QPen(QColor("#6B7684"))
        penna.setWidthF(1.4)
        if edge.symmetric:
            penna.setStyle(Qt.PenStyle.DashLine)
        linea.setPen(penna)
        linea.setZValue(-5)
        scene.addItem(linea)

    per_id: Dict[str, object] = {}
    for box in lay.boxes:
        item = _shape_item(box)
        item.setData(NODE_ID_ROLE, box.unit.node_id)
        item.setToolTip("%s\n%s" % (box.unit.label, box.unit.description)
                        if box.unit.description else box.unit.label)
        item.setZValue(1)
        scene.addItem(item)
        per_id[box.unit.node_id] = item

        testo = QGraphicsSimpleTextItem(_short(box.unit.label))
        testo.setFont(etichetta)
        testo.setBrush(QBrush(QColor(_readable_on(box.unit.style.fill))))
        larghezza = testo.boundingRect().width()
        testo.setPos(box.x + (box.w - larghezza) / 2, box.y + box.h / 2 - 8)
        testo.setData(NODE_ID_ROLE, box.unit.node_id)
        testo.setZValue(2)
        scene.addItem(testo)
    return per_id


class MatrixView(QGraphicsView):
    """La matrice navigabile: rotella per ingrandire, clic per scegliere."""

    selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHints(QPainter.RenderHint.Antialiasing
                            | QPainter.RenderHint.TextAntialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._layout: Optional[Layout] = None

    def show_layout(self, lay: Layout) -> None:
        self._layout = lay
        build_scene(lay, self.scene())
        self.fit()

    def fit(self) -> None:
        if self._layout is not None:
            self.fitInView(self.scene().sceneRect(),
                           Qt.AspectRatioMode.KeepAspectRatio)

    def zoom(self, fattore: float) -> None:
        self.scale(fattore, fattore)

    def wheelEvent(self, event):                    # noqa: N802 (API Qt)
        self.zoom(1.15 if event.angleDelta().y() > 0 else 1 / 1.15)

    def mousePressEvent(self, event):               # noqa: N802 (API Qt)
        item = self.itemAt(event.pos())
        if item is not None:
            node_id = item.data(NODE_ID_ROLE)
            if node_id:
                self.selected.emit(str(node_id))
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):         # noqa: N802 (API Qt)
        self.fit()

    def save_svg(self, path, title: str = "") -> Optional[str]:
        """Salva il disegno passando dal writer puro, non da Qt."""
        if self._layout is None:
            return None
        return write_svg(self._layout, path, title)

    def save_png(self, path, scala: float = 2.0) -> Optional[str]:
        if self._layout is None:
            return None
        rettangolo = self.scene().sceneRect()
        immagine = QImage(int(rettangolo.width() * scala),
                          int(rettangolo.height() * scala),
                          QImage.Format.Format_ARGB32)
        immagine.fill(QColor("#FBFCFE"))
        pittore = QPainter(immagine)
        pittore.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.scene().render(pittore)
        pittore.end()
        immagine.save(str(path))
        return str(path)
