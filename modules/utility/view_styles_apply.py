"""Applicare uno stile a un layer di QGIS: il QML dentro e fuori, la
ricetta delle etichette, e la scelta di chi comanda al caricamento
(spec «Stili delle viste», 2026-10-13). Qui c'è QGIS; il modello puro
sta in :mod:`view_styles`, la tabella in :mod:`view_styles_store`."""
from __future__ import annotations

import os
from typing import Optional

from .atlas_labels import US_FIELDS, label_field, labelled_ids, quota_labeling, us_labeling
from .view_styles import LabelRecipe, ViewSpec, choose_style, default_recipe, view_by_name

_STYLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "gis", "styles_spatialite")


def shipped_qml(spec: Optional[ViewSpec]) -> Optional[str]:
    """Il percorso del QML fornito con il plugin per la vista, o None."""
    if spec is None or not spec.qml:
        return None
    percorso = os.path.join(_STYLES_DIR, spec.qml)
    return percorso if os.path.isfile(percorso) else None


def _style_categories():
    """Solo quello che è uno stile: simbologia, etichette, resa. Le altre
    categorie (campi, moduli, proprietà personalizzate…) del layer di
    arrivo non si toccano (revisione, M5)."""
    from qgis.core import QgsMapLayer
    C = QgsMapLayer.StyleCategory
    return C.Symbology | C.Symbology3D | C.Labeling | C.Rendering


def export_qml_text(layer) -> str:
    """Simbologia ed etichette del layer come testo QML."""
    from qgis.core import QgsReadWriteContext
    from qgis.PyQt.QtXml import QDomDocument
    doc = QDomDocument()
    layer.exportNamedStyle(doc, QgsReadWriteContext(), _style_categories())
    return doc.toString()


def import_qml_text(layer, text: str) -> bool:
    """Il testo QML sul layer; ``False`` se non si legge o QGIS lo rifiuta."""
    from qgis.PyQt.QtXml import QDomDocument
    doc = QDomDocument()
    esito = doc.setContent(str(text or ""))
    ok = esito[0] if isinstance(esito, tuple) else bool(esito)
    if not ok or doc.documentElement().isNull():
        return False
    risultato = layer.importNamedStyle(doc, _style_categories())
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


def _current_format(layer):
    """Il formato del testo che il layer ha adesso, o None."""
    try:
        etichettatura = layer.labeling()
        if etichettatura is None:
            return None
        impostazioni = etichettatura.settings()
        return impostazioni.format()
    except Exception:                               # noqa: BLE001
        return None


def recipe_from_layer(layer) -> LabelRecipe:
    """La ricetta che descrive le etichette che il layer ha adesso — per un
    QML importato o uno stile salvato con QGIS: accese o spente, che cosa
    scrivono, una per unità (revisione, I2)."""
    from qgis.core import QgsPalLayerSettings
    try:
        etichettatura = layer.labeling()
        if etichettatura is None or not layer.labelsEnabled():
            return LabelRecipe()
        impostazioni = etichettatura.settings()
        espressione = str(impostazioni.fieldName or "")
        proprieta = impostazioni.dataDefinedProperties()
        mostra = proprieta.property(QgsPalLayerSettings.Property.Show)
        una = "$id IN" in str(mostra.expressionString() if mostra.isActive() else "")
        if una:
            return LabelRecipe(enabled=True, preset="us_circle", one_per_unit=True)
        if "quota" in espressione and "format_number" in espressione:
            return LabelRecipe(enabled=True, preset="quota", placement="above_symbol")
        return LabelRecipe(enabled=True, preset="field", expression=espressione or None)
    except Exception:                               # noqa: BLE001
        return LabelRecipe()


def apply_recipe(layer, recipe: LabelRecipe, touch_when_off: bool = True,
                 keep_format: bool = False) -> bool:
    """Le etichette secondo la ricetta. ``True`` se il layer è stato toccato.

    «Una per unità» si ricalcola qui, ogni volta: l'elenco dei disegni da
    etichettare che un QML porta con sé è quello del giorno in cui è stato
    salvato. Con ``keep_format`` il carattere resta quello che il layer ha
    (il QML di uno stile salvato): la ricetta rifà solo quello che è suo
    (revisione, I1)."""
    from qgis.core import QgsVectorLayerSimpleLabeling
    if not recipe.enabled or recipe.preset == "none":
        if touch_when_off:
            layer.setLabelsEnabled(False)
            return True
        return False
    formato_prima = _current_format(layer) if keep_format else None
    try:
        campi = [f.name() for f in layer.fields()]
        if recipe.preset == "us_circle":
            if label_field(campi, US_FIELDS) is None:
                return False
            ids = (labelled_ids(layer) or None) if recipe.one_per_unit else None
            nuove = us_labeling(campi, ids)
        elif recipe.preset == "quota":
            nuove = quota_labeling(campi)
        else:
            nuove = _field_labeling(layer, recipe)
    except Exception:                               # noqa: BLE001
        return False
    if nuove is None:
        return False
    if formato_prima is not None:
        impostazioni = nuove.settings()
        impostazioni.setFormat(formato_prima)
        nuove = QgsVectorLayerSimpleLabeling(impostazioni)
    layer.setLabeling(nuove)
    layer.setLabelsEnabled(True)
    return True


def periodization_rows(engine) -> list:
    """Le righe ``(sito, periodo, fase, cron_iniziale, cont_per)`` di
    ``periodizzazione_table``, per l'ordine per cronologia; ``[]`` se il
    database non c'è o non si legge."""
    if engine is None:
        return []
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            return [tuple(r) for r in conn.execute(
                text("SELECT sito, periodo, fase, cron_iniziale, cont_per FROM periodizzazione_table"))]
    except Exception:                               # noqa: BLE001
        return []


def enforce_unit_order(layer, engine=None, periodization=None, view_name: Optional[str] = None) -> bool:
    """L'ordine di disegno delle viste di unità come il Time Manager, sempre:
    prima i periodi per cronologia quando la periodizzazione si legge, poi
    ``order_layer`` dal più antico (0, sotto) al più recente (sopra), poi
    l'indice stratigrafico — così spegnendo una categoria si vede quello
    che sta sotto (Enzo, 13 ottobre 2026). L'ordine sta sul renderer,
    quindi va rimesso dopo ogni QML, salvato o fornito. Vale solo per le
    unità: con ``view_name`` la vista dev'essere del gruppo «unita»; senza,
    il layer dev'essere di poligoni (le quote hanno ``order_layer`` anche
    loro, ma sono punti)."""
    try:
        if layer is None or not layer.isValid() or "order_layer" not in layer.fields().names():
            return False
        if view_name is not None:
            spec = view_by_name(view_name)
            if spec is None or spec.group != "unita":
                return False
        else:
            from qgis.core import QgsWkbTypes
            if QgsWkbTypes.geometryType(layer.wkbType()) != QgsWkbTypes.GeometryType.PolygonGeometry:
                return False
        if periodization is None:
            periodization = periodization_rows(engine)
        from .create_style import apply_stratigraphic_order
        return bool(apply_stratigraphic_order(layer, periodization or None, override=True))
    except Exception:                               # noqa: BLE001
        return False


def apply_view_style(layer, view_name: str, site: Optional[str] = None, *, engine=None,
                     fallback: bool = True) -> str:
    """Chi comanda al caricamento: lo stile predefinito del sito, poi quello
    per tutti i siti, poi — se ``fallback`` — il QML fornito con la ricetta
    di partenza; con ``fallback=False`` (i caricatori che oggi caricano la
    vista nuda) senza stile salvato non si tocca niente.
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
            # Il QML porta già etichette accese o spente e il loro carattere:
            # la ricetta rifà solo quello che è suo (revisione, I1 e I2).
            apply_recipe(layer, scelto.recipe, touch_when_off=False, keep_format=True)
            enforce_unit_order(layer, engine, view_name=view_name)
            return "saved:%d" % int(scelto.id)
    if not fallback:
        enforce_unit_order(layer, engine, view_name=view_name)
        return "none"
    qml = shipped_qml(spec)
    if qml:
        try:
            esito = layer.loadNamedStyle(qml)
            riuscito = esito[1] if isinstance(esito, tuple) else bool(esito)
            if not riuscito:
                qml = None
        except Exception:                           # noqa: BLE001
            qml = None
    apply_recipe(layer, default_recipe(spec), touch_when_off=False)
    enforce_unit_order(layer, engine, view_name=view_name)
    return "shipped" if qml else "none"
