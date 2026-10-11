"""L'anteprima della matrice: il filtro, i confini, la composizione.

Il bottone «visualizza matrix» della scheda US disegnava tutto il sito
con Graphviz (``tred`` + ``dot``) e mostrava il JPEG in una finestra di
matplotlib. Dal 5.13.72-alpha disegna invece la matrice di s3dgraphy —
la stessa dell'em.json e del pannello dell'Extended Matrix, quindi con
anche i nodi di paradato: estrattori, combinatori, proprietà,
documenti — ridotta alle **sole unità che la query corrente ha messo in
``DATA_LIST``**, e sotto di essa la pianta delle stesse unità. Tutto in
un PNG solo dentro ``pyarchinit_Matrix_folder``, perché una immagine si
porta in una relazione e una finestra no (richiesta di Enzo del
2026-10-11).

Qui sta la parte che **decide**, e che si prova headless: quali unità
restano, quali restano sbiadite, come si ritrovano le geometrie nei
layer, quanto viene grande l'immagine e dove si incolla ciascun pezzo.
Il disegno vero — la scena Qt della matrice e il render dei layer — sta
in ``matrix_preview_png``, che è l'unico pezzo che tocca QGIS.

Niente Qt, niente QGIS, niente database.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .em_matrix_links import FIELD_SETS, unit_identity
from .em_matrix_model import MatrixModel
from .em_matrix_records import unit_type

#: L'identità di una unità per il confronto: sito, area, us, tipo.
UnitKey = Tuple[str, str, str, str]

#: Come i layer dei disegni chiamano sito, area, us e tipo. Le prime due
#: righe sono quelle di ``em_matrix_links.FIELD_SETS`` — un test incrocia
#: le due tabelle, perché due copie che divergono sono peggio di una
#: copia sola. La terza è la tabella delle quote, che non serviva allo
#: zoom e serve qui: la pianta le disegna.
PLAN_FIELD_SETS = FIELD_SETS + (("sito_q", "area_q", "us_q", "unita_tipo_q"),)

#: Le tabelle da cui viene la pianta, nell'ordine in cui si disegnano:
#: prima le unità, poi le quote sopra, che sono punti e devono restare
#: leggibili. ``pyarchinit_quote_usm`` c'è nello schema ma è vuota in
#: ogni database visto finora: entra nell'elenco e, se non dà
#: geometrie, non fa male a nessuno.
PLAN_TABLES = (
    "pyunitastratigrafiche",
    "pyunitastratigrafiche_usm",
    "pyarchinit_quote",
    "pyarchinit_quote_usm",
)

#: Larghezza e altezza in pixel che la pianta non scavalca. Il tetto
#: serve: un'immagine che non si alloca non è un'anteprima.
PLAN_MIN_W, PLAN_MAX_W = 520, 4000
PLAN_MIN_H, PLAN_MAX_H = 260, 2800

#: Lo spazio fra la matrice e la pianta, dove passa la riga di stacco.
GUTTER = 28


@dataclass(frozen=True)
class Identity:
    """Le quattro colonne con cui si ritrova una unità.

    Non il solo numero di US: questo plugin distingue la US 1 dell'area 1
    dalla US 1 dell'area 2 in tutto il resto, e una matrice che le
    confondesse contraddirebbe la scheda da cui è nata.
    """
    sito: str
    area: str
    us: str
    unita_tipo: str

    @property
    def key(self) -> UnitKey:
        """L'identità per il confronto: sigle vecchie convertite.

        ``USVA`` e ``USVs`` sono la stessa cosa scritta in due momenti
        della vita del vocabolario (migrazione
        ``2026_05_us_vocabulary_alignment``): confrontarle alla lettera
        farebbe sparire dalla matrice unità che la query ha scelto.
        """
        return (self.sito, self.area, self.us, _tipo(self.unita_tipo))


def _testo(valore) -> str:
    return str(valore).strip() if valore is not None else ""


def _tipo(valore) -> str:
    """Il tipo normalizzato: sigla vecchia convertita, maiuscole ignorate."""
    return unit_type(valore).casefold()


def _campo(record, nome):
    """Il campo della riga, sia che sia un oggetto sia un dizionario.

    ``DATA_LIST`` porta le righe di ``us_table`` come oggetti del
    mappatore; i test le passano come dizionari, che è la stessa cosa
    detta senza database.
    """
    if isinstance(record, dict):
        return record.get(nome)
    return getattr(record, nome, None)


def identities_from_records(records: Iterable) -> Tuple[Identity, ...]:
    """Le identità delle righe date, nell'ordine, senza doppioni.

    È il filtro dell'anteprima: quello che l'archeologo ha davanti nella
    scheda — la query che ha fatto — e non tutto lo scavo. Una riga senza
    sito o senza numero di US non identifica niente e si salta.
    """
    viste: Set[UnitKey] = set()
    identita: List[Identity] = []
    for record in records or ():
        voce = Identity(
            sito=_testo(_campo(record, "sito")),
            area=_testo(_campo(record, "area")),
            us=_testo(_campo(record, "us")),
            unita_tipo=_testo(_campo(record, "unita_tipo")))
        if not voce.sito or not voce.us:
            continue
        if voce.key in viste:
            continue
        viste.add(voce.key)
        identita.append(voce)
    return tuple(identita)


def choose_site(identities: Sequence[Identity],
                requested=None) -> Tuple[str, List[str]]:
    """Il sito da disegnare e quelli che restano fuori.

    Il grafo si costruisce per un sito alla volta, ma una ricerca può
    toccarne più d'uno. Comanda **la ricerca**, non la casella del sito:
    se quella che il chiamante propone non è fra i siti delle righe
    trovate — la casella si può cambiare senza rifare la ricerca —
    varrebbe il sito di un grafo che con queste unità non c'entra, e la
    matrice uscirebbe vuota.
    """
    siti: List[str] = []
    for voce in identities or ():
        if voce.sito not in siti:
            siti.append(voce.sito)
    if not siti:
        return (str(requested or "").strip(), [])
    chiesto = str(requested or "").strip()
    scelto = chiesto if chiesto in siti else siti[0]
    return (scelto, [s for s in siti if s != scelto])


def keys_of(identities: Iterable[Identity]) -> frozenset:
    """Le identità come insieme di chiavi, pronte per il confronto."""
    return frozenset(i.key for i in identities or ())


def key_of_unit(unit) -> Optional[UnitKey]:
    """La chiave dell'unità dell'em.json, o ``None``.

    ``None`` per tutto ciò che non è una riga della scheda: l'em.json
    porta ``sito``, ``area``, ``us`` e ``unita_tipo`` dentro ``data``
    per ogni nodo che viene da ``us_table`` — anche per gli estrattori e
    i documenti, che in pyArchInit sono righe della scheda come le
    altre — e non li porta per un'epoca o per un gruppo.
    """
    identita = unit_identity(unit)
    if not identita:
        return None
    return (identita.get("sito", ""), identita.get("area", ""),
            identita.get("us", ""), _tipo(identita.get("unita_tipo")))


def filter_model(model, keys):
    """La matrice ridotta alle unità scelte, più un salto intorno.

    Un rapporto che esce dall'insieme scelto pone una domanda: buttare
    l'arco, o tenere la casella all'altro capo? Si tiene la casella, e
    **sbiadita** — la stessa scelta che il Time Manager fa già
    (``em_matrix_records._bridges``, campo ``Unit.dimmed``). Buttare
    l'arco farebbe sembrare che la US scelta non copra niente, cioè
    direbbe una cosa falsa sulla stratigrafia; tenere la casella senza
    sbiadirla farebbe sembrare che sia fra quelle che si stanno
    guardando. Un salto solo: se no una US tirerebbe dentro mezzo scavo.

    Un rapporto fra due caselle entrambe sbiadite non si disegna: quella
    casella è lì per mostrare dove va il rapporto della US scelta, non
    per raccontare una sequenza sua.

    Le epoche che non hanno più nessuna unità se ne vanno: una fascia
    vuota occupa altezza e non racconta niente, e l'immagine deve
    adattarsi al contenuto.

    Senza chiavi — nessuna query, nessun filtro — si restituisce la
    matrice come sta: tutto il sito.
    """
    if not keys:
        return model
    scelte = {u.node_id for u in model.units if key_of_unit(u) in keys}
    if not scelte:
        # Nessuna delle unità filtrate sta nel grafo: meglio dirlo e
        # disegnare tutto, che consegnare un'immagine vuota.
        return replace_warnings(model, [
            "Nessuna delle unità filtrate si ritrova nella matrice del "
            "sito: la disegno tutta."])
    vicine: Set[str] = set()
    for r in model.relations:
        if r.source in scelte and r.target not in scelte:
            vicine.add(r.target)
        elif r.target in scelte and r.source not in scelte:
            vicine.add(r.source)
    dentro = scelte | vicine
    unita = [u if u.node_id in scelte else replace(u, dimmed=True)
             for u in model.units if u.node_id in dentro]
    relazioni = [r for r in model.relations
                 if (r.source in scelte or r.target in scelte)
                 and r.source in dentro and r.target in dentro]
    usate = {u.epoch_id for u in unita}
    epoche = [e for e in model.epochs if e.node_id in usate]
    avvisi = list(model.warnings)
    fuori = len(model.units) - len(unita)
    if fuori:
        avvisi.append("%d unità del sito non entrano in questa matrice: "
                      "la vista è filtrata." % fuori)
    if vicine:
        avvisi.append("%d unità sono disegnate sbiadite: non sono fra "
                      "quelle filtrate, ma un rapporto le cita."
                      % len(vicine))
    return MatrixModel(units=unita, epochs=epoche, relations=relazioni,
                       title=model.title, warnings=avvisi)


def replace_warnings(model, aggiunte):
    """Lo stesso modello con qualche avviso in più."""
    return MatrixModel(units=list(model.units), epochs=list(model.epochs),
                       relations=list(model.relations), title=model.title,
                       warnings=list(model.warnings) + list(aggiunte))


# ------------------------------------------------------------- la pianta

def _virgolette(valore: str) -> str:
    """Il valore dentro un'espressione QGIS: l'apostrofo si raddoppia,
    altrimenti «L'Aquila» spezza l'espressione in due."""
    return "'%s'" % str(valore).replace("'", "''")


def layer_filter(identities: Sequence[Identity],
                 fields: Iterable[str]) -> Optional[str]:
    """L'espressione che tiene nel layer le sole unità scelte, o ``None``.

    ``None`` vuol dire «questo layer non sa chi sono»: chi chiama lo
    lascia fuori dalla pianta invece di disegnarci tutto lo scavo.

    Le unità si raggruppano per sito, area e tipo, e il numero di US
    finisce in un ``IN``: con 1300 US una catena di ``OR`` a quattro
    condizioni diventa un'espressione che QGIS valuta per ogni
    geometria del layer.

    Il tipo si confronta **con tolleranza**: ``unita_tipo_s`` e
    ``unita_tipo_q`` sono colonne aggiunte ai disegni e sono vuote in
    ogni database visto finora (nel sito di esempio sono NULL su tutte e
    700 le quote). Una geometria in più sulla pianta si vede e si
    capisce; una pianta vuota perché la colonna non è stata riempita,
    no.
    """
    campi = {str(c) for c in (fields or ())}
    scelta = None
    for insieme in PLAN_FIELD_SETS:
        if {insieme[0], insieme[2]} <= campi:
            scelta = insieme
            break
    if scelta is None or not identities:
        return None
    sito_f, area_f, us_f, tipo_f = scelta
    gruppi: Dict[Tuple[str, str, str], List[str]] = {}
    for voce in identities:
        chiave = (voce.sito, voce.area, voce.unita_tipo)
        if voce.us not in gruppi.setdefault(chiave, []):
            gruppi[chiave].append(voce.us)
    pezzi = []
    for (sito, area, tipo), numeri in gruppi.items():
        parti = ['"%s" = %s' % (sito_f, _virgolette(sito))]
        if area and area_f in campi:
            parti.append('"%s" = %s' % (area_f, _virgolette(area)))
        if tipo and tipo_f in campi:
            parti.append('("%s" IS NULL OR "%s" = \'\' OR "%s" = %s)'
                         % (tipo_f, tipo_f, tipo_f, _virgolette(tipo)))
        parti.append('"%s" IN (%s)'
                     % (us_f, ", ".join(_virgolette(n) for n in numeri)))
        pezzi.append("(%s)" % " AND ".join(parti))
    if len(pezzi) == 1:
        return pezzi[0]
    return " OR ".join(pezzi)


def plan_size(matrix_width, extent) -> Optional[Tuple[int, int]]:
    """Quanto grande viene la pianta: ``(larghezza, altezza)`` o ``None``.

    Larga come la matrice — così le due metà dell'immagine si leggono
    come una colonna sola — e alta quanto chiede la forma dello scavo.
    ``extent`` è ``(x1, y1, x2, y2)`` nell'unità del layer; ``None``
    quando le unità scelte non hanno nessuna geometria, e allora
    l'immagine è la sola matrice.

    L'altezza non deforma niente: il render allarga l'inquadratura fino
    al rapporto dell'immagine, non la schiaccia. Entro i limiti si
    mostra lo scavo, oltre si mostra un po' più di contorno.
    """
    if not extent:
        return None
    x1, y1, x2, y2 = (float(v) for v in extent)
    larghezza_mondo, altezza_mondo = x2 - x1, y2 - y1
    if larghezza_mondo <= 0 and altezza_mondo <= 0:
        # Un punto solo — una quota, una US disegnata con un solo vertice:
        # si disegna comunque, quadrata.
        rapporto = 1.0
    elif larghezza_mondo <= 0:
        rapporto = float(PLAN_MAX_H)
    else:
        rapporto = altezza_mondo / larghezza_mondo
    larghezza = int(round(min(max(float(matrix_width or 0), PLAN_MIN_W),
                              PLAN_MAX_W)))
    altezza = int(round(min(max(larghezza * rapporto, PLAN_MIN_H),
                            PLAN_MAX_H)))
    return (larghezza, altezza)


@dataclass(frozen=True)
class Composition:
    """Dove va ogni pezzo nell'immagine finale."""
    width: int
    height: int
    #: ``(x, y)`` dell'angolo in alto a sinistra, o ``None`` se il pezzo
    #: non c'è.
    matrix_at: Optional[Tuple[int, int]] = None
    plan_at: Optional[Tuple[int, int]] = None
    #: L'ordinata della riga di stacco, o ``None`` con un pezzo solo.
    divider_y: Optional[int] = None


def compose(matrix: Optional[Tuple[int, int]],
            plan: Optional[Tuple[int, int]],
            gutter: int = GUTTER) -> Optional[Composition]:
    """La misura dell'immagine finale e il posto dei due pezzi.

    La matrice sopra, la pianta sotto — come ha chiesto Enzo — larghe
    quanto il più largo dei due, con il più stretto centrato: una
    colonna sbilanciata si legge come un errore di impaginazione.
    L'altezza è la somma più lo stacco. Niente pagina fissa: l'immagine
    si adatta al contenuto, che è il motivo per cui non si passa da una
    composizione di stampa.

    ``None`` se non c'è niente da comporre.
    """
    pezzi = [p for p in (matrix, plan)
             if p and int(p[0]) > 0 and int(p[1]) > 0]
    if not pezzi:
        return None
    larghezza = max(int(p[0]) for p in pezzi)
    stacco = int(gutter) if len(pezzi) > 1 else 0
    altezza = sum(int(p[1]) for p in pezzi) + stacco
    y = 0
    matrice_in = pianta_in = None
    riga = None
    if matrix and int(matrix[0]) > 0 and int(matrix[1]) > 0:
        matrice_in = ((larghezza - int(matrix[0])) // 2, y)
        y += int(matrix[1])
        if stacco:
            riga = y + stacco // 2
            y += stacco
    if plan and int(plan[0]) > 0 and int(plan[1]) > 0:
        pianta_in = ((larghezza - int(plan[0])) // 2, y)
    return Composition(width=larghezza, height=altezza,
                       matrix_at=matrice_in, plan_at=pianta_in,
                       divider_y=riga)


# --------------------------------------------------- da dove si leggono

@dataclass(frozen=True)
class PlanSource:
    """Come QGIS arriva ai layer dei disegni.

    Si ricava dalla stringa di connessione che il plugin ha già in mano,
    senza rileggere ``config.cfg``: una fonte sola per il grafo e per la
    pianta non può divergere.
    """
    provider: str
    #: Il file SQLite, per ``ogr``.
    path: str = ""
    #: I pezzi della connessione PostgreSQL. La password non si registra
    #: da nessuna parte: viaggia solo nell'URI che si consegna a QGIS.
    host: str = ""
    port: str = ""
    database: str = ""
    user: str = ""
    password: str = ""


#: Le colonne con cui si riconosce una unità disegnata e si sceglie il suo
#: poligono rappresentativo: sito, area, US, indice. Sono quelle di
#: ``pyunitastratigrafiche`` e ``pyunitastratigrafiche_usm``, che hanno
#: lo stesso schema.
LABEL_FIELDS = ("scavo_s", "area_s", "us_s", "stratigraph_index_us")

#: Il campo chiave dei due layer, con cui si indica un poligono preciso.
LABEL_KEY = "gid"


def label_ids(rows: Iterable[Tuple]) -> List:
    """I poligoni da etichettare: **uno per unità**, il più grande.

    ``rows`` sono ``(gid, sito, area, us, indice, area_mq)``.

    Perché uno solo. La convenzione del plugin
    (``styles_spatialite/us_vuote.qml``) etichetta la riga con
    ``stratigraph_index_us = 2``, ma un'unità può averne **più di una**:
    nel database di esempio la US 2 ne ha due, e sull'anteprima il suo
    numero compariva due volte, cerchiato, in due punti diversi del
    disegno. Erano i «doppioni» che si vedevano (Enzo, 11 ottobre 2026).

    Quale delle due: la **più grande**, perché è il corpo dell'unità e non
    un lembo, e perché così l'etichetta cade dove l'archeologo la
    cercherebbe. A parità di area vince il `gid` più piccolo, che è stabile
    da un disegno all'altro.

    Un'unità senza nessun poligono di indice 2 — 10 delle 170 di
    ``pyunitastratigrafiche_usm``, la US 0 — prende comunque il suo:
    altrimenti resterebbe senza etichetta e nessuno saprebbe perché.
    """
    migliore: Dict[Tuple, Tuple] = {}
    for riga in rows:
        gid, sito, area, us, indice = riga[:5]
        superficie = float(riga[5]) if len(riga) > 5 and riga[5] is not None \
            else 0.0
        chiave = (_testo(sito), _testo(area), _testo(us))
        # Prima l'indice 2, poi l'area, poi il gid: un poligono di contorno
        # batte sempre un incluso, anche se l'incluso fosse più grande.
        punteggio = (1 if str(indice).strip() in ("2", "2.0") else 0,
                     superficie, -_ordine(gid))
        if chiave not in migliore or punteggio > migliore[chiave][0]:
            migliore[chiave] = (punteggio, gid)
    return sorted((v[1] for v in migliore.values()), key=_ordine)


def _ordine(gid):
    """Un `gid` ordinabile anche quando arriva come testo."""
    try:
        return int(gid)
    except (TypeError, ValueError):
        return 0


def fallback_label_ids(rows: Iterable[Tuple]) -> List:
    """Compatibilità: i poligoni da etichettare perché la loro unità non ha
    l'indice 2. Sostituita da :func:`label_ids`, che ne sceglie uno per
    unità invece di aggiungerne alle righe con l'indice 2."""
    con_due: Dict[Tuple, bool] = {}
    primo: Dict[Tuple, object] = {}
    for riga in rows:
        gid, sito, area, us, indice = riga[:5]
        chiave = (_testo(sito), _testo(area), _testo(us))
        if str(indice).strip() in ("2", "2.0"):
            con_due[chiave] = True
        con_due.setdefault(chiave, False)
        if chiave not in primo or _ordine(gid) < _ordine(primo[chiave]):
            primo[chiave] = gid
    return sorted((primo[c] for c, c2 in con_due.items() if not c2),
                  key=_ordine)


def label_expression(ids: Iterable = (), prefisso: str = "US") -> str:
    """L'espressione dell'etichetta «US n», per i soli poligoni scelti.

    Il testo è quello della convenzione di ``us_vuote.qml`` — il prefisso
    dell'unità, uno spazio, il numero — e ``NULL`` (nessuna etichetta) per
    tutti gli altri poligoni.

    Il **prefisso** lo dice il chiamante perché lo sa solo lui: nel layer
    `pyunitastratigrafiche_usm` la colonna `unita_tipo_s` è vuota, quindi
    dal dato non si capisce che quelle sono USM, e il disegno le chiamava
    «US 1», «US 2»… come le unità stratigrafiche. Due unità diverse con lo
    stesso nome sulla stessa pianta sembrano un doppione, e non lo sono.
    """
    elenco = [str(_ordine(i)) for i in ids]
    if not elenco:
        return "NULL"
    return ("CASE WHEN \"%s\" IN (%s) THEN '%s' || ' ' || \"us_s\" END"
            % (LABEL_KEY, ", ".join(elenco), prefisso))


def plan_source(conn_str) -> Optional[PlanSource]:
    """La fonte dei layer dalla stringa di connessione, o ``None``.

    Si riconoscono le due che pyArchInit usa: ``sqlite:///percorso`` e
    ``postgresql://utente:parola@host:porta/base``. Il provider OGR, e
    non quello spatialite, per lo stesso motivo per cui lo usa
    ``_load_spatialite_view``: quello spatialite si tiene in cache lo
    schema sbagliato.
    """
    testo = str(conn_str or "").strip()
    if not testo:
        return None
    if testo.startswith("sqlite:"):
        percorso = testo.split("///", 1)[-1].split("?", 1)[0]
        if not percorso or percorso == ":memory:":
            return None
        return PlanSource(provider="ogr", path=percorso)
    if testo.startswith("postgres"):
        try:
            from urllib.parse import unquote, urlsplit
            pezzi = urlsplit(testo)
        except Exception:                           # noqa: BLE001
            return None
        if not pezzi.hostname:
            return None
        return PlanSource(
            provider="postgres",
            host=pezzi.hostname,
            port=str(pezzi.port or 5432),
            database=unquote((pezzi.path or "").lstrip("/")),
            user=unquote(pezzi.username or ""),
            password=unquote(pezzi.password or ""))
    return None
