"""Come si legge una voce del campo ``rapporti``.

Il campo è testo: una lista di liste scritta dalla scheda US. Nello stesso
database convivono due formati, perché il quarto e il terzo posto sono
arrivati dopo:

``[tipo, us, area, sito]``
    il formato lungo di oggi;
``[tipo, us]``
    il formato corto delle schede più vecchie — nel database di esempio
    sono **tutte le 1870 voci**. Significa «stessa area di chi la cita».

Chi legge deve reggere entrambi. Fino al 2026-10-08 l'esportatore della
matrice prendeva ``voce[2]`` senza guardare e moriva con «list index out
of range» su qualunque sito scritto col formato corto (segnalato da Enzo).

Da non confondere con ``rapporti2``, che è un'altra lista con un'altra
forma: ``[tipo, us, unita_tipo, descrizione, periodizzazione, area, sito]``
(e la sua variante corta a 5 posti, senza area e sito).
"""
from __future__ import annotations

from typing import Optional, Tuple


def rapporto_target(entry, default_area) -> Optional[Tuple[str, str, str]]:
    """``(tipo, us, area)`` della voce, o ``None`` se non è una relazione.

    ``None`` quando la voce non è una lista, è più corta di due posti, o
    non nomina l'unità collegata: una riga vuota lasciata nella tabella
    della scheda non è un rapporto. L'area è quella dichiarata dalla
    voce; se manca o è vuota, è ``default_area`` — l'area di chi cita.
    """
    if not isinstance(entry, (list, tuple)) or len(entry) < 2:
        return None
    us = entry[1]
    if us is None or str(us).strip() == "":
        return None
    area = ""
    if len(entry) > 2 and entry[2] is not None:
        area = str(entry[2]).strip()
    return str(entry[0]), str(us), area or str(default_area)


def rapporto2_target(entry, default_area):
    """``(tipo, us, unita_tipo, descrizione, periodizzazione, area)``, o None.

    ``rapporti2`` è la lista ricca: sette posti oggi, cinque nelle schede
    più vecchie (senza area e sito). Sotto i cinque la voce non dice
    abbastanza per nominare un nodo della matrice e si salta.
    """
    if not isinstance(entry, (list, tuple)) or len(entry) < 5:
        return None
    us = entry[1]
    if us is None or str(us).strip() == "":
        return None
    area = ""
    if len(entry) > 5 and entry[5] is not None:
        area = str(entry[5]).strip()
    return (str(entry[0]), str(us), str(entry[2]), str(entry[3]),
            str(entry[4]), area or str(default_area))
