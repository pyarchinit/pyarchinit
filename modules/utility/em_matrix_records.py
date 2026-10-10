"""La matrice costruita dalle righe della scheda, senza passare da un file.

Il pannello dell'Extended Matrix parte dall'em.json, che è la cosa giusta
quando si vuole vedere esattamente quello che viaggia verso EMStudio. Il
Time Manager ha un'altra esigenza: disegnare la matrice delle sole US
visibili alla posizione corrente del cursore, molte volte di seguito,
mentre l'archeologo muove la manopola o l'atlante sforna una pagina dopo
l'altra. Lì passare da un file — e da Graphviz, cioè da un sottoprocesso
e da un JPEG di megabyte — costa troppo.

Questo modulo costruisce lo stesso ``MatrixModel`` a partire dai record,
così l'impaginatore, il writer SVG e la vista Qt sono gli stessi: una
matrice sola, disegnata in un modo solo, da qualunque parte arrivi.

Niente Qt, niente QGIS, niente s3dgraphy, niente database: si prova tutto
headless e in millisecondi.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .em_matrix_model import Epoch, MatrixModel, Relation, Unit

#: La vecchia scrittura dei tipi virtuali. È la stessa mappa della
#: migrazione ``2026_05_us_vocabulary_alignment``; un test la incrocia con
#: quella, perché due copie che divergono sono peggio di una copia sola.
LEGACY_UNITA_TIPO = {"USVA": "USVs", "USVB": "USVn",
                     "USVC": "USVn", "USVc": "USVn"}


#: Indice della voce nel vocabolario dei rapporti → ``(tipo, da girare)``.
#: Lo stesso ordine di ``RELATIONSHIPS`` del plugin e di
#: ``_REL_INDEX_EDGE_TYPE`` della libreria, che un test incrocia. «Da
#: girare» vuol dire che la voce dice la stessa cosa dall'altro capo —
#: «coperto da» rispetto a «copre» — e nella matrice la freccia deve
#: partire sempre da chi sta sopra.
REL_INDEX_KIND = (
    ("equals", False),      # 0  Uguale a
    ("bonded_to", False),   # 1  Si lega a
    ("overlies", False),    # 2  Copre
    ("overlies", True),     # 3  Coperto da
    ("fills", False),       # 4  Riempie
    ("fills", True),        # 5  Riempito da
    ("cuts", False),        # 6  Taglia
    ("cuts", True),         # 7  Tagliato da
    ("abuts", False),       # 8  Si appoggia a
    ("abuts", True),        # 9  Gli si appoggia
    # La coppia della continuità. «X successiva a T» è «X is_after T»: la
    # freccia parte da X, che è il più recente, come per «Copre». «X
    # precedente a T» è la stessa cosa letta dall'altro capo («T is_after
    # X»), che la libreria nomina is_before: si gira, come «Coperto da».
    ("is_after", False),    # 10 Continuità successiva a
    ("is_after", True),     # 11 Continuità precedente a
)


def _kinds():
    """Ogni voce dei rapporti, in tutte le lingue, verso il suo tipo.

    Si legge dal vocabolario i18n del plugin: le voci sono quelle che
    l'archeologo ha scritto nella scheda, in italiano, tedesco, inglese,
    arabo… La posizione nella lista è il significato, ed è la stessa in
    tutte le lingue.
    """
    from .pyarchinit_i18n_stratigraphic import RELATIONSHIPS

    tabella: Dict[str, Tuple[str, bool]] = {}
    for voci in RELATIONSHIPS.values():
        for indice, voce in enumerate(voci):
            if indice < len(REL_INDEX_KIND):
                tabella.setdefault(str(voce).strip().lower(),
                                   REL_INDEX_KIND[indice])
    return tabella


_KINDS: Optional[Dict[str, Tuple[str, bool]]] = None


def kind_of(voce) -> Optional[Tuple[str, bool]]:
    """``(tipo, da girare)`` della voce di rapporto, o ``None``."""
    global _KINDS
    if _KINDS is None:
        try:
            _KINDS = _kinds()
        except Exception:                           # noqa: BLE001
            _KINDS = {}
    return _KINDS.get(str(voce or "").strip().lower())


def unit_type(unita_tipo) -> str:
    """Il tipo con cui si disegna l'unità, vecchie sigle convertite."""
    tipo = str(unita_tipo or "").strip() or "US"
    return LEGACY_UNITA_TIPO.get(tipo, tipo)


def node_id(area, us, tipo) -> str:
    """L'identità dell'unità nel disegno: «1.USM12»."""
    return "%s.%s%s" % (str(area or "").strip(), unit_type(tipo),
                        str(us or "").strip())


def _epoch_id(periodo, fase) -> Optional[str]:
    p, f = str(periodo or "").strip(), str(fase or "").strip()
    return "%s_%s" % (p, f) if p else None


def _anno(valore) -> float:
    try:
        return float(str(valore).strip())
    except (TypeError, ValueError):
        return 0.0


def _rapporti_di(record) -> Tuple[list, Optional[str]]:
    """Le voci del campo ``rapporti``, e il guasto se non si leggono."""
    grezzo = record.get("rapporti")
    if not grezzo:
        return [], None
    if isinstance(grezzo, (list, tuple)):
        return list(grezzo), None
    import ast
    try:
        letto = ast.literal_eval(str(grezzo))
    except Exception:                               # noqa: BLE001
        return [], "il campo rapporti non si legge"
    if not isinstance(letto, (list, tuple)):
        return [], "il campo rapporti non è un elenco"
    return list(letto), None


def _bridges(records, visible) -> Set[Tuple[str, str]]:
    """Le posizioni ``(area, us)`` che servono solo ad agganciare i nodi.

    Sono quelle che una unità visibile cita in ``rapporti``, e quelle che
    citano una unità visibile. Un salto solo, come faceva la via vecchia
    con Graphviz: bastano a non spezzare la sequenza senza tirare dentro
    tutto lo scavo.
    """
    ponti: Set[Tuple[str, str]] = set()
    for record in records or ():
        area = str(record.get("area") or "").strip()
        us = str(record.get("us") or "").strip()
        if not us:
            continue
        voci, _guasto = _rapporti_di(record)
        citate = set()
        for voce in voci:
            if not isinstance(voce, (list, tuple)) or len(voce) < 2:
                continue
            if kind_of(voce[0]) is None:
                continue
            bersaglio_us = str(voce[1] or "").strip()
            bersaglio_area = (str(voce[2]).strip() if len(voce) > 2
                              and str(voce[2] or "").strip() else area)
            if bersaglio_us:
                citate.add((bersaglio_area, bersaglio_us))
        if (area, us) in visible:
            ponti |= citate - visible          # chi la visibile cita
        elif citate & visible:
            ponti.add((area, us))              # chi cita la visibile
    return ponti


def model_from_records(records: Iterable[Dict[str, Any]],
                       periods: Sequence[Sequence[Any]] = (),
                       visible: Optional[Set[Tuple[str, str]]] = None,
                       title: str = "") -> MatrixModel:
    """La matrice delle righe date, con le sue fasce.

    ``records``: dizionari con almeno ``sito``, ``area``, ``us``,
    ``unita_tipo``, ``rapporti``, ``periodo_iniziale``, ``fase_iniziale``.
    ``periods``: righe di ``periodizzazione_table`` nella forma
    ``(periodo, fase, datazione_estesa, cron_iniziale, cron_finale)``.
    ``visible``: le coppie ``(area, us)`` da disegnare; ``None`` = tutte.

    Quello che non si può disegnare non ferma il disegno: finisce negli
    avvisi, come fa il lettore dell'em.json.
    """
    avvisi: List[str] = []
    unita: List[Unit] = []
    per_posizione: Dict[Tuple[str, str], str] = {}

    # Le unità che un rapporto cita o che citano una visibile: entrano nel
    # disegno, ma sbiadite. Un salto solo — se no una US visibile
    # tirerebbe dentro mezzo scavo.
    ponti = _bridges(records, visible) if visible is not None else set()

    for record in records or ():
        area = str(record.get("area") or "").strip()
        us = str(record.get("us") or "").strip()
        if not us:
            continue
        fuori = False
        if visible is not None and (area, us) not in visible:
            if (area, us) not in ponti:
                continue
            fuori = True
        tipo = unit_type(record.get("unita_tipo"))
        chiave = node_id(area, us, tipo)
        if chiave in {u.node_id for u in unita}:
            avvisi.append("Due righe per %s: ne disegno una." % chiave)
            continue
        # Un rapporto cita l'unità per area e numero, non per tipo: è così
        # che si ritrova il bersaglio.
        per_posizione.setdefault((area, us), chiave)
        dati = {k: v for k, v in record.items() if v not in (None, "")}
        dati["area"], dati["us"] = area, us
        unita.append(Unit(
            node_id=chiave, label=chiave, node_type=tipo,
            epoch_id=_epoch_id(record.get("periodo_iniziale"),
                               record.get("fase_iniziale")),
            description=str(record.get("d_stratigrafica") or ""),
            data=dati, dimmed=fuori))

    epoche = []
    for riga in periods or ():
        riga = list(riga) + [None] * (5 - len(riga))
        periodo, fase, datazione, inizio, fine = riga[:5]
        chiave = _epoch_id(periodo, fase)
        if not chiave:
            continue
        epoche.append(Epoch(
            node_id=chiave,
            name=str(datazione or "Periodo %s" % periodo),
            start=_anno(inizio), end=_anno(fine)))

    presenti = {u.node_id for u in unita}
    relazioni: List[Relation] = []
    gia = set()
    mancanti = 0
    for record in records or ():
        area = str(record.get("area") or "").strip()
        us = str(record.get("us") or "").strip()
        mio = per_posizione.get((area, us))
        if mio is None or mio not in presenti:
            continue
        voci, guasto = _rapporti_di(record)
        if guasto:
            avvisi.append("%s: %s." % (mio, guasto))
            continue
        for voce in voci:
            if not isinstance(voce, (list, tuple)) or len(voce) < 2:
                continue
            tipo_voce = kind_of(voce[0])
            if tipo_voce is None:
                continue
            bersaglio_us = str(voce[1] or "").strip()
            bersaglio_area = (str(voce[2]).strip() if len(voce) > 2
                              and str(voce[2] or "").strip() else area)
            altro = per_posizione.get((bersaglio_area, bersaglio_us))
            if altro is None or altro not in presenti:
                mancanti += 1
                continue
            kind, girare = tipo_voce
            a, b = (altro, mio) if girare else (mio, altro)
            if a == b or (a, b, kind) in gia:
                continue
            gia.add((a, b, kind))
            relazioni.append(Relation(source=a, target=b, kind=kind))

    if mancanti:
        avvisi.append(
            "%d rapporti non si disegnano: puntano a unità che non sono in "
            "questa matrice." % mancanti)
    # Le fasce si leggono dall'alto, la più recente in cima.
    epoche.sort(key=lambda e: (e.start != 0.0 or e.end != 0.0, e.start, e.end),
                reverse=True)
    return MatrixModel(units=unita, epochs=epoche, relations=relazioni,
                       title=title, warnings=avvisi)


def write_matrix_svg(records, periods, path, visible=None, title=""):
    """La matrice delle righe date, scritta in SVG. ``(percorso, modello)``.

    È la via che il Time Manager usa al posto di Graphviz: nessun
    sottoprocesso, nessun file intermedio, nessun JPEG di megabyte —
    misurato sul sito di esempio, 5 ms contro 300, e 29 KB contro 2,6 MB.
    Lo stesso impaginatore e lo stesso writer del pannello: una matrice
    sola, disegnata in un modo solo.
    """
    from .em_matrix_layout import layout
    from .em_matrix_svg import write_svg

    model = model_from_records(records, periods, visible, title)
    return write_svg(layout(model), path, title), model
