"""Applicare uno stile a un layer di QGIS: il QML dentro e fuori, la
ricetta delle etichette, e la scelta di chi comanda al caricamento
(spec «Stili delle viste», 2026-10-13). Qui c'è QGIS; il modello puro
sta in :mod:`view_styles`, la tabella in :mod:`view_styles_store`."""
from __future__ import annotations

import os
from typing import Optional

from .atlas_labels import (US_FIELDS, label_field, label_quote_view, labelled_ids,
                           us_labeling)
from .view_styles import LabelRecipe, ViewSpec, choose_style, default_recipe, view_by_name

_STYLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "gis", "styles_spatialite")


def shipped_qml(spec: Optional[ViewSpec]) -> Optional[str]:
    """Il percorso del QML fornito con il plugin per la vista, o None."""
    if spec is None or not spec.qml:
        return None
    percorso = os.path.join(_STYLES_DIR, spec.qml)
    return percorso if os.path.isfile(percorso) else None


def export_qml_text(layer) -> str:
    """Simbologia ed etichette del layer come testo QML."""
    from qgis.PyQt.QtXml import QDomDocument
    doc = QDomDocument()
    layer.exportNamedStyle(doc)
    return doc.toString()


def import_qml_text(layer, text: str) -> bool:
    """Il testo QML sul layer; ``False`` se non si legge o QGIS lo rifiuta."""
    from qgis.PyQt.QtXml import QDomDocument
    doc = QDomDocument()
    esito = doc.setContent(str(text or ""))
    ok = esito[0] if isinstance(esito, tuple) else bool(esito)
    if not ok or doc.documentElement().isNull():
        return False
    risultato = layer.importNamedStyle(doc)
    riuscito = risultato[0] if isinstance(risultato, tuple) else bool(risultato)
    if riuscito:
        layer.triggerRepaint()
    return bool(riuscito)


def _field_labeling(layer, recipe: LabelRecipe):
    """Un'etichetta semplice su un campo o un'espressione, con posizione e
    scostamento in millimetri (preset ``field``)."""
    from qgis.core import QgsPalLayerSettings, QgsUnitTypes, QgsVectorLayerSimpleLabeling
    nomi = [f.name() for f in layer.fields()]
    testo = str(recipe.expression or "").strip()
    if not testo:
        return None
    impostazioni = QgsPalLayerSettings()
    if testo in nomi:
        impostazioni.fieldName = testo
        impostazioni.isExpression = False
    else:
        impostazioni.fieldName = testo
        impostazioni.isExpression = True
    if recipe.placement == "around_point":
        impostazioni.placement = QgsPalLayerSettings.Placement.AroundPoint
    else:
        impostazioni.placement = QgsPalLayerSettings.Placement.OverPoint
        impostazioni.centroidInside = True
        if recipe.placement == "above_symbol":
            impostazioni.quadOffset = QgsPalLayerSettings.QuadrantPosition.QuadrantAbove
            impostazioni.yOffset = -abs(float(recipe.offset_mm or 0.0))
            impostazioni.offsetUnits = QgsUnitTypes.RenderUnit.RenderMillimeters
    return QgsVectorLayerSimpleLabeling(impostazioni)


def apply_recipe(layer, recipe: LabelRecipe, touch_when_off: bool = True) -> bool:
    """Le etichette secondo la ricetta. ``True`` se il layer è stato toccato.

    «Una per unità» si ricalcola qui, ogni volta: l'elenco dei disegni da
    etichettare che un QML porta con sé è quello del giorno in cui è stato
    salvato."""
    if not recipe.enabled or recipe.preset == "none":
        if touch_when_off:
            layer.setLabelsEnabled(False)
            return True
        return False
    try:
        if recipe.preset == "us_circle":
            campi = [f.name() for f in layer.fields()]
            if label_field(campi, US_FIELDS) is None:
                return False
            ids = (labelled_ids(layer) or None) if recipe.one_per_unit else None
            nuove = us_labeling(campi, ids)
        elif recipe.preset == "quota":
            return label_quote_view(layer)
        else:
            nuove = _field_labeling(layer, recipe)
    except Exception:                               # noqa: BLE001
        return False
    if nuove is None:
        return False
    layer.setLabeling(nuove)
    layer.setLabelsEnabled(True)
    return True


def apply_view_style(layer, view_name: str, site: Optional[str] = None, *, engine=None) -> str:
    """Chi comanda al caricamento: lo stile predefinito del sito, poi quello
    per tutti i siti, poi il QML fornito con la ricetta di partenza.
    Torna ``"saved:<id>"``, ``"shipped"`` o ``"none"``."""
    spec = view_by_name(view_name)
    if spec is None:
        return "none"
    if engine is not None:
        try:
            from .view_styles_store import list_styles
            scelto = choose_style(list_styles(engine, view_name), site)
        except Exception:                           # noqa: BLE001
            scelto = None
        if scelto is not None and import_qml_text(layer, scelto.qml):
            apply_recipe(layer, scelto.recipe, touch_when_off=True)
            return "saved:%d" % int(scelto.id)
    qml = shipped_qml(spec)
    if qml:
        try:
            layer.loadNamedStyle(qml)
        except Exception:                           # noqa: BLE001
            qml = None
    apply_recipe(layer, default_recipe(spec), touch_when_off=False)
    return "shipped" if qml else "none"
