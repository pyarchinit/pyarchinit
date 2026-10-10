"""L'inserto panoramico della tavola: dove si è nel mondo.

Enzo, 2026-10-09: «l'overview, nel caso di uno scavo, come base map deve
avere un OpenStreetMap o satellite con il solo puntino della
localizzazione».

Ha ragione sul perché: l'inserto non serve a ripetere lo scavo — quello
c'è già, grande, accanto — ma a dire in che parte del mondo quello scavo
sta. Un inserto inquadrato sullo scavo non dice niente del tutto.

Qui c'è la parte che si decide senza QGIS e senza rete: quale delle
mappe del layout è l'inserto, quale sfondo usare, e quanto largo
inquadrare.
"""
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

#: Gli sfondi disponibili, come sorgenti XYZ. Si scaricano dalla rete:
#: senza, l'inserto resta col solo puntino su fondo bianco, che è meno
#: utile ma non è un errore.
BASE_MAPS = {
    "osm": {
        "nome": "OpenStreetMap",
        "url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        "zmin": 0, "zmax": 19,
    },
    "satellite": {
        "nome": "Satellite (Esri World Imagery)",
        "url": ("https://server.arcgisonline.com/ArcGIS/rest/services/"
                "World_Imagery/MapServer/tile/{z}/{y}/{x}"),
        "zmin": 0, "zmax": 19,
    },
}

#: Quello che si usa se nessuno dice altrimenti.
DEFAULT_BASE_MAP = "osm"

#: Mezza larghezza dell'inserto, in metri (Web Mercator). Un inserto da
#: cento metri non dice dove sei: dice solo che sei lì. Cento chilometri
#: per lato mostrano la regione e la costa, che è quello che serve.
OVERVIEW_HALF_WIDTH = 100_000.0


def overview_indexes(misure: Sequence[Tuple[float, float]],
                     principale: Optional[int]) -> List[int]:
    """Quali mappe del layout sono inserti: tutte tranne quella grande."""
    if not misure or principale is None:
        return []
    return [i for i in range(len(misure)) if i != principale]


#: I soli caratteri da codificare dentro il valore di ``url=``.
#:
#: Le graffe di ``{z}/{x}/{y}`` perché QGIS le codifica (e un uri con le
#: graffe nude non si rilegge); ``&`` ed ``=`` perché spezzerebbero l'uri
#: in due parametri quando l'indirizzo porta una chiave in coda. Schema e
#: barre **no**: codificare anche quelli era il baco.
_DA_CODIFICARE = {"{": "%7B", "}": "%7D", "&": "%26", "=": "%3D"}


def quote_tile_url(url: str) -> str:
    """L'indirizzo delle tessere come lo scrive QGIS dentro l'uri.

    ``quote(url, safe="")`` codificava tutto, ``:`` e ``/`` compresi, e
    QGIS decodificando una volta si ritrovava una stringa ancora
    codificata — non un indirizzo. Nel pannello del layer si leggeva
    ``url=https%3A%2F%2Ftile.openstreetmap.org%2F…`` e le statistiche di
    cache contavano **29 700 errori** con zero tessere trovate, mentre il
    layer che QGIS aggiunge da «XYZ Tiles» scrive
    ``url=https://tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png``
    (Enzo, 2026-10-10: le proprietà dei due layer a confronto).
    """
    testo = str(url or "")
    for carattere, codice in _DA_CODIFICARE.items():
        testo = testo.replace(carattere, codice)
    return testo


def base_map_uri(kind: str = DEFAULT_BASE_MAP) -> str:
    """La stringa di sorgente che QGIS vuole per un provider ``wms`` XYZ.

    Parola per parola quella che QGIS scrive di suo per una connessione
    XYZ, ``tilePixelRatio`` compreso: è l'unica che scarica le tessere.
    """
    scelta = BASE_MAPS.get(kind) or BASE_MAPS[DEFAULT_BASE_MAP]
    return ("tilePixelRatio=1&type=xyz&url=%s&zmax=%d&zmin=%d"
            % (quote_tile_url(scelta["url"]), scelta["zmax"], scelta["zmin"]))


def base_map_name(kind: str = DEFAULT_BASE_MAP) -> str:
    return (BASE_MAPS.get(kind) or BASE_MAPS[DEFAULT_BASE_MAP])["nome"]


def overview_window(punto, half_width: float = OVERVIEW_HALF_WIDTH):
    """Il rettangolo dell'inserto intorno al punto, o ``None``."""
    try:
        x, y = (float(v) for v in punto)
    except (TypeError, ValueError):
        return None
    mezzo = abs(float(half_width)) or OVERVIEW_HALF_WIDTH
    return (x - mezzo, y - mezzo, x + mezzo, y + mezzo)


#: Il gruppo dell'albero dei layer dove vive la roba dell'inserto, e il
#: tema mappa che l'inserto segue. Nomi fermi: si riusano fra una
#: generazione e l'altra, se no ogni export lascerebbe un gruppo in più.
GROUP_NAME = "pyArchInit — inserto atlante"
THEME_NAME = "pyArchInit inserto atlante"

#: Il nome del layer del puntino. Fermo come gli altri due, e per lo
#: stesso motivo: si riusa invece di moltiplicarsi.
PUNTO_NAME = "Localizzazione"


def theme_layers(sfondo, punto):
    """I layer che vanno nel tema dell'inserto, nell'ordine di disegno.

    «Una vista solo per osm senza layer dentro» (Enzo, 2026-10-10): nel
    tema non entra **nessun** layer del progetto — né le US né le quote.
    Il puntino sì: è il motivo per cui l'inserto esiste.

    Senza puntino non c'è inserto da fare, e la lista resta vuota. Senza
    sfondo (rete assente) resta il solo puntino, che dice meno ma non è
    un errore.
    """
    if punto is None:
        return []
    return ([sfondo, punto] if sfondo is not None else [punto])


def is_base_map(source: str, kind: str = DEFAULT_BASE_MAP) -> bool:
    """Vero se ``source`` è la sorgente dello sfondo di tipo ``kind``.

    Si riconosce dalla **sorgente**, non dal nome: chi usa il plugin può
    rinominare il layer nella TOC, e cercandolo per nome se ne
    aggiungerebbe uno nuovo a ogni export.
    """
    if not source:
        return False
    scelta = BASE_MAPS.get(kind) or BASE_MAPS[DEFAULT_BASE_MAP]
    from urllib.parse import quote, unquote

    testo = unquote(str(source))
    return scelta["url"] in testo or quote(scelta["url"], safe="") in str(source)
