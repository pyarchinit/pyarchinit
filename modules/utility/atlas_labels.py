"""Le etichette della tavola: il numero di US e la quota.

Enzo, 2026-10-09: «inserire il nome US in un cerchio, il nome in
grassetto, e la quota sul layer puntuale; la quota deve stare sopra la
linea del simbolo — il simbolo è un triangolino rosso e una linea
sottile orizzontale, quindi la quota deve andare sopra la linea
orizzontale».

La parte che sceglie e misura sta qui e si prova senza QGIS; quella che
costruisce gli oggetti di etichettatura importa Qt solo quando serve.
"""
from __future__ import annotations

from typing import Iterable, Optional, Sequence

#: Come si chiama il numero dell'unità, in ordine di preferenza: il nome
#: della scheda prima di quello della tabella dei disegni.
US_FIELDS = ("us", "us_s")

#: Come si chiama la quota nella vista delle quote.
QUOTA_FIELDS = ("quota_q", "quota")

#: Dove sta la linea orizzontale del simbolo della quota, in millimetri
#: rispetto al punto, negativo verso l'alto. **Misurato**, non dedotto:
#: disegnando il simbolo di `quote_us_view.qml` a 300 dpi, i pixel rossi
#: vanno da -2,7 a -0,8 mm e la riga più larga — la linea orizzontale —
#: sta a -2,7 mm, centrata sulla x del punto.
QUOTA_LINE_MM = -2.7

#: Dove va il centro del testo della quota: sopra la linea, con lo spazio
#: di mezza riga di testo perché non la tocchi.
QUOTA_OFFSET_MM = -4.2

#: Quanto è grande il testo, in millimetri.
US_TEXT_MM = 2.2
QUOTA_TEXT_MM = 2.0

#: Come si raggruppano i disegni di una stessa unità. La vista US ha una
#: riga per ogni **disegno**, non per ogni US: sul sito di esempio sono
#: 482 poligoni per 51 unità, e senza raggruppare la tavola esce coperta
#: da «36 36 36 36». L'identità è quella della scheda: area più numero.
US_GROUP_FIELDS = ("area", "us")
US_GROUP_FIELDS_ALT = ("area_s", "us_s")


#: Sotto questa lunghezza la linea di richiamo non si disegna: un
#: richiamo lungo zero è solo sporcizia sul disegno.
CALLOUT_MIN_MM = 2.0

#: Il campo che dice chi sta sopra a chi nel disegno.
STACK_FIELD = "order_layer"


def label_field(fields: Iterable[str], candidates: Sequence[str]) -> Optional[str]:
    """Il primo dei campi cercati che il layer possiede, o ``None``."""
    presenti = {str(f) for f in (fields or ())}
    for nome in candidates:
        if nome in presenti:
            return nome
    return None


def quota_expression(field: str) -> str:
    """La quota con due decimali: «12.3400000001» su una tavola è illeggibile."""
    return 'format_number("%s", 2)' % str(field).replace('"', '""')


def largest_per_group(rows):
    """Per ogni gruppo, l'id del disegno più grande. ``{chiave: fid}``.

    ``rows`` sono quadruple ``(fid, chiave, area, livello)``. La vista US
    ha una riga per ogni **disegno**: sul sito di esempio 482 poligoni
    per 37 unità, e senza questo la tavola esce coperta da «36 36 36 36».
    A parità d'area vince il livello più alto — quello che si vede.
    """
    migliori = {}
    for riga in rows or ():
        try:
            fid, chiave, area, livello = riga
            area = float(area or 0.0)
            livello = float(livello if livello is not None else 0.0)
        except (TypeError, ValueError):
            continue
        attuale = migliori.get(chiave)
        if attuale is None or (area, livello) > (attuale[1], attuale[2]):
            migliori[chiave] = (fid, area, livello)
    return {k: v[0] for k, v in migliori.items()}


def ids_expression(ids) -> Optional[str]:
    """``$id IN (…)``, o ``None`` se non c'è niente da etichettare.

    Si passano gli id invece di far calcolare a QGIS chi è coperto:
    `overlay_within` su sé stesso è O(n²) e si rivaluta a ogni disegno —
    misurato, su 482 poligoni non finiva in due minuti. Il conto si fa
    una volta in Python, con un indice spaziale, e solo sulle poche
    etichette che compaiono davvero.
    """
    elenco = sorted({int(i) for i in (ids or ())})
    if not elenco:
        return None
    return "$id IN (%s)" % ", ".join(str(i) for i in elenco)


def _richiamo():
    """La linea che collega l'etichetta spostata al suo disegno."""
    from qgis.core import QgsSimpleLineCallout, QgsUnitTypes
    from qgis.PyQt.QtGui import QColor

    richiamo = QgsSimpleLineCallout()
    richiamo.setEnabled(True)
    richiamo.lineSymbol().setColor(QColor("#7A2020"))
    richiamo.lineSymbol().setWidth(0.2)
    richiamo.setMinimumLength(CALLOUT_MIN_MM)
    richiamo.setMinimumLengthUnit(QgsUnitTypes.RenderUnit.RenderMillimeters)
    return richiamo


def _testo(dimensione_mm: float, grassetto: bool, colore: str):
    from qgis.core import QgsTextFormat, QgsUnitTypes
    from qgis.PyQt.QtGui import QColor, QFont

    formato = QgsTextFormat()
    carattere = QFont("Helvetica")
    carattere.setBold(bool(grassetto))
    formato.setFont(carattere)
    formato.setSize(float(dimensione_mm))
    formato.setSizeUnit(QgsUnitTypes.RenderUnit.RenderMillimeters)
    formato.setColor(QColor(colore))
    return formato


def us_labeling(fields, ids=None):
    """Il numero dell'unità, in grassetto dentro un cerchio bianco.

    Il cerchio serve a leggerlo sopra il riempimento della US, che è
    chiaro ma non bianco, e a non confonderlo con il disegno.
    """
    from qgis.core import (QgsPalLayerSettings, QgsTextBackgroundSettings,
                           QgsUnitTypes, QgsVectorLayerSimpleLabeling)
    from qgis.PyQt.QtCore import QSizeF
    from qgis.PyQt.QtGui import QColor

    campo = label_field(fields, US_FIELDS)
    if campo is None:
        return None
    impostazioni = QgsPalLayerSettings()
    impostazioni.fieldName = campo
    # Posizioni alternative invece di una sola: con `OverPoint` QGIS
    # scarta l'etichetta che non entra, e il numero sparisce. Così la
    # sposta, e il richiamo dice a quale disegno appartiene.
    impostazioni.placement = \
        QgsPalLayerSettings.Placement.OrderedPositionsAroundPoint
    impostazioni.centroidInside = True
    impostazioni.centroidWhole = False
    impostazioni.dist = 0.0
    impostazioni.setCallout(_richiamo())
    _niente_sovrapposizioni(impostazioni)
    # Un numero per unità, e solo se quella unità si vede: l'elenco lo
    # calcola `labelled_ids`, qui si legge soltanto.
    mostra = ids_expression(ids)
    if mostra:
        from qgis.core import QgsProperty
        impostazioni.dataDefinedProperties().setProperty(
            QgsPalLayerSettings.Property.Show,
            QgsProperty.fromExpression(mostra))
    formato = _testo(US_TEXT_MM, True, "#1A1A1A")
    sfondo = QgsTextBackgroundSettings()
    sfondo.setEnabled(True)
    sfondo.setType(QgsTextBackgroundSettings.ShapeType.ShapeCircle)
    sfondo.setFillColor(QColor("#FFFFFF"))
    sfondo.setStrokeColor(QColor("#7A2020"))
    sfondo.setStrokeWidth(0.25)
    sfondo.setStrokeWidthUnit(QgsUnitTypes.RenderUnit.RenderMillimeters)
    sfondo.setSizeType(QgsTextBackgroundSettings.SizeType.SizeBuffer)
    sfondo.setSize(QSizeF(0.9, 0.9))
    sfondo.setSizeUnit(QgsUnitTypes.RenderUnit.RenderMillimeters)
    formato.setBackground(sfondo)
    impostazioni.setFormat(formato)
    return QgsVectorLayerSimpleLabeling(impostazioni)


def quota_labeling(fields):
    """La quota, sopra la linea orizzontale del simbolo."""
    from qgis.core import (QgsPalLayerSettings, QgsUnitTypes,
                           QgsVectorLayerSimpleLabeling)

    campo = label_field(fields, QUOTA_FIELDS)
    if campo is None:
        return None
    impostazioni = QgsPalLayerSettings()
    impostazioni.fieldName = quota_expression(campo)
    impostazioni.isExpression = True
    impostazioni.placement = QgsPalLayerSettings.Placement.OverPoint
    impostazioni.xOffset = 0.0
    # Negativo = verso l'alto: provato disegnando, non dedotto.
    impostazioni.yOffset = QUOTA_OFFSET_MM
    impostazioni.offsetUnits = QgsUnitTypes.RenderUnit.RenderMillimeters
    impostazioni.setCallout(_richiamo())
    _niente_sovrapposizioni(impostazioni)
    impostazioni.setFormat(_testo(QUOTA_TEXT_MM, False, "#7A2020"))
    return QgsVectorLayerSimpleLabeling(impostazioni)


def _niente_sovrapposizioni(impostazioni) -> None:
    """Le etichette non si coprono mai fra loro, né coprono i simboli."""
    try:
        from qgis.core import Qgis

        posizionamento = impostazioni.placementSettings()
        posizionamento.setOverlapHandling(
            Qgis.LabelOverlapHandling.PreventOverlap)
        # Spostarsi è meglio che sparire: si accettano posizioni meno
        # buone pur di mostrare il numero.
        posizionamento.setAllowDegradedPlacement(True)
    except Exception:                               # noqa: BLE001
        pass
    try:
        ostacoli = impostazioni.obstacleSettings()
        ostacoli.setIsObstacle(True)
    except Exception:                               # noqa: BLE001
        pass


def labelled_ids(layer, group_fields=None):
    """Gli id dei disegni da etichettare: uno per unità, e solo se si vede.

    «Si vede» vuol dire che nessun disegno di livello più alto lo
    contiene per intero: una US coperta a metà si vede ancora, e la sua
    etichetta serve. Si usa l'indice spaziale, e il confronto si fa solo
    sui pochi candidati che toccano il disegno — non su tutti.
    """
    from qgis.core import QgsSpatialIndex

    campi = [f.name() for f in layer.fields()]
    chiave_campi = None
    for coppia in (US_GROUP_FIELDS, US_GROUP_FIELDS_ALT):
        if set(coppia) <= set(campi):
            chiave_campi = coppia
            break
    if chiave_campi is None:
        return []

    livelli, geometrie, righe = {}, {}, []
    for f in layer.getFeatures():
        g = f.geometry()
        if g is None or g.isEmpty():
            continue
        try:
            chiave = tuple(str(f[c]) for c in chiave_campi)
        except Exception:                           # noqa: BLE001
            continue
        livello = f[STACK_FIELD] if STACK_FIELD in campi else None
        livelli[f.id()] = -1e9 if livello is None else float(livello)
        geometrie[f.id()] = g
        righe.append((f.id(), chiave, g.area(), livelli[f.id()]))

    candidati = largest_per_group(righe)
    if STACK_FIELD not in campi:
        return list(candidati.values())             # senza ordine non si nasconde

    indice = QgsSpatialIndex(layer.getFeatures())
    visibili = []
    for fid in candidati.values():
        mia = geometrie.get(fid)
        if mia is None:
            continue
        coperta = False
        for altro in indice.intersects(mia.boundingBox()):
            if altro == fid or livelli.get(altro, -1e9) <= livelli[fid]:
                continue
            sopra = geometrie.get(altro)
            if sopra is not None and sopra.contains(mia):
                coperta = True
                break
        if not coperta:
            visibili.append(fid)
    return visibili
