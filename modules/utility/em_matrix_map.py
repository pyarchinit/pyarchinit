"""Dalla matrice alla mappa: lo zoom sulla geometria dell'unità.

Richiesta di Enzo del 2026-10-08: cliccando una US nel pannello si deve
poter andare a vedere dove sta, se la pianta è disegnata. Qui c'è solo il
pezzo che parla con QGIS — leggere i layer, selezionare, inquadrare. Chi
decide quale layer vince e quanto larga è l'inquadratura sta in
``em_matrix_links``, che si prova senza avviare QGIS.

Si **legge** il progetto e non lo si cambia: nessun layer aggiunto,
nessun gruppo, nessuna modifica aperta. Zoomare non è modificare, e un
pannello che riordina il progetto di chi lo apre è un pannello che non si
riapre più.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

#: Quanta aria intorno alla geometria, in frazione della sua dimensione.
MARGIN = 0.15

#: Di quanto si allarga dove la geometria è piatta — una quota è un punto,
#: un muro può essere una linea — nelle unità di misura del layer.
MINIMUM_SPAN = 5.0


def project_layers() -> List:
    """I layer vettoriali con geometria, nell'ordine della legenda.

    Dall'albero e non da ``mapLayers()``, che è un dizionario: fra due
    layer che sanno rispondere si prova prima quello che l'utente vede in
    cima, non quello che capita.
    """
    try:
        from qgis.core import QgsProject
        nodi = QgsProject.instance().layerTreeRoot().findLayers()
    except Exception:                               # noqa: BLE001
        return []
    layers = []
    for nodo in nodi:
        try:
            layer = nodo.layer()
        except Exception:                           # noqa: BLE001
            continue
        if layer is None:
            continue
        if not (hasattr(layer, "getFeatures") and hasattr(layer, "fields")):
            continue                                # un raster non ha campi
        try:
            if hasattr(layer, "isSpatial") and not layer.isSpatial():
                continue
        except Exception:                           # noqa: BLE001
            pass
        layers.append(layer)
    return layers


def _field_names(layer) -> List[str]:
    try:
        return [campo.name() for campo in layer.fields()]
    except Exception:                               # noqa: BLE001
        return []


def _box_of(geometria) -> Optional[tuple]:
    """Il rettangolo della geometria, o ``None`` se non c'è geometria.

    Una riga che esiste nel layer ma senza pianta disegnata non è un
    disegno: dirlo è la differenza fra «non l'hai disegnata» e «non l'ho
    trovata».
    """
    if geometria is None:
        return None
    try:
        if geometria.isNull() or geometria.isEmpty():
            return None
        riquadro = geometria.boundingBox()
        return (riquadro.xMinimum(), riquadro.yMinimum(),
                riquadro.xMaximum(), riquadro.yMaximum())
    except Exception:                               # noqa: BLE001
        return None


def _found_in(layer, espressione: str):
    """``[(id, rettangolo)]`` delle feature del layer che corrispondono."""
    from qgis.core import QgsFeatureRequest

    richiesta = QgsFeatureRequest().setFilterExpression(espressione)
    trovate = []
    for feature in layer.getFeatures(richiesta):
        trovate.append((feature.id(), _box_of(feature.geometry())))
    return trovate


def _rectangle(layer, canvas, box) -> "object":
    """Il rettangolo nel sistema di riferimento della mappa.

    Senza la riproiezione un layer in un sistema diverso da quello del
    progetto manderebbe la vista in mezzo all'oceano.
    """
    from qgis.core import QgsRectangle

    rettangolo = QgsRectangle(box[0], box[1], box[2], box[3])
    try:
        from qgis.core import QgsCoordinateTransform, QgsProject
        sorgente = layer.crs()
        destinazione = canvas.mapSettings().destinationCrs()
        if (sorgente.isValid() and destinazione.isValid()
                and sorgente != destinazione):
            rettangolo = QgsCoordinateTransform(
                sorgente, destinazione,
                QgsProject.instance()).transformBoundingBox(rettangolo)
    except Exception:                               # noqa: BLE001
        pass
    return rettangolo


def zoom_to_unit(iface, unit, connection=None, *, layers=None,
                 margin: float = MARGIN) -> Tuple[bool, str]:
    """Inquadra la geometria dell'unità. ``(fatto, frase per l'utente)``.

    ``connection`` serve solo a risolvere ``id_us``, che è la chiave più
    precisa quando il layer è la vista US; senza, si cerca per sito, area,
    us e tipo.
    """
    from .em_matrix_links import (candidate_layers, find_unit_extent,
                                  padded_box, resolve_id_us, unit_identity)

    etichetta = str(getattr(unit, "label", "") or "questo nodo")
    if not unit_identity(unit):
        return False, ("«%s» non è una riga della scheda US: sulla mappa non "
                       "c'è una geometria da cercare." % etichetta)

    disponibili = list(layers) if layers is not None else project_layers()
    descrittori = [(layer, _field_names(layer)) for layer in disponibili]
    id_us = resolve_id_us(connection, unit) if connection is not None else None

    if not candidate_layers(unit, descrittori, id_us=id_us):
        return False, ("Nessuno dei layer caricati porta i campi per "
                       "riconoscere «%s»: carica la vista US e riprova."
                       % etichetta)

    esito = find_unit_extent(unit, descrittori, id_us=id_us, fetch=_found_in)
    if esito is None:
        return False, ("«%s» non risulta disegnata in nessuno dei layer "
                       "caricati." % etichetta)

    layer, ids, riquadro = esito
    try:
        layer.selectByIds(ids)
    except Exception:                               # noqa: BLE001
        pass
    canvas = iface.mapCanvas()
    canvas.setExtent(_rectangle(
        layer, canvas, padded_box(riquadro, margin=margin,
                                  minimum=MINIMUM_SPAN)))
    canvas.refresh()
    try:
        canvas.flashFeatureIds(layer, ids)
    except Exception:                               # noqa: BLE001
        pass
    nome = ""
    try:
        nome = str(layer.name())
    except Exception:                               # noqa: BLE001
        pass
    return True, ("Zoom su «%s» in «%s» (%d %s)."
                  % (etichetta, nome, len(ids),
                     "geometria" if len(ids) == 1 else "geometrie"))


# ---------------------------------------------------------------------------
# Più unità insieme: le geometrie di cui parla un capitolo della narrativa
# ---------------------------------------------------------------------------

_MSG = {
    "none": {"it": "Nessuna delle unità citate è una riga della scheda US: sulla "
                   "mappa non c'è niente da cercare.",
             "en": "None of the cited units is a US record: nothing to look for "
                   "on the map."},
    "no_layers": {"it": "Nessuno dei layer caricati porta i campi per riconoscere le "
                        "unità: carica la vista US e riprova.",
                  "en": "None of the loaded layers has the fields to recognise the "
                        "units: load the US view and try again."},
    "nothing": {"it": "Nessuna delle {total} unità risulta disegnata nei layer "
                      "caricati: {names}.",
                "en": "None of the {total} units is drawn in the loaded layers: "
                      "{names}."},
    "nothing_one": {"it": "L'unità {names} non risulta disegnata nei layer caricati.",
                    "en": "Unit {names} is not drawn in the loaded layers."},
    "done": {"it": "Evidenziate {n} unità su {total} in «{layer}» ({k} {geom}).",
             "en": "Highlighted {n} of {total} units in “{layer}” ({k} {geom})."},
    "done_one": {"it": "Evidenziata l'unità {names} in «{layer}» ({k} {geom}).",
                 "en": "Highlighted unit {names} in “{layer}” ({k} {geom})."},
    "geom_one": {"it": "geometria", "en": "geometry"},
    "geom_many": {"it": "geometrie", "en": "geometries"},
    "missing": {"it": "Non disegnate: {names}.", "en": "Not drawn: {names}."},
}


def _m(key: str, lang: str, **kw) -> str:
    voce = _MSG[key]
    return voce.get((lang or "it")[:2], voce["en"]).format(**kw)


def _names(etichette, massimo: int = 5) -> str:
    testo = ", ".join(etichette[:massimo])
    if len(etichette) > massimo:
        testo += ", … (%d)" % len(etichette)
    return testo


def zoom_to_units(iface, units, connection=None, *, layers=None,
                  margin: float = MARGIN, lang: str = "it") -> Tuple[int, str]:
    """Seleziona e inquadra insieme le geometrie di più unità (quelle di cui
    parla un capitolo della narrativa). ``(quante trovate, frase)``.

    Una selezione sola per layer, con tutte le feature; l'inquadratura
    abbraccia tutto; le unità non disegnate si dicono per nome. Un nodo che
    non è una riga della scheda non si cerca.
    """
    from .em_matrix_links import (candidate_layers, find_unit_extent,
                                  merge_boxes, padded_box, resolve_id_us,
                                  unit_identity)

    validi = [u for u in units if unit_identity(u)]
    if not validi:
        return 0, _m("none", lang)
    disponibili = list(layers) if layers is not None else project_layers()
    descrittori = [(layer, _field_names(layer)) for layer in disponibili]

    per_layer: dict = {}
    mancanti: List[str] = []
    qualche_layer = False
    for unit in validi:
        etichetta = str(getattr(unit, "label", "") or unit.node_id)
        id_us = resolve_id_us(connection, unit) if connection is not None else None
        if not candidate_layers(unit, descrittori, id_us=id_us):
            mancanti.append(etichetta)
            continue
        qualche_layer = True
        esito = find_unit_extent(unit, descrittori, id_us=id_us, fetch=_found_in)
        if esito is None:
            mancanti.append(etichetta)
            continue
        layer, ids, riquadro = esito
        voce = per_layer.setdefault(id(layer), [layer, [], []])
        voce[1].extend(i for i in ids if i not in voce[1])
        voce[2].append(riquadro)

    trovate = len(validi) - len(mancanti)
    if not per_layer:
        if not qualche_layer:
            return 0, _m("no_layers", lang)
        if len(validi) == 1:
            return 0, _m("nothing_one", lang, names=_names(mancanti))
        return 0, _m("nothing", lang, total=len(validi), names=_names(mancanti))

    canvas = iface.mapCanvas()
    rettangolo = None
    for layer, ids, riquadri in per_layer.values():
        try:
            layer.selectByIds(ids)
        except Exception:                           # noqa: BLE001
            pass
        pezzo = _rectangle(layer, canvas, padded_box(
            merge_boxes(riquadri), margin=margin, minimum=MINIMUM_SPAN))
        if rettangolo is None:
            rettangolo = pezzo
        else:
            rettangolo.combineExtentWith(pezzo)
    canvas.setExtent(rettangolo)
    canvas.refresh()
    for layer, ids, _riquadri in per_layer.values():
        try:
            canvas.flashFeatureIds(layer, ids)
        except Exception:                           # noqa: BLE001
            pass

    primo = next(iter(per_layer.values()))
    nome = ""
    try:
        nome = str(primo[0].name())
    except Exception:                               # noqa: BLE001
        pass
    quante_geom = sum(len(v[1]) for v in per_layer.values())
    geom = _m("geom_one" if quante_geom == 1 else "geom_many", lang)
    if len(validi) == 1:
        frase = _m("done_one", lang, names=str(getattr(validi[0], "label", "") or validi[0].node_id),
                   layer=nome, k=quante_geom, geom=geom)
    else:
        frase = _m("done", lang, n=trovate, total=len(validi), layer=nome, k=quante_geom,
                   geom=geom)
    if mancanti:
        frase += " " + _m("missing", lang, names=_names(mancanti))
    return trovate, frase
