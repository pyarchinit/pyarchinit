"""Dove va ogni casella della matrice: le fasce e i livelli.

Due regole, nell'ordine:

1. **La fascia** è quella dell'epoca in cui l'unità è nata
   (``has_first_epoch``), e le fasce stanno in colonna dalla più recente
   in cima — come la matrice di pyArchInit e come EMStudio.
   È la lettura che l'archeologo si aspetta: ogni unità nel suo periodo.
2. **Il livello** dentro la fascia viene dalla stratigrafia: chi copre sta
   sopra chi è coperto. Le relazioni simmetriche («uguale a») non
   spingono giù nessuno.

Niente Qt, niente Graphviz, niente rete: l'impaginatore è puro, si prova
headless, e il pannello disegna soltanto quello che qui è già deciso.
Non si usa ``dot`` di proposito — il vincolo delle fasce non è il suo
mestiere, e il pannello deve funzionare su una installazione pulita.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .em_matrix_model import MatrixModel, Epoch, Unit

#: Relazioni che NON ordinano dall'alto in basso: le due unità sono
#: contemporanee, non una sopra l'altra.
SYMMETRIC_KINDS = frozenset({
    "equals", "bonded_to", "has_same_time", "is_physically_equal_to",
    "is_bonded_to", "contrasts_with",
})


@dataclass(frozen=True)
class LayoutConfig:
    box_w: float = 132.0
    box_h: float = 36.0
    h_gap: float = 26.0
    v_gap: float = 30.0
    band_pad: float = 18.0
    band_label_w: float = 196.0
    margin: float = 24.0
    #: Quante caselle al massimo su una riga prima di andare a capo.
    #: Senza questo, un sito dove quasi tutte le US stanno nello stesso
    #: periodo dava una fascia larga 103.000 pixel (misurato sul caso
    #: Ventena, 1311 US): illeggibile e impossibile da salvare.
    max_columns: int = 14
    #: Toglie dal DISEGNO i rapporti che un cammino più lungo già dice
    #: (come il «tred» di Graphviz): se A copre B e B copre C, l'arco
    #: A→C non aggiunge niente e sporca la matrice. I dati non si
    #: toccano, e i livelli restano calcolati su tutti i rapporti.
    transitive_reduction: bool = True
    #: Oltre questi archi la riduzione costa troppo e si salta.
    reduction_limit: int = 4000


@dataclass
class Box:
    unit: Unit
    x: float
    y: float
    w: float
    h: float


@dataclass
class Band:
    epoch: Optional[Epoch]
    label: str
    sublabel: str
    color: str
    y: float
    h: float


@dataclass
class Edge:
    kind: str
    points: List[Tuple[float, float]]
    symmetric: bool = False
    #: Il legame di un nodo di continuità: racconta per quanto a lungo
    #: una unità sopravvive, non che una sta sopra l'altra. Va disegnato
    #: a parte.
    continuity: bool = False


@dataclass
class Layout:
    bands: List[Band] = field(default_factory=list)
    boxes: List[Box] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    width: float = 0.0
    height: float = 0.0
    title: str = ""
    removed_redundant: int = 0


def _ranks(ids: Sequence[str], archi: Sequence[Tuple[str, str]]) -> Dict[str, int]:
    """Livello di ogni unità: 0 = nessuno la copre.

    Percorso più lungo calcolato a onde. Il taglio dei cicli: quando
    nessuno ha più grado d'ingresso zero e restano nodi, si promuove
    quello con meno archi entranti. Uno scavo reale un ciclo ce l'ha — la
    verifica rapporti lo segnala — e il disegno non è il posto per
    rifiutarlo.
    """
    rimasti = set(ids)
    entranti: Dict[str, set] = {i: set() for i in ids}
    uscenti: Dict[str, set] = {i: set() for i in ids}
    for s, t in archi:
        if s in entranti and t in entranti and s != t:
            entranti[t].add(s)
            uscenti[s].add(t)
    livello: Dict[str, int] = {}
    while rimasti:
        pronti = sorted(i for i in rimasti if not (entranti[i] & rimasti))
        if not pronti:
            # ciclo: si promuove chi ha meno vincoli ancora in piedi
            pronti = [min(sorted(rimasti),
                          key=lambda i: len(entranti[i] & rimasti))]
        for i in pronti:
            precedenti = [livello[p] for p in entranti[i] if p in livello]
            livello[i] = (max(precedenti) + 1) if precedenti else 0
        rimasti -= set(pronti)
    return livello


def _equality_groups(unita, relations) -> Dict[str, str]:
    """Rappresentante del gruppo di uguaglianza di ogni unità.

    «Uguale a» e «si lega a» non sono una sovrapposizione: le unità così
    legate sono la stessa cosa vista in due punti dello scavo e stanno
    sulla STESSA riga della matrice, accostate (regola della matrice di
    Harris, chiesta da Enzo il 2026-10-08). Per l'incolonnamento il
    gruppo conta come una unità sola.
    """
    padre = {i: i for i in unita}

    def radice(i):
        while padre[i] != i:
            padre[i] = padre[padre[i]]
            i = padre[i]
        return i

    for r in relations:
        if r.kind in SYMMETRIC_KINDS and r.source in padre and r.target in padre:
            a, b = radice(r.source), radice(r.target)
            if a != b:
                padre[max(a, b)] = min(a, b)
    return {i: radice(i) for i in unita}


def _components(archi: Sequence[Tuple[str, str]]) -> Dict[str, int]:
    """A quale gruppo fortemente connesso appartiene ogni nodo.

    Tarjan iterativo (niente ricorsione: una sequenza stratigrafica lunga
    farebbe saltare il limite di Python). Serve alla riduzione: dentro un
    gruppo ogni arco ha una strada alternativa — il giro stesso — e
    toglierlo cancellerebbe un rapporto vero.
    """
    adiacenti: Dict[str, list] = {}
    for s, t in archi:
        adiacenti.setdefault(s, []).append(t)
        adiacenti.setdefault(t, [])
    indice: Dict[str, int] = {}
    minimo: Dict[str, int] = {}
    sulla_pila: Dict[str, bool] = {}
    pila: list = []
    gruppo: Dict[str, int] = {}
    contatore = [0]
    gruppi = [0]

    for radice in sorted(adiacenti):
        if radice in indice:
            continue
        lavoro = [(radice, iter(adiacenti[radice]))]
        indice[radice] = minimo[radice] = contatore[0]
        contatore[0] += 1
        pila.append(radice)
        sulla_pila[radice] = True
        while lavoro:
            nodo, vicini = lavoro[-1]
            avanzato = False
            for prossimo in vicini:
                if prossimo not in indice:
                    indice[prossimo] = minimo[prossimo] = contatore[0]
                    contatore[0] += 1
                    pila.append(prossimo)
                    sulla_pila[prossimo] = True
                    lavoro.append((prossimo, iter(adiacenti[prossimo])))
                    avanzato = True
                    break
                if sulla_pila.get(prossimo):
                    minimo[nodo] = min(minimo[nodo], indice[prossimo])
            if avanzato:
                continue
            lavoro.pop()
            if lavoro:
                padre = lavoro[-1][0]
                minimo[padre] = min(minimo[padre], minimo[nodo])
            if minimo[nodo] == indice[nodo]:
                gruppi[0] += 1
                while True:
                    uscito = pila.pop()
                    sulla_pila[uscito] = False
                    gruppo[uscito] = gruppi[0]
                    if uscito == nodo:
                        break
    return gruppo


def _redundant(archi: Sequence[Tuple[str, str]],
               limite: int) -> set:
    """Gli archi che un cammino più lungo già dice.

    Il «tred» di Graphviz: se A copre B e B copre C, l'arco A→C non
    aggiunge niente. **Solo fra gruppi diversi**: dentro un ciclo ogni
    arco ha per forza una strada alternativa — il giro — e toglierlo
    cancellerebbe un rapporto che esiste. Un ciclo nei rapporti è un
    errore dell'archeologo da vedere, non da far sparire (trovato dalla
    review del 2026-10-08: un anello di quattro unità perdeva tutti e
    quattro gli archi).
    """
    if len(archi) > limite:
        return set()                    # su un grafo enorme non vale la pena
    gruppo = _components(archi)
    adiacenti: Dict[str, set] = {}
    for s, t in archi:
        adiacenti.setdefault(s, set()).add(t)
    ridondanti = set()
    for s, t in archi:
        if gruppo.get(s) == gruppo.get(t):
            continue                    # stesso ciclo: non si tocca
        visti = {s}
        pila = [n for n in adiacenti.get(s, ()) if n != t]
        trovato = False
        while pila:
            n = pila.pop()
            if n == t:
                trovato = True
                break
            if n in visti:
                continue
            visti.add(n)
            pila.extend(adiacenti.get(n, ()))
        if trovato:
            ridondanti.add((s, t))
    return ridondanti


def _mediana(valori):
    meta = len(valori) // 2
    if len(valori) % 2:
        return valori[meta]
    return (valori[meta - 1] + valori[meta]) / 2.0


def _assign_x(righe, vicini, passo: float) -> Dict[str, float]:
    """L'ascissa di ogni unità: chi copre sopra e IN MEZZO a quello che
    copre, invece che incolonnato a sinistra.

    Il metodo è quello di `dot`: si parte dalle posizioni d'ordine, poi a
    onde — su e giù — ogni unità punta alla mediana delle sue vicine e la
    riga si ricompatta mantenendo le distanze. Senza questo passo una
    matrice sembra una pila, non una matrice (segnalato da Enzo:
    «non è esploso come un Harris matrix»).
    """
    x: Dict[str, float] = {}
    for riga in righe:
        for n, i in enumerate(riga):
            x[i] = n * passo
    for giro in range(6):
        sequenza = righe if giro % 2 == 0 else list(reversed(righe))
        for riga in sequenza:
            if not riga:
                continue
            desiderato = []
            for i in riga:
                vicine = sorted(x[v] for v in vicini.get(i, ()) if v in x)
                desiderato.append(_mediana(vicine) if vicine else x[i])
            corrente = [desiderato[0]]
            for d in desiderato[1:]:
                corrente.append(max(d, corrente[-1] + passo))
            # la riga si sposta in blocco sul punto che vorrebbe, così le
            # distanze restano e il baricentro ci arriva lo stesso
            scarto = _mediana(sorted(desiderato)) - _mediana(sorted(corrente))
            for i, valore in zip(riga, corrente):
                x[i] = valore + scarto
    minimo = min(x.values()) if x else 0.0
    return {i: valore - minimo for i, valore in x.items()}


def _order_within_ranks(per_livello: Dict[int, List[str]],
                        vicini: Dict[str, set]) -> None:
    """Riduce gli incroci: due passate baricentriche, su e giù."""
    livelli = sorted(per_livello)
    for giro in range(2):
        sequenza = livelli if giro == 0 else list(reversed(livelli))
        posizione = {i: n for lv in livelli
                     for n, i in enumerate(per_livello[lv])}
        for lv in sequenza:
            def baricentro(i):
                vicine = [posizione[v] for v in vicini.get(i, ())
                          if v in posizione]
                return (sum(vicine) / len(vicine)) if vicine else posizione[i]
            per_livello[lv].sort(key=lambda i: (baricentro(i), i))
            for n, i in enumerate(per_livello[lv]):
                posizione[i] = n


def layout(model: MatrixModel, config: LayoutConfig = LayoutConfig()) -> Layout:
    """Le coordinate di fasce, caselle e archi."""
    unita = {u.node_id: u for u in model.units}

    gruppo_uguali = _equality_groups(unita, model.relations)
    ordinanti = [(r.source, r.target) for r in model.relations
                 if r.kind not in SYMMETRIC_KINDS
                 and r.source in unita and r.target in unita]
    # Per i livelli il gruppo di uguaglianza conta come una unità sola:
    # altrimenti due unità uguali finirebbero su righe diverse.
    ordinanti_gruppi = [(gruppo_uguali[s], gruppo_uguali[t])
                        for s, t in ordinanti
                        if gruppo_uguali[s] != gruppo_uguali[t]]
    vicini: Dict[str, set] = {i: set() for i in unita}
    for r in model.relations:
        if r.source in unita and r.target in unita:
            vicini[r.source].add(r.target)
            vicini[r.target].add(r.source)

    gruppi: List[Tuple[Optional[Epoch], List[str]]] = []
    # La più recente in cima, comunque arrivino: il modello le ordina già,
    # ma un grafo costruito a mano non è tenuto a farlo.
    epoche = sorted(model.epochs, key=lambda e: (e.start, e.end), reverse=True)
    for epoca in epoche:
        dentro = [i for i, u in unita.items() if u.epoch_id == epoca.node_id]
        gruppi.append((epoca, dentro))
    senza = [i for i, u in unita.items() if u.epoch_id not in
             {e.node_id for e in epoche}]
    if senza:
        gruppi.append((None, senza))

    risultato = Layout(title=model.title)
    y = config.margin
    colonne_max = 1
    tutte_le_righe: List[List[str]] = []
    piani: List[Tuple[Optional[Epoch], List[List[str]], float, float]] = []
    for epoca, dentro in gruppi:
        insieme = set(dentro)
        rappresentanti = sorted({gruppo_uguali[i] for i in dentro})
        interni = [(s, t) for s, t in ordinanti_gruppi
                   if s in insieme and t in insieme]
        livello = _ranks(rappresentanti, interni)
        per_livello: Dict[int, List[str]] = {}
        for i in rappresentanti:
            per_livello.setdefault(livello.get(i, 0), []).append(i)
        _order_within_ranks(per_livello, vicini)
        # il gruppo si riapre qui: i suoi membri restano accostati
        membri: Dict[str, List[str]] = {}
        for i in sorted(dentro):
            membri.setdefault(gruppo_uguali[i], []).append(i)
        for chiave in list(per_livello):
            espansa: List[str] = []
            for rappresentante in per_livello[chiave]:
                espansa.extend(membri.get(rappresentante, [rappresentante]))
            per_livello[chiave] = espansa

        # Un livello affollato va a capo: le sue caselle occupano più
        # righe di disegno, e la fascia cresce in altezza invece che in
        # larghezza.
        righe_disegno: List[List[str]] = []
        for _livello, ids in sorted(per_livello.items()):
            for inizio in range(0, len(ids), config.max_columns):
                righe_disegno.append(ids[inizio:inizio + config.max_columns])
        righe = len(righe_disegno)
        altezza = (config.band_pad * 2
                   + (righe * config.box_h + max(righe - 1, 0) * config.v_gap
                      if righe else config.box_h))
        risultato.bands.append(Band(
            epoch=epoca,
            label=(epoca.name if epoca else "Senza epoca dichiarata"),
            sublabel=("%s — %s" % (_anno(epoca.start), _anno(epoca.end))
                      if epoca else "nessun periodo iniziale nella scheda"),
            color=(epoca.color if epoca else "#F2F2F2"),
            y=y, h=altezza))
        piani.append((epoca, righe_disegno, y, altezza))
        tutte_le_righe.extend(righe_disegno)
        colonne_max = max([colonne_max] + [len(r) for r in righe_disegno])
        y += altezza

    ascisse = _assign_x(tutte_le_righe, vicini, config.box_w + config.h_gap)
    for _epoca, righe_disegno, cima, _altezza in piani:
        for riga, ids in enumerate(righe_disegno):
            for i in ids:
                risultato.boxes.append(Box(
                    unit=unita[i],
                    x=config.margin + config.band_label_w + ascisse.get(i, 0.0),
                    y=cima + config.band_pad + riga * (config.box_h
                                                       + config.v_gap),
                    w=config.box_w, h=config.box_h))

    centro = {b.unit.node_id: b for b in risultato.boxes}
    ridondanti = (_redundant(ordinanti, config.reduction_limit)
                  if config.transitive_reduction else set())
    gia_disegnati = set()
    for r in model.relations:
        a, b = centro.get(r.source), centro.get(r.target)
        if a is None or b is None or r.source == r.target:
            continue                    # un cappio non dice niente a vista
        if (r.source, r.target, r.kind) in gia_disegnati:
            continue                    # la stessa relazione scritta due volte
        gia_disegnati.add((r.source, r.target, r.kind))
        simmetrica = r.kind in SYMMETRIC_KINDS
        if not simmetrica and (r.source, r.target) in ridondanti:
            risultato.removed_redundant += 1
            continue
        continuita = "BR" in (unita[r.source].node_type,
                              unita[r.target].node_type)
        risultato.edges.append(Edge(
            kind=r.kind, symmetric=simmetrica, continuity=continuita,
            points=_route(a, b, simmetrica,
                          scarto=((len(risultato.edges) % 3) - 1) * 4.0)))

    risultato.width = max(
        [config.margin * 2 + config.band_label_w + config.box_w]
        + [b.x + b.w + config.margin for b in risultato.boxes])
    risultato.height = y + config.margin
    return risultato


#: Quanto scende la linea prima di spostarsi di lato. Corto: deve
#: staccarsi dalla casella di partenza, non tagliare la pagina.
_STACCO = 14.0


def _route(a: Box, b: Box, simmetrica: bool,
           scarto: float = 0.0) -> List[Tuple[float, float]]:
    """La spezzata da ``a`` a ``b``: un pezzetto giù, di lato, poi giù.

    Lo spostamento laterale avviene **subito sotto la casella di
    partenza**, non a metà strada: così una relazione che attraversa più
    fasce scende nella colonna di arrivo invece di tagliare in verticale
    le caselle che incontra (visto sul primo disegno del sito di
    esempio). ``scarto`` sposta di poco la discesa, perché due linee
    vicine non si sovrappongano fino a sembrarne una.
    """
    if simmetrica:
        # Due linee orizzontali, come il segno di uguale: è così che la
        # matrice di Harris dice «sono la stessa cosa».
        sinistra, destra = (a, b) if a.x <= b.x else (b, a)
        x1, x2 = sinistra.x + sinistra.w, destra.x
        meta = sinistra.y + sinistra.h / 2
        return [(x1, meta - 3.0), (x2, meta - 3.0),
                (x1, meta + 3.0), (x2, meta + 3.0)]
    # Quando l'arrivo sta PIÙ IN ALTO della partenza — i periodi e la
    # stratigrafia si contraddicono — si esce dal lato di sopra e si
    # arriva dal lato di sotto, altrimenti la spezzata si ripiega su sé
    # stessa (review 2026-10-08).
    allinsu = b.y + b.h <= a.y
    p = (a.x + a.w / 2, a.y if allinsu else a.y + a.h)
    q = (b.x + b.w / 2, b.y + b.h if allinsu else b.y)
    if abs(p[0] - q[0]) < 0.5 and not scarto:
        return [p, q]
    passo = -_STACCO if allinsu else _STACCO
    giu = p[1] + passo
    if (allinsu and giu < q[1]) or (not allinsu and giu > q[1]):
        giu = (p[1] + q[1]) / 2
    x = q[0] + scarto
    return [p, (p[0], giu), (x, giu), q]


def _anno(valore: float) -> str:
    anno = int(round(valore))
    return "%d a.C." % abs(anno) if anno < 0 else "%d" % anno
