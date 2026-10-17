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
    QTransform,
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

from .em_matrix_glyphs import (Glyph, GlyphLayer, contain, glyph_for,
                               is_property, parse_path, property_drawing)
from .em_matrix_layout import Box, Layout
from .em_matrix_svg import (OPACITA_FUORI, ROSSO_SALITA, _label_place,
                            _polygon, _short, write_svg)

#: Il dato in cui vive l'id del nodo sull'elemento grafico.
NODE_ID_ROLE = 0

#: Tetto dei pixel di un'immagine salvata. Una tela grande con la scala a
#: 2 chiedeva 0,3 GB sul caso Ventena (1311 US): meglio una scala più
#: bassa di un'immagine che non si alloca.
MAX_PIXELS = 40_000_000

#: Oltre questi elementi la scena si fa lenta da navigare; chi apre il
#: pannello può avvisare invece di lasciare l'utente a chiedersi perché.
HEAVY_ITEMS = 4000

#: Quanto sta sopra la linea di base l'etichetta a corpo 9. Il writer SVG
#: ragiona in linee di base, Qt in angolo alto a sinistra: questo è il
#: ponte fra i due, ed è il valore che la matrice ha sempre usato.
_ASCENDENTE = 12.0


def is_heavy(lay: Layout) -> bool:
    """Vero se il disegno è abbastanza grande da farsi sentire.

    Una casella non vale più uno: un pittogramma dell'Extended Matrix è
    fatto di livelli — il combinatore ne ha otto — e contarlo come una
    forma sola direbbe che una matrice di paradati è leggera quando non
    lo è.
    """
    elementi = len(lay.edges) + len(lay.bands) * 3
    for box in lay.boxes:
        glifo = glyph_for(box.unit.node_type)
        if glifo is not None:
            elementi += len(glifo.layers) + 1
        elif is_property(box.unit.node_type):
            elementi += 3
        else:
            elementi += 2
    return elementi > HEAVY_ITEMS


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


#: Il legame fra il nome del vertice di un tracciato e il metodo di Qt.
_CAPI = {"round": Qt.PenCapStyle.RoundCap, "square": Qt.PenCapStyle.SquareCap}
_GIUNTI = {"round": Qt.PenJoinStyle.RoundJoin,
           "bevel": Qt.PenJoinStyle.BevelJoin}


def _painter_path(comandi, evenodd: bool = False) -> QPainterPath:
    """Il tracciato di ``em_matrix_glyphs`` come percorso di Qt.

    I comandi sono già quelli del contratto — assoluti, solo
    ``M``/``L``/``C``/``Z`` — quindi qui non si interpreta niente: si
    ricopia. È il «new Path2D(d) and nothing else» del file, detto in Qt.
    """
    percorso = QPainterPath()
    if evenodd:
        percorso.setFillRule(Qt.FillRule.OddEvenFill)
    for comando in comandi:
        nome = comando[0]
        if nome == "M":
            percorso.moveTo(comando[1], comando[2])
        elif nome == "L":
            percorso.lineTo(comando[1], comando[2])
        elif nome == "C":
            percorso.cubicTo(comando[1], comando[2], comando[3],
                             comando[4], comando[5], comando[6])
        elif nome == "Z":
            percorso.closeSubpath()
    return percorso


def _layer_item(livello: GlyphLayer):
    """Un livello del pittogramma: un tracciato, un colore, e basta."""
    item = QGraphicsPathItem(
        _painter_path(livello.commands, livello.fill_rule == "evenodd"))
    item.setBrush(QBrush(QColor(livello.fill)) if livello.fill
                  else QBrush(Qt.BrushStyle.NoBrush))
    if livello.stroke:
        penna = QPen(QColor(livello.stroke))
        # Lo spessore è misurato nel viewBox: lo scala la trasformazione
        # del glifo, come in SVG. Mai una larghezza in pixel.
        penna.setWidthF(float(livello.stroke_width))
        penna.setCapStyle(_CAPI.get(livello.line_cap, Qt.PenCapStyle.FlatCap))
        penna.setJoinStyle(_GIUNTI.get(livello.line_join,
                                       Qt.PenJoinStyle.MiterJoin))
        item.setPen(penna)
    else:
        item.setPen(QPen(Qt.PenStyle.NoPen))
    if livello.opacity < 1.0:
        item.setOpacity(float(livello.opacity))
    return item


def _glyph_items(glifo: Glyph, box: Box):
    """Il pittogramma dentro la casella: ``contain``, centrato."""
    scala, dx, dy = contain(glifo, box.x, box.y, box.w, box.h)
    trasformazione = QTransform()
    trasformazione.translate(dx, dy)
    trasformazione.scale(scala, scala)
    elementi = []
    for livello in glifo.layers:
        item = _layer_item(livello)
        item.setTransform(trasformazione)
        elementi.append(item)
    return elementi


def _property_items(box: Box):
    """La proprietà: il campo grigio e la parentesi aperta a sinistra."""
    disegno = property_drawing(box.x, box.y, box.w, box.h)
    campo = QGraphicsPathItem(_painter_path(parse_path(disegno.field_d)))
    campo.setBrush(QBrush(QColor(disegno.fill)))
    campo.setPen(QPen(Qt.PenStyle.NoPen))
    parentesi = QGraphicsPathItem(_painter_path(parse_path(disegno.bracket_d)))
    parentesi.setBrush(QBrush(Qt.BrushStyle.NoBrush))
    penna = QPen(QColor(disegno.stroke))
    penna.setWidthF(disegno.stroke_width)
    penna.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    parentesi.setPen(penna)
    return [campo, parentesi]


def _node_items(box: Box):
    """Gli elementi grafici della casella, nell'ordine in cui si disegnano.

    Il pittogramma dell'Extended Matrix quando il tipo ne ha uno, la
    parentesi quando è una proprietà, la forma geometrica per tutto il
    resto — le stesse tre strade del writer SVG, perché quello che si
    vede a schermo e quello che esce dal file non divergano.
    """
    glifo = glyph_for(box.unit.node_type)
    if glifo is not None:
        return _glyph_items(glifo, box)
    if is_property(box.unit.node_type):
        return _property_items(box)
    return [_shape_item(box)]


def _arrow_item(da, a, colore):
    """La punta della freccia in fondo alla linea: senza, il verso del
    rapporto non si legge dove le epoche e la stratigrafia divergono."""
    import math

    dx, dy = a[0] - da[0], a[1] - da[1]
    lunghezza = math.hypot(dx, dy)
    if lunghezza < 1.0:
        return None
    ux, uy = dx / lunghezza, dy / lunghezza
    base = (a[0] - ux * 9.0, a[1] - uy * 9.0)
    lato = (-uy * 3.5, ux * 3.5)
    punta = QGraphicsPolygonItem(QPolygonF([
        QPointF(*a),
        QPointF(base[0] + lato[0], base[1] + lato[1]),
        QPointF(base[0] - lato[0], base[1] - lato[1])]))
    punta.setBrush(QBrush(colore))
    punta.setPen(QPen(colore))
    return punta


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

    # Il gruppo dei paradati di un'unità: la cornice tratteggiata di
    # EMStudio, sotto le linee e le caselle.
    for gruppo in lay.groups:
        cornice = QGraphicsRectItem(QRectF(gruppo.x, gruppo.y, gruppo.w, gruppo.h))
        penna = QPen(QColor("#9AA4B2"))
        penna.setStyle(Qt.PenStyle.DashLine)
        penna.setWidthF(1.0)
        cornice.setPen(penna)
        cornice.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        cornice.setZValue(-6)
        scene.addItem(cornice)

    for edge in lay.edges:
        percorso = QPainterPath(QPointF(*edge.points[0]))
        if edge.symmetric:
            # Due linee staccate: il segno di uguale, non una spezzata.
            percorso.lineTo(QPointF(*edge.points[1]))
            percorso.moveTo(QPointF(*edge.points[2]))
            percorso.lineTo(QPointF(*edge.points[3]))
        else:
            for x, y in edge.points[1:]:
                percorso.lineTo(QPointF(x, y))
        linea = QGraphicsPathItem(percorso)
        # Il legame di continuità più marcato: racconta una durata, non
        # una sovrapposizione. Il rosso della salita vince su tutto: dice
        # che stratigrafia e cronologia si contraddicono.
        if edge.upward:
            penna = QPen(QColor(ROSSO_SALITA))
            penna.setWidthF(2.2 if edge.continuity else 1.6)
        else:
            penna = QPen(QColor("#1A1A1A" if edge.continuity else "#6B7684"))
            penna.setWidthF(2.2 if edge.continuity else 1.4)
        linea.setPen(penna)
        linea.setZValue(-5)
        scene.addItem(linea)
        if not edge.symmetric:
            punta = _arrow_item(edge.points[-2], edge.points[-1],
                                penna.color())
            if punta is not None:
                punta.setZValue(-4)
                scene.addItem(punta)

    per_id: Dict[str, object] = {}
    for box in lay.boxes:
        fuori = bool(getattr(box.unit, "dimmed", False))
        suggerimento = ("%s\n%s" % (box.unit.label, box.unit.description)
                        if box.unit.description else box.unit.label)
        elementi = _node_items(box)
        for item in elementi:
            if fuori:
                # Non è fra le unità che si stanno guardando: sta nel
                # disegno solo perché un rapporto la cita. Lo sbiadito si
                # moltiplica a quello che il livello si porta — il velo
                # al 7% del combinatore resta un velo.
                item.setOpacity(item.opacity() * OPACITA_FUORI)
            item.setData(NODE_ID_ROLE, box.unit.node_id)
            item.setToolTip(suggerimento)
            item.setZValue(1)
            scene.addItem(item)
        per_id[box.unit.node_id] = elementi[0]

        x, y, colore = _label_place(box)
        testo = QGraphicsSimpleTextItem(_short(box.unit.label))
        testo.setFont(etichetta)
        testo.setBrush(QBrush(QColor(colore)))
        larghezza = testo.boundingRect().width()
        # ``_label_place`` dà la linea di base, come l'SVG; Qt vuole
        # l'angolo in alto a sinistra.
        testo.setPos(x - larghezza / 2, y - _ASCENDENTE)
        if fuori:
            testo.setOpacity(OPACITA_FUORI)
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
        pixel = rettangolo.width() * rettangolo.height()
        if pixel > 0:
            # Il tetto vale sempre: un minimo sulla scala lo rendeva
            # aggirabile da una tela enorme (review 2026-10-08).
            scala = min(scala, (MAX_PIXELS / pixel) ** 0.5)
        immagine = QImage(max(int(rettangolo.width() * scala), 1),
                          max(int(rettangolo.height() * scala), 1),
                          QImage.Format.Format_ARGB32)
        if immagine.isNull():
            return None
        immagine.fill(QColor("#FBFCFE"))
        pittore = QPainter(immagine)
        pittore.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.scene().render(pittore)
        pittore.end()
        if not immagine.save(str(path)):
            return None
        return str(path)
