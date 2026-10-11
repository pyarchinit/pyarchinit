"""Come si legge una voce del campo ``rapporti``.

Il campo è testo: una lista di liste scritta dalla scheda US. Nello stesso
database convivono due formati, perché il quarto e il terzo posto sono
arrivati dopo:

``[tipo, us, area, sito]``
    il formato lungo, quello che la scheda scrive oggi;
``[tipo, us]``
    il formato corto delle schede più vecchie. Significa «stessa area di
    chi la cita».

I due convivono nello stesso database, anche nello stesso momento: nel
DB di esempio che spediamo sono corte tutte e 1870 le voci, mentre in un
database aggiornato dalla scheda di oggi il sito su cui si lavora le ha
lunghe e gli altri siti no (misurato il 2026-10-08 sul DB di Enzo: 187
lunghe sul sito italiano, 1683 corte sugli altri nove).

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


# ---------------------------------------------------------------------------
# Completare le colonne `area` e `sito`
#
# Il bottone «Aggiorna Area/Sito nei rapporti» (Ctrl+U) della scheda US
# riempie le due colonne che la forma corta non ha. Fino all'11 ottobre 2026
# le riempiva male su uno scavo a più aree, e il guasto era doppio:
#
# * la forma corta prendeva l'area **della scheda**, anche quando l'unità
#   collegata in quell'area non esiste;
# * l'area veniva poi cercata con `WHERE us = ? AND sito = ?` prendendo la
#   **prima** riga, e riscritta **anche dove era già giusta**: sul DB di
#   prova, dove US 1 e US 9 esistono in area 1 e in area 2, le relazioni
#   della scheda dell'area 2 diventavano relazioni dell'area 1.
#
# La regola: l'identità di una scheda è `UniqueConstraint('sito', 'area',
# 'us', 'unita_tipo')`, quindi un rapporto che non dice l'area non nomina
# una riga, e un rapporto che la dice **la nomina**: se quella riga esiste,
# non la si corregge. Il resto si decide così — l'area della scheda quando
# l'unità collegata esiste lì (la convenzione del formato corto: la
# stratigrafia si osserva dentro un'area), altrimenti l'unica area in cui
# esiste, altrimenti niente. Un'area inventata collega la scheda all'unità
# sbagliata; una colonna vuota si vede e si corregge a mano.
# ---------------------------------------------------------------------------

#: Perché l'area è quella: l'unità collegata esiste nell'area della scheda.
STESSA_AREA = "stessa_area"
#: Perché l'area è quella: l'unità collegata esiste in una sola area.
UNICA = "unica"
#: Non si decide: il numero esiste in più aree e nessuna è quella della
#: scheda. Si lascia la colonna com'è e si segnala.
AMBIGUA = "ambigua"
#: Non si decide: quel numero non esiste in nessuna area del sito.
INESISTENTE = "inesistente"


def _t(valore) -> str:
    """Il valore come testo strisciato; ``None`` è stringa vuota.

    ``area`` è testo battuto a mano in una scheda: ``'1 '`` è l'area 1, e
    confrontarla senza strisciare fa aggiornare zero righe (è il guasto che
    `rapporti_check._key_clause` documenta per le correzioni cronologiche).
    """
    return "" if valore is None else str(valore).strip()


def indice_aree(righe) -> dict:
    """``{numero di US: set(aree)}`` da una lista di coppie ``(us, area)``.

    Una query per sito invece di una per rapporto: chi cercava l'area una
    riga per volta rifletteva la tabella — 119 colonne — a ogni relazione.
    """
    indice = {}
    for us, area in righe:
        indice.setdefault(_t(us), set()).add(_t(area))
    return indice


def risolvi_area(us, area_scheda, aree):
    """``(area, motivo)`` per un rapporto che nomina ``us``.

    ``aree`` sono le aree in cui quel numero esiste nel sito. L'area è
    ``None`` quando non si può decidere, e il motivo dice perché: vedi
    :data:`STESSA_AREA`, :data:`UNICA`, :data:`AMBIGUA`, :data:`INESISTENTE`.
    """
    disponibili = {_t(a) for a in (aree or ())}
    disponibili.discard("")
    if not disponibili:
        return None, INESISTENTE
    mia = _t(area_scheda)
    if mia and mia in disponibili:
        return mia, STESSA_AREA
    if len(disponibili) == 1:
        return next(iter(disponibili)), UNICA
    return None, AMBIGUA


def completa_rapporti(rapporti, *, area_scheda, sito, aree_per_us,
                      pos_area=2, pos_sito=3):
    """Riempie ``area`` e ``sito`` in una lista di rapporti.

    ``rapporti`` è la lista già letta dal campo; ``aree_per_us`` è
    l'indice di :func:`indice_aree`. ``pos_area``/``pos_sito`` sono 2 e 3
    per ``rapporti``, 5 e 6 per ``rapporti2``.

    Ritorna ``(lista, irrisolti)``: la lista nuova — le voci che non
    nominano nessuna unità sono buttate, e quello che sta oltre la colonna
    del sito non si tiene, come ha sempre fatto la scheda — e la lista
    delle ``(us, motivo, area_dichiarata)`` che non si sono potute
    decidere, da far vedere a chi ha premuto il bottone.
    """
    fuori, irrisolti = [], []
    for voce in rapporti or ():
        if not isinstance(voce, (list, tuple)) or len(voce) < 2:
            continue
        nuova = [_t(x) for x in voce[:pos_sito + 1]]
        while len(nuova) <= pos_sito:
            nuova.append("")
        us = nuova[1]
        if not us:
            # Una riga cominciata e non finita — «Copre» e il numero
            # ancora da battere — si tiene: la scheda la conserva
            # (`table2dict(preserve_empty=True)`), e un bottone che
            # riempie due colonne non è il posto dove cancellarla.
            nuova[pos_sito] = _t(sito)
            fuori.append(nuova)
            continue
        aree = aree_per_us.get(us, set())
        dichiarata = nuova[pos_area]
        if not (dichiarata and dichiarata in {_t(a) for a in aree}):
            area, motivo = risolvi_area(us, area_scheda, aree)
            if area is None:
                irrisolti.append((us, motivo, dichiarata))
            else:
                nuova[pos_area] = area
        nuova[pos_sito] = _t(sito)
        fuori.append(nuova)
    return fuori, irrisolti


# ---------------------------------------------------------------------------
# La riga del rapporto reciproco mancante
#
# `US_USM.rapporti_stratigrafici_check` la scrive in tre lingue, e il
# correttore la rilegge. Il vecchio lettore era una manciata di espressioni
# regolari che pretendevano `\d+` per le aree (uno scavo a saggi — «Saggio
# I» — ripiegava sull'area 1), cercavano `Site:` anche in italiano, e
# conoscevano solo SU/US/USM/WSU: sulla riga tedesca, che dice `SE:`,
# alzavano ValueError e la correzione non partiva.
# ---------------------------------------------------------------------------

_RIGA_RECIPROCO = None


def leggi_riga_reciproco(riga):
    """I sei pezzi della riga «Rapporto reciproco non trovato», o ``None``.

    ``{'sito', 'area_a', 'us_a', 'rapporto', 'us_b', 'area_b',
    'unita_tipo'}``: ``a`` è la scheda che dichiara il rapporto, ``b``
    quella in cui il reciproco manca — ed è ``area_b`` che dice in quale
    area cercarla, su uno scavo dove lo stesso numero esiste in più aree.

    ``None`` quando la riga non si legge: una correzione proposta con
    l'area indovinata scrive il reciproco sulla scheda sbagliata.
    """
    global _RIGA_RECIPROCO
    if _RIGA_RECIPROCO is None:
        import re
        _RIGA_RECIPROCO = re.compile(
            r"(?:Sito|Site|Ausgrabungsstätte)\s*:\s*(?P<sito>.*?)"
            r",\s*(?:Area|Areal)\s*:\s*(?P<area_a>.*?)"
            r",\s*(?P<tipo>[A-Za-z]+)\s*:\s*(?P<us_a>\S+)"
            r"\s+(?P<rapporto>.+?)"
            r"\s+(?P=tipo)\s*:\s*(?P<us_b>\S+)"
            r"\s+(?:Area|Areal)\s*:\s*(?P<area_b>[^:]*?)\s*:")
    trovato = _RIGA_RECIPROCO.search(riga or "")
    if not trovato:
        return None
    pezzi = {k: _t(v) for k, v in trovato.groupdict().items()}
    pezzi["unita_tipo"] = pezzi.pop("tipo")
    if not (pezzi["us_a"] and pezzi["us_b"] and pezzi["rapporto"]):
        return None
    return pezzi
