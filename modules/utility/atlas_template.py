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
