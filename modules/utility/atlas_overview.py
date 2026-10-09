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


def base_map_uri(kind: str = DEFAULT_BASE_MAP) -> str:
    """La stringa di sorgente che QGIS vuole per un provider ``wms`` XYZ.

    L'URL va codificato: le graffe di ``{z}/{x}/{y}`` e gli ``&`` dentro
    l'indirizzo spezzerebbero l'uri.
    """
    from urllib.parse import quote

    scelta = BASE_MAPS.get(kind) or BASE_MAPS[DEFAULT_BASE_MAP]
    return ("type=xyz&url=%s&zmax=%d&zmin=%d"
            % (quote(scelta["url"], safe=""), scelta["zmax"], scelta["zmin"]))


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
