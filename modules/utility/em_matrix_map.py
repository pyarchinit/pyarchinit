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
