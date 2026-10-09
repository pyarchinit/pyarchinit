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


def us_group_expression(fields) -> Optional[str]:
    """La chiave con cui si raggruppano i disegni della stessa unità."""
    presenti = {str(f) for f in (fields or ())}
    for coppia in (US_GROUP_FIELDS, US_GROUP_FIELDS_ALT):
        if set(coppia) <= presenti:
            return "concat(%s)" % ", '-', ".join('"%s"' % c for c in coppia)
    return None


def us_show_expression(fields) -> Optional[str]:
    """Mostra l'etichetta solo sul disegno più grande di ogni unità.

    Così il numero compare **una volta per US** invece che su ciascuno
    dei suoi poligoni. Senza chiave di raggruppamento si etichetta tutto,
    che è il comportamento di prima: meglio ripetuto che assente.
    """
    chiave = us_group_expression(fields)
    if chiave is None:
        return None
    return "$area >= maximum($area, group_by:=%s)" % chiave


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


def us_labeling(fields):
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
    impostazioni.placement = QgsPalLayerSettings.Placement.OverPoint
    impostazioni.centroidInside = True
    impostazioni.centroidWhole = False
    # Un numero per unità, non uno per disegno.
    mostra = us_show_expression(fields)
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
    impostazioni.setFormat(_testo(QUOTA_TEXT_MM, False, "#7A2020"))
    return QgsVectorLayerSimpleLabeling(impostazioni)
