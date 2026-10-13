"""Chi scrive le etichette in ettari? Non pyArchInit (13 ottobre 2026:
cercato in tutto il plugin, nei QML forniti, nel database, nel profilo di
QGIS e negli altri plugin attivi — niente). Restano i layer del progetto
e le annotazioni: questo audit li guarda e lo dice in chiaro al
caricamento della vista US, col nome di chi le porta. Parte pura
(:func:`looks_like_area`, :func:`hectare_label_sources`) e lettura del
progetto QGIS (:func:`audit_project`)."""
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

_AREA = re.compile(r"\$area|\barea\s*\(|\$length|/\s*10000\b|\bha\b|m²|mq\b", re.I)
_HA_TEXT = re.compile(r"\d[\d.,]*\s*ha\b", re.I)

_M = {
    "it": {"layer": "Le etichette in ettari vengono dal layer «{name}» del progetto (espressione: {expr}), non da pyArchInit: spegnile dalle proprietà di quel layer o toglilo.",
           "preview": "{n} layer «pyarchinit_us_view» della Map preview, registrati nel progetto fuori dal pannello dei layer, portano etichette in ettari (espressione: {expr}): pyArchInit li toglie alla prossima apertura della Map preview.",
           "annotations": "{n} annotazioni del progetto scrivono un'area in ettari (livello «Annotazioni» nel pannello dei layer), non pyArchInit."},
    "en": {"layer": "The hectare labels come from the project layer “{name}” (expression: {expr}), not from pyArchInit: switch them off in that layer's properties or remove it.",
           "preview": "{n} “pyarchinit_us_view” layers of the Map preview, registered in the project outside the layers panel, carry hectare labels (expression: {expr}): pyArchInit removes them the next time the Map preview opens.",
           "annotations": "{n} project annotations write an area in hectares (the “Annotations” layer in the layers panel), not pyArchInit."},
}

#: Il nome che la Map preview dà ai suoi due layer, registrati nel progetto
#: ma non nel pannello (``addMapLayers(…, False)``).
PREVIEW_LAYER_NAME = "pyarchinit_us_view"


def looks_like_area(expression: Optional[str]) -> bool:
    """Vero se un'espressione di etichetta scrive un'area o un'unità di
    misura: ``$area``, ``area(...)``, ``/10000``, «ha», «m²»."""
    return bool(expression) and bool(_AREA.search(str(expression)))


def hectare_label_sources(layers: Iterable[Sequence[Any]],
                          annotation_texts: Iterable[str] = ()) -> Dict[str, Any]:
    """``layers``: ``(nome, etichette accese, espressione[, nel pannello])``;
    ``annotation_texts``: i testi delle annotazioni del progetto. Torna i
    layer accesi con un'espressione d'area, quali di questi sono i resti
    della Map preview (nome della preview, fuori dal pannello) e quante
    annotazioni scrivono ettari."""
    trovati: List[Tuple[str, str]] = []
    preview: List[str] = []
    for voce in layers:
        nome, accese, espressione = voce[0], voce[1], voce[2]
        nel_pannello = bool(voce[3]) if len(voce) > 3 else True
        if accese and looks_like_area(espressione):
            trovati.append((str(nome), str(espressione)))
            if str(nome) == PREVIEW_LAYER_NAME and not nel_pannello:
                preview.append(str(nome))
    quante = sum(1 for t in annotation_texts if t and _HA_TEXT.search(str(t)))
    return {"layers": trovati, "preview": preview, "annotations": quante}


def describe(esito: Dict[str, Any], lang: Optional[str] = None) -> List[str]:
    """Le frasi da mostrare: una per layer (col nome e l'espressione), una
    per i resti della Map preview, una per le annotazioni; vuoto se non c'è
    niente da dire."""
    m = _M["it" if str(lang or "it")[:2] == "it" else "en"]
    frasi: List[str] = []
    resti = list(esito.get("preview") or [])
    strati = [s for s in (esito.get("layers") or []) if not (resti and s[0] == PREVIEW_LAYER_NAME)]
    for nome, espressione in strati[:5]:
        frasi.append(m["layer"].format(name=nome, expr=str(espressione)[:80]))
    if resti:
        espressione = next((e for n, e in (esito.get("layers") or []) if n == PREVIEW_LAYER_NAME), "")
        frasi.append(m["preview"].format(n=len(resti), expr=str(espressione)[:80]))
    if esito.get("annotations"):
        frasi.append(m["annotations"].format(n=esito["annotations"]))
    return frasi


def _expressions_of(layer) -> List[str]:
    """Le espressioni delle etichette di un layer: quella semplice, o
    quelle di tutte le regole."""
    out: List[str] = []
    try:
        lab = layer.labeling()
    except Exception:                               # noqa: BLE001
        return out
    if lab is None:
        return out
    try:
        if lab.type() == "rule-based":
            def visita(regola):
                try:
                    s = regola.settings()
                    if s is not None and s.fieldName:
                        out.append(str(s.fieldName))
                except Exception:                   # noqa: BLE001
                    pass
                for figlio in regola.children():
                    visita(figlio)
            visita(lab.rootRule())
        else:
            s = lab.settings()
            if s is not None and s.fieldName:
                out.append(str(s.fieldName))
    except Exception:                               # noqa: BLE001
        pass
    return out


def audit_project(project=None) -> Dict[str, Any]:
    """L'audit sul progetto QGIS aperto: layer vettoriali con etichette
    accese che scrivono aree, e annotazioni (nuove e vecchie) con ettari."""
    from qgis.core import QgsProject
    progetto = project or QgsProject.instance()
    strati: List[Tuple[str, bool, Optional[str], bool]] = []
    radice = progetto.layerTreeRoot()
    for layer in progetto.mapLayers().values():
        if not hasattr(layer, "labeling"):
            continue
        try:
            accese = bool(layer.labelsEnabled())
        except Exception:                           # noqa: BLE001
            accese = False
        try:
            nel_pannello = radice.findLayer(layer.id()) is not None
        except Exception:                           # noqa: BLE001
            nel_pannello = True
        for espressione in _expressions_of(layer):
            strati.append((layer.name(), accese, espressione, nel_pannello))
    testi: List[str] = []
    try:
        for item in progetto.mainAnnotationLayer().items().values():
            for metodo in ("text", "document"):
                f = getattr(item, metodo, None)
                if callable(f):
                    v = f()
                    testi.append(v.toPlainText() if hasattr(v, "toPlainText") else str(v))
                    break
    except Exception:                               # noqa: BLE001
        pass
    try:
        for ann in progetto.annotationManager().annotations():
            doc = getattr(ann, "document", None)
            if callable(doc):
                testi.append(doc().toPlainText())
    except Exception:                               # noqa: BLE001
        pass
    return hectare_label_sources(strati, testi)
