"""Quali modelli di stampa sanno fare l'atlante del Time Manager.

Il generatore pretende, oltre a una mappa, due elementi che solo il
modello del Time Manager possiede: il titolo HTML e l'immagine della
matrice. Scegliendo un altro `.qpt` — e il selettore li elenca tutti,
compresi i venticinque modelli adArte/pyarchinit — il generatore trovava
``None``, stampava una riga sulla console e tornava indietro in silenzio:
nessun messaggio, nessuna tavola, la barra di avanzamento lasciata
aperta. «A volte parte, a volte no» (Enzo, 2026-10-09): dipendeva da
quale modello si sceglieva.

Qui si riconosce che cosa un modello sa fare, leggendo il file. Senza
Qt: la finestra di scelta deve poterlo dire prima di caricare qualcosa.
"""
from __future__ import annotations

import re
from typing import Dict

#: Il tipo di ``QgsLayoutItemMap`` nel file di un modello.
MAP_TYPE = "65639"

#: L'id del telaio HTML che porta il titolo «Tavola N».
TITLE_ID = "123"

#: L'id dell'immagine in cui finisce la matrice.
MATRIX_ID = "matrix"

_MAPPA = re.compile(r'<LayoutItem\b[^>]*type="%s"' % MAP_TYPE)


def capabilities(xml: str) -> Dict[str, bool]:
    """Che cosa il modello sa fare: ``{"map":…, "title":…, "matrix":…}``.

    Si legge il testo e non si carica il layout: la finestra di scelta
    deve poter marcare venticinque file senza aprirne nessuno.
    """
    testo = xml or ""
    return {
        "map": bool(_MAPPA.search(testo)),
        "title": ('id="%s"' % TITLE_ID) in testo,
        "matrix": ('id="%s"' % MATRIX_ID) in testo,
    }


def is_usable(caps: Dict[str, bool]) -> bool:
    """Vero se con questo modello una tavola si può fare.

    Serve la mappa, e basta: senza il titolo o senza l'immagine della
    matrice le tavole escono lo stesso, solo più spoglie. Quello che
    manca si salta — abortire tutta la generazione perché manca una
    casella di testo è la ragione per cui i layout restavano vuoti.
    """
    return bool((caps or {}).get("map"))


def describe_missing(caps: Dict[str, bool], lang: str = "it") -> str:
    """La frase da mostrare, o stringa vuota se non manca niente."""
    caps = caps or {}
    if lang.startswith("en"):
        nomi = {"map": "a map", "title": "the «Tavola N» title",
                "matrix": "the matrix picture"}
        senza_mappa = ("This template has no map: no sheet can be drawn "
                       "from it.")
        parziale = "This template has no %s: that part will be left out."
    else:
        nomi = {"map": "una mappa", "title": "il titolo «Tavola N»",
                "matrix": "l'immagine della matrice"}
        senza_mappa = ("Questo modello non ha una mappa: non ci si può "
                       "disegnare nessuna tavola.")
        parziale = "Questo modello non ha %s: quella parte resterà fuori."
    if not caps.get("map"):
        return senza_mappa
    mancanti = [nomi[k] for k in ("title", "matrix") if not caps.get(k)]
    if not mancanti:
        return ""
    return parziale % (" né ".join(mancanti) if lang == "it"
                       else " nor ".join(mancanti))


#: Il suffisso dei modelli preparati per l'atlante del Time Manager.
PREPARED_SUFFIX = " + Time Manager"


def what_to_add(caps: Dict[str, bool]):
    """Che cosa manca a questo modello, nell'ordine in cui si aggiunge.

    Vuoto se non manca niente, e vuoto anche se manca la **mappa**: in
    quel caso non è un modello da atlante, e aggiungerci la matrice non
    lo renderebbe utile.
    """
    caps = caps or {}
    if not caps.get("map"):
        return []
    return [k for k in ("title", "matrix") if not caps.get(k)]


def prepared_name(path):
    """Il nome del modello preparato, accanto all'originale.

    Un file nuovo, mai una sovrascrittura: i modelli sono di chi usa il
    plugin, e li ha scelti lui.
    """
    from pathlib import Path

    percorso = Path(path)
    gambo = percorso.stem
    if gambo.endswith(PREPARED_SUFFIX):
        return percorso
    return percorso.with_name(gambo + PREPARED_SUFFIX + percorso.suffix)


def add_items(layout, mancanti):
    """Aggiunge al layout gli elementi che l'atlante cerca.

    Su una **pagina nuova**, mai sopra quella esistente: in un modello
    che non si conosce si finirebbe per coprire la legenda o il
    cartiglio, e una matrice di Harris schiacciata in un angolo non si
    legge. La pagina ha la stessa misura delle altre.
    """
    from qgis.core import (QgsLayoutFrame, QgsLayoutItemHtml,
                           QgsLayoutItemPage, QgsLayoutItemPicture,
                           QgsLayoutPoint, QgsLayoutSize, QgsUnitTypes)
    from qgis.PyQt.QtCore import QRectF

    if not mancanti:
        return 0
    raccolta = layout.pageCollection()
    modello_pagina = raccolta.page(0)
    pagina = QgsLayoutItemPage(layout)
    if modello_pagina is not None:
        pagina.setPageSize(modello_pagina.pageSize())
    raccolta.addPage(pagina)
    indice = raccolta.pageCount() - 1
    misura = pagina.pageSize()
    larghezza, altezza = misura.width(), misura.height()
    unita = misura.units()
    margine = min(larghezza, altezza) * 0.05
    alto_titolo = max(altezza * 0.07, 10.0)
    cima = raccolta.page(indice).pos().y() if hasattr(
        raccolta.page(indice), "pos") else 0.0

    aggiunti = 0
    if "title" in mancanti:
        html = QgsLayoutItemHtml(layout)
        layout.addMultiFrame(html)
        telaio = QgsLayoutFrame(layout, html)
        html.addFrame(telaio)
        telaio.setId(TITLE_ID)
        telaio.attemptSetSceneRect(QRectF(
            margine, cima + margine, larghezza - 2 * margine, alto_titolo))
        aggiunti += 1
    if "matrix" in mancanti:
        immagine = QgsLayoutItemPicture(layout)
        layout.addLayoutItem(immagine)
        immagine.setId(MATRIX_ID)
        immagine.setFrameEnabled(True)
        # Il riquadro si stringe sul disegno invece di restare mezzo
        # vuoto: una matrice è alta e stretta, la pagina è larga.
        try:
            immagine.setResizeMode(
                QgsLayoutItemPicture.ResizeMode.ZoomResizeFrame)
        except Exception:                           # noqa: BLE001
            try:
                immagine.setResizeMode(
                    QgsLayoutItemPicture.ZoomResizeFrame)
            except Exception:                       # noqa: BLE001
                pass
        y = cima + margine + alto_titolo + margine * 0.5
        immagine.attemptSetSceneRect(QRectF(
            margine, y, larghezza - 2 * margine,
            altezza - (y - cima) - margine))
        aggiunti += 1
    return aggiunti


def qgis_is_running() -> bool:
    """Vero se c'è una ``QgsApplication`` viva.

    Costruire un ``QgsPrintLayout`` senza di lei non dà un'eccezione: dà
    un **segmentation fault**, e si porta via tutto il processo. Scoperto
    perché la preparazione all'avvio gira anche da
    ``install_dir()``, che i test chiamano senza QGIS (2026-10-09).
    """
    try:
        from qgis.core import QgsApplication
        return QgsApplication.instance() is not None
    except Exception:                               # noqa: BLE001
        return False


def prepare_file(path, out_dir=None):
    """Scrive accanto all'originale un modello adatto all'atlante.

    Restituisce il percorso scritto, o ``None`` se non c'era niente da
    aggiungere (o se il modello non ha una mappa, o se QGIS non è vivo).
    """
    from pathlib import Path

    if not qgis_is_running():
        return None

    from qgis.core import (QgsPrintLayout, QgsProject, QgsReadWriteContext)
    from qgis.PyQt.QtXml import QDomDocument

    percorso = Path(path)
    testo = percorso.read_text(encoding="utf-8", errors="replace")
    mancanti = what_to_add(capabilities(testo))
    if not mancanti:
        return None

    layout = QgsPrintLayout(QgsProject.instance())
    layout.initializeDefaults()
    doc = QDomDocument()
    doc.setContent(testo)
    layout.readXml(doc.documentElement(), doc, QgsReadWriteContext())
    if not add_items(layout, mancanti):
        return None

    destinazione = prepared_name(percorso)
    if out_dir is not None:
        destinazione = Path(out_dir) / destinazione.name
    if not layout.saveAsTemplate(str(destinazione), QgsReadWriteContext()):
        return None
    return str(destinazione)


def to_prepare(folder):
    """I modelli della cartella che non hanno ancora la copia preparata.

    Si guardano i nomi, non il contenuto: deve costare poco, perché gira
    a ogni avvio. I template escono da ``profile.zip``, che si riestrae
    quando la cartella manca — e allora le copie preparate se ne vanno
    con lei. Così si rifanno da sole, ma solo quelle che mancano.
    """
    from pathlib import Path

    cartella = Path(folder)
    if not cartella.is_dir():
        return []
    da_fare = []
    for percorso in sorted(cartella.glob("*.qpt")):
        if PREPARED_SUFFIX in percorso.stem:
            continue
        if prepared_name(percorso).exists():
            continue
        # Leggere il testo costa poco, caricare un layout no: un modello
        # già completo (o senza mappa) si scarta qui, se no a ogni avvio
        # lo si aprirebbe per scoprire che non c'è niente da fare.
        try:
            testo = percorso.read_text(encoding="utf-8", errors="replace")
        except Exception:                           # noqa: BLE001
            continue
        if not what_to_add(capabilities(testo)):
            continue
        da_fare.append(percorso)
    return da_fare


def ensure_prepared(folder, limit=None):
    """Prepara i modelli che ne hanno bisogno. Restituisce quanti ne ha fatti.

    Mai un'eccezione verso il chiamante: è roba che gira all'avvio del
    plugin, e un modello storto non deve impedire a pyArchInit di
    partire.
    """
    if not qgis_is_running():
        return 0
    fatti = 0
    for percorso in to_prepare(folder):
        if limit is not None and fatti >= limit:
            break
        try:
            if prepare_file(percorso):
                fatti += 1
        except Exception:                           # noqa: BLE001
            continue
    return fatti
