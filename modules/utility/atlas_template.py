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
    # L'inserto e' «una mappa che non e' la grande»: e' la stessa regola
    # che usa il generatore (``atlas_overview.overview_indexes``), quindi
    # qui basta contarle. Con una sola mappa l'inserto non c'e', e il
    # localizzatore non si disegna da nessuna parte.
    return {
        "map": bool(_MAPPA.search(testo)),
        "title": ('id="%s"' % TITLE_ID) in testo,
        "matrix": ('id="%s"' % MATRIX_ID) in testo,
        "overview": len(_MAPPA.findall(testo)) >= 2,
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
    return [k for k in ("title", "matrix", "overview")
            if not caps.get(k)]


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


#: Quanto e' grande l'inserto, in frazione del lato corto della mappa
#: grande, e quanto sta staccato dal suo bordo (mm). Un localizzatore si
#: guarda, non si legge: piu' grande di cosi' ruba spazio al disegno.
INSET_FRACTION = 0.20
INSET_MARGIN_MM = 3.0
INSET_MIN_MM = 18.0
#: E un tetto, perche' la frazione da sola non scala: su un A0 il lato
#: corto della mappa e' quasi un metro, e il 20% sarebbe un localizzatore
#: da venti centimetri. Misurato: A4 -> 37 mm, A0 -> 45 mm.
INSET_MAX_MM = 45.0


def inset_rect(main_rect):
    """Dove mettere l'inserto dentro la mappa grande, o ``None``.

    ``main_rect`` e ``(x, y, larghezza, altezza)`` in mm. Il titolo e la
    matrice vanno su una pagina nuova per non coprire il cartiglio;
    l'inserto no — un localizzatore su un'altra pagina non localizza
    niente. Sta **dentro** il rettangolo della mappa, in basso a destra,
    dove sta per convenzione: li' non puo' coprire ne' la legenda ne' il
    cartiglio, perche' non esce dalla mappa.

    ``None`` se non ci sta: su una mappa da francobollo un inserto
    coprirebbe il disegno invece di aiutarlo.
    """
    try:
        x, y, w, h = (float(v) for v in main_rect)
    except (TypeError, ValueError):
        return None
    if w <= 0 or h <= 0:
        return None
    lato = min(INSET_MAX_MM,
               max(INSET_MIN_MM, min(w, h) * INSET_FRACTION))
    if lato + 2 * INSET_MARGIN_MM > min(w, h):
        return None
    return (x + w - INSET_MARGIN_MM - lato,
            y + h - INSET_MARGIN_MM - lato, lato, lato)


def _main_map(layout):
    """La mappa piu' grande del layout, che e' quella del disegno."""
    from qgis.core import QgsLayoutItemMap

    mappe = [i for i in layout.items() if isinstance(i, QgsLayoutItemMap)]
    if not mappe:
        return None
    return max(mappe, key=lambda m: (m.sizeWithUnits().width()
                                     * m.sizeWithUnits().height()))


def _add_overview(layout):
    """Aggiunge l'inserto dentro la mappa grande. 1 se l'ha messo, 0 se no."""
    from qgis.core import (QgsLayoutItemMap, QgsLayoutPoint, QgsLayoutSize,
                           QgsUnitTypes)
    from qgis.PyQt.QtGui import QColor

    grande = _main_map(layout)
    if grande is None:
        return 0
    pos = grande.pagePositionWithUnits()
    mis = grande.sizeWithUnits()
    dove = inset_rect((pos.x(), pos.y(), mis.width(), mis.height()))
    if dove is None:
        return 0
    x, y, w, h = dove
    inserto = QgsLayoutItemMap(layout)
    inserto.attemptMove(QgsLayoutPoint(
        x, y, QgsUnitTypes.LayoutUnit.LayoutMillimeters),
        page=grande.page())
    inserto.attemptResize(QgsLayoutSize(
        w, h, QgsUnitTypes.LayoutUnit.LayoutMillimeters))
    # Una cornice e un fondo bianco: senza, su un disegno chiaro
    # l'inserto non si distingue da quello che gli sta sotto.
    inserto.setFrameEnabled(True)
    inserto.setFrameStrokeColor(QColor(60, 60, 60))
    inserto.setBackgroundEnabled(True)
    inserto.setBackgroundColor(QColor(255, 255, 255))
    inserto.setId("overview")
    inserto.setZValue(grande.zValue() + 1)
    layout.addLayoutItem(inserto)
    return 1


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
    aggiunti = 0
    if "overview" in mancanti:
        aggiunti += _add_overview(layout)
    # Il titolo e la matrice vanno su una pagina nuova; l'inserto no. Se
    # manca solo lui, qui non si crea niente: una pagina bianca in piu'
    # sarebbe un peggioramento.
    sulla_pagina_nuova = [k for k in ("title", "matrix") if k in mancanti]
    if not sulla_pagina_nuova:
        return aggiunti
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
    """I modelli della cartella la cui copia preparata manca o è stantia.

    I template escono da ``profile.zip``, che si riestrae quando la
    cartella manca — e allora le copie preparate se ne vanno con lei.
    Così si rifanno da sole, ma solo quelle che servono.

    **Stantia** vuol dire preparata da una versione che aggiungeva meno
    cose: le copie del 2026-10-09 non hanno l'inserto panoramico, e una
    tavola senza inserto non mostra dove si è nel mondo. Una copia
    ``+ Time Manager`` è nostra, non di chi usa il plugin, quindi si
    rifà; l'originale non si tocca mai.

    Si leggono i testi, non si caricano i layout: sono ventitré file da
    poche decine di kB e gira a ogni avvio.
    """
    from pathlib import Path

    cartella = Path(folder)
    if not cartella.is_dir():
        return []
    da_fare = []
    for percorso in sorted(cartella.glob("*.qpt")):
        if PREPARED_SUFFIX in percorso.stem:
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
        preparata = prepared_name(percorso)
        if preparata.exists():
            # C'è già: si rifà solo se le manca qualcosa che oggi
            # sappiamo aggiungere.
            try:
                fatta = preparata.read_text(encoding="utf-8",
                                            errors="replace")
            except Exception:                       # noqa: BLE001
                continue
            if not what_to_add(capabilities(fatta)):
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
