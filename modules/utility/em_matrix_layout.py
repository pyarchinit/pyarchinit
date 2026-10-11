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

import bisect
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .em_matrix_glyphs import box_size, label_overhang
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
    #: Le due unità che l'arco collega. Prima non c'erano, e senza di loro
    #: non si può né instradare intorno alle caselle altrui né misurare se
    #: una linea passa dentro una casella che non è la sua.
    source: str = ""
    target: str = ""
    symmetric: bool = False
    #: Il legame di un nodo di continuità: racconta per quanto a lungo
    #: una unità sopravvive, non che una sta sopra l'altra. Va disegnato
    #: a parte.
    continuity: bool = False
    #: La freccia risale le fasce invece di scendere: chi copre sta in
    #: un'epoca più antica di chi è coperto. È una contraddizione fra
    #: stratigrafia e cronologia, e si disegna in rosso perché si veda
    #: subito — convenzione dell'Extended Matrix (E. Demetrescu,
    #: 2026-10-09). Una relazione simmetrica non ha verso: mai in salita.
    upward: bool = False


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
                # Un pittogramma dell'Extended Matrix ha la casella
                # guidata dall'altezza, e la proprietà è larga quanto il
                # suo testo: la colonna resta quella di sempre e la
                # casella ci sta in mezzo, così le unità stratigrafiche
                # non si spostano di un pixel e la freccia di un glifo
                # arriva sul glifo invece che sul vuoto accanto.
                larghezza, altezza_casella = box_size(
                    unita[i].node_type, unita[i].label,
                    config.box_w, config.box_h)
                risultato.boxes.append(Box(
                    unit=unita[i],
                    x=(config.margin + config.band_label_w
                       + ascisse.get(i, 0.0)
                       + (config.box_w - larghezza) / 2.0),
                    y=cima + config.band_pad + riga * (config.box_h
                                                       + config.v_gap),
                    w=larghezza, h=altezza_casella))

    centro = {b.unit.node_id: b for b in risultato.boxes}
    # Un indice solo per tutto il disegno: le caselle non si muovono più.
    griglia = _Griglia(risultato.boxes)
    ridondanti = (_redundant(ordinanti, config.reduction_limit)
                  if config.transitive_reduction else set())
    gia_disegnati = set()
    for r in model.relations:
        a, b = centro.get(r.source), centro.get(r.target)
        if a is None or b is None or r.source == r.target:
            continue                    # un cappio non dice niente a vista
        simmetrica = r.kind in SYMMETRIC_KINDS
        # Una simmetrica si riconosce dalla **coppia**, non dal verso: «la 40
        # è uguale alla 41» e «la 41 è uguale alla 40» sono la stessa cosa
        # detta due volte — il reciproco, che l'archeologo scrive su entrambe
        # le schede — e disegnarle entrambe metteva due segni di uguale
        # identici uno sull'altro (visto rendendo la SVG del sito di prova:
        # quattro gruppi `edge equality` per due coppie).
        impronta = ((r.kind, frozenset((r.source, r.target))) if simmetrica
                    else (r.source, r.target, r.kind))
        if impronta in gia_disegnati:
            continue                    # la stessa relazione scritta due volte
        gia_disegnati.add(impronta)
        if not simmetrica and (r.source, r.target) in ridondanti:
            risultato.removed_redundant += 1
            continue
        continuita = "BR" in (unita[r.source].node_type,
                              unita[r.target].node_type)
        # y cresce verso il basso e la fascia più recente sta in cima:
        # se la partenza è più in basso dell'arrivo, la freccia risale.
        in_salita = (not simmetrica) and a.y > b.y
        risultato.edges.append(Edge(
            kind=r.kind, source=r.source, target=r.target,
            symmetric=simmetrica, continuity=continuita,
            upward=in_salita,
            points=_route(a, b, simmetrica,
                          scarto=((len(risultato.edges) % 3) - 1) * 4.0,
                          griglia=griglia,
                          esclusi=(r.source, r.target))))

    # Il nome di un pittogramma è più largo del pittogramma, e non si
    # taglia: la tela deve tenerci dentro anche quello, se no l'ultimo
    # documento a destra perde metà del suo nome fuori dal foglio.
    risultato.width = max(
        [config.margin * 2 + config.band_label_w + config.box_w]
        + [b.x + b.w + config.margin
           + label_overhang(b.unit.node_type, b.unit.label, b.w)
           for b in risultato.boxes])
    risultato.height = y + config.margin
    return risultato


#: Quanto scende la linea prima di spostarsi di lato. Corto: deve
#: staccarsi dalla casella di partenza, non tagliare la pagina.
_STACCO = 14.0


def attraversa(punti: Sequence[Tuple[float, float]],
               ostacoli: Sequence[Box], margine: float = 1.5,
               limite: int = 0) -> int:
    """Quante volte una spezzata entra dentro una delle caselle date.

    Serve a instradare e serve ai test: «nessun arco passa sotto un nodo» è
    una proprietà che si misura, non che si spera. Il margine lascia passare
    una linea che sfiora il bordo — gli estremi di un arco *toccano* per
    forza le loro caselle.

    ``limite`` ferma il conto appena lo raggiunge: quando la domanda è «ne
    attraversa almeno uno?» contarli tutti su una matrice da mille unità
    costa e non serve.
    """
    n = 0
    for (px, py), (qx, qy) in zip(punti, punti[1:]):
        for b in ostacoli:
            if limite and n >= limite:
                return n
            x1, y1 = b.x + margine, b.y + margine
            x2, y2 = b.x + b.w - margine, b.y + b.h - margine
            if x2 <= x1 or y2 <= y1:
                continue
            # Un segmento è orizzontale o verticale (la spezzata è
            # ortogonale): basta il rettangolo contro il rettangolo.
            sx1, sx2 = min(px, qx), max(px, qx)
            sy1, sy2 = min(py, qy), max(py, qy)
            if sx1 < x2 and x1 < sx2 and sy1 < y2 and y1 < sy2:
                n += 1
                break
    return n


def _corridoi(ostacoli: Sequence[Box]) -> List[float]:
    """Le quote dove una linea orizzontale non incontra nessuna casella.

    Una per ogni intercapedine fra due file di caselle, più una sopra la
    prima e una sotto l'ultima: sono le corsie in cui si può correre di
    lato senza passare sotto a nessuno.
    """
    if not ostacoli:
        return []
    bordi = sorted({round(b.y, 2) for b in ostacoli}
                   | {round(b.y + b.h, 2) for b in ostacoli})
    corsie = []
    for y1, y2 in zip(bordi, bordi[1:]):
        meta = (y1 + y2) / 2.0
        if not any(b.y < meta < b.y + b.h for b in ostacoli):
            corsie.append(meta)
    corsie.append(bordi[0] - 8.0)
    corsie.append(bordi[-1] + 8.0)
    return corsie


#: Quanto si sta larghi da una casella quando le si passa accanto.
_SPIRAGLIO = 7.0

#: Più larga di qualunque matrice: serve a dire «tutta la fila».
_MOLTO = 1e9


class _Griglia:
    """Le caselle indicizzate per fila e ordinate per ascissa.

    Serve a non guardare mille caselle per ogni tratto di ogni linea.
    Senza, l'impaginazione del database Ventena (1311 US, 655 rapporti)
    passava da meno di un secondo a **tredici**: quattro tratti per arco
    contro 1310 caselle fanno tre milioni e mezzo di confronti, in Python.
    Con l'indice si guardano solo le file che il tratto attraversa, e
    dentro la fila solo le caselle la cui ascissa ci sta — una manciata.
    """

    __slots__ = ("_righe", "_chiavi", "_xs", "_maxw")

    def __init__(self, boxes: Sequence[Box]):
        self._righe: Dict[Tuple[float, float], List[Box]] = {}
        for b in boxes:
            self._righe.setdefault((round(b.y, 1), round(b.h, 1)),
                                   []).append(b)
        for v in self._righe.values():
            v.sort(key=lambda c: c.x)
        self._chiavi = sorted(self._righe)
        self._xs = {k: [b.x for b in v] for k, v in self._righe.items()}
        self._maxw = {k: max(b.w for b in v) for k, v in self._righe.items()}

    def intorno(self, punti: Sequence[Tuple[float, float]],
                esclusi: Sequence[str] = ()) -> List[Box]:
        """Le caselle che una spezzata potrebbe incontrare, senza le sue."""
        ys = [y for _x, y in punti]
        xs = [x for x, _y in punti]
        return self.nella_fascia(min(ys), max(ys), min(xs), max(xs), esclusi)

    def nella_fascia(self, y1: float, y2: float, x1: float, x2: float,
                     esclusi: Sequence[str] = ()) -> List[Box]:
        lo_y, hi_y = min(y1, y2) - _SPIRAGLIO, max(y1, y2) + _SPIRAGLIO
        lo_x, hi_x = min(x1, x2) - _SPIRAGLIO, max(x1, x2) + _SPIRAGLIO
        fuori = set(esclusi)
        out: List[Box] = []
        for chiave in self._chiavi:
            ry, rh = chiave
            if ry > hi_y or lo_y > ry + rh:
                continue
            fila = self._righe[chiave]
            i = bisect.bisect_left(self._xs[chiave], lo_x - self._maxw[chiave])
            for b in fila[i:]:
                if b.x > hi_x:
                    break
                if b.unit.node_id not in fuori:
                    out.append(b)
        return out


def _blocchi(ostacoli: Sequence[Box], lo: float, hi: float,
             verticale: bool) -> List[Tuple[float, float]]:
    """Gli intervalli occupati lungo un asse, uniti.

    Con ``verticale`` si guarda chi sta nella fascia di ordinate
    ``lo..hi`` e si restituiscono le ascisse che occupa; senza, il
    contrario. Serve a trovare uno spiraglio **calcolandolo** invece di
    provare venti candidati e misurarli uno per uno: su quattrocento unità
    quella ricerca costava più di un minuto.
    """
    lo, hi = min(lo, hi), max(lo, hi)
    grezzi = []
    for c in ostacoli:
        if verticale:
            a, b2, c1, c2 = c.y, c.y + c.h, c.x, c.x + c.w
        else:
            a, b2, c1, c2 = c.x, c.x + c.w, c.y, c.y + c.h
        if a < hi + _SPIRAGLIO and lo - _SPIRAGLIO < b2:
            grezzi.append((c1 - _SPIRAGLIO, c2 + _SPIRAGLIO))
    grezzi.sort()
    uniti: List[Tuple[float, float]] = []
    for a, b2 in grezzi:
        if uniti and a <= uniti[-1][1]:
            uniti[-1] = (uniti[-1][0], max(uniti[-1][1], b2))
        else:
            uniti.append((a, b2))
    return uniti


def _spiraglio(blocchi: Sequence[Tuple[float, float]],
               preferito: float) -> List[float]:
    """Le posizioni libere più vicine a ``preferito``, fuori dai blocchi.

    Il posto preferito quando è già libero; altrimenti i due bordi del
    blocco che lo contiene — passo a sinistra o passo a destra, le due
    scelte che un disegnatore farebbe a mano.

    Due e non più: camminare in fuori di blocco in blocco è stato provato
    e non ha tolto **nessun** attraversamento in più (424 su una matrice
    casuale da 400 unità, identici), mentre costava il 66% di tempo. Dove
    due bordi non bastano non c'è corsia libera affatto, e cercarla più in
    là non la fa esistere.
    """
    for a, b2 in blocchi:
        if a <= preferito <= b2:
            return [a, b2]
    return [preferito]


def _route(a: Box, b: Box, simmetrica: bool,
           scarto: float = 0.0,
           ostacoli: Sequence[Box] = (),
           griglia: Optional["_Griglia"] = None,
           esclusi: Sequence[str] = ()) -> List[Tuple[float, float]]:
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
    def costa(punti, limite=1):
        """Quanto attraversa una candidata. Gli ostacoli li dà la griglia
        quando c'è: guardare mille caselle per ogni tratto costa tredici
        secondi sul database Ventena, guardare quelle vicine meno di uno."""
        vicini = (griglia.intorno(punti, esclusi) if griglia is not None
                  else ostacoli)
        return attraversa(punti, vicini, limite=limite)

    if abs(p[0] - q[0]) < 0.5 and not scarto:
        diretto = [p, q]
        if not costa(diretto):
            return diretto
    passo = -_STACCO if allinsu else _STACCO
    giu = p[1] + passo
    if (allinsu and giu < q[1]) or (not allinsu and giu > q[1]):
        giu = (p[1] + q[1]) / 2
    x = q[0] + scarto

    def spezzata(quota):
        return [p, (p[0], quota), (x, quota), q]

    preferita = spezzata(giu)
    if griglia is None and not ostacoli:
        return preferita            # nessuno da scansare
    costo_preferita = costa(preferita)
    if not costo_preferita:
        return preferita

    # La corsia di prima passa dentro una casella di qualcun altro.
    #
    # Si sposta la **linea**, non il nodo: le colonne portano l'ordine
    # stratigrafico e la fascia porta l'epoca, quindi muovere una casella
    # per far passare una freccia rompe proprio la cosa che la matrice
    # dice. Una corsia libera dice la stessa relazione senza toccare
    # niente.
    #
    # Lo spiraglio si **calcola**: si guarda chi occupa la fascia che la
    # linea deve attraversare e si prende il bordo libero più vicino.
    # Provare venti candidati e misurarli costava più di un minuto su
    # quattrocento unità.
    migliore, suo_costo = preferita, costo_preferita

    def vicini(y1, y2, x1, x2):
        return (griglia.nella_fascia(y1, y2, x1, x2, esclusi)
                if griglia is not None else ostacoli)

    # 1. La corsa di lato, a una quota libera.
    corsa = vicini(min(p[1], q[1]) - 40.0, max(p[1], q[1]) + 40.0,
                   min(p[0], x), max(p[0], x))
    for quota in _spiraglio(_blocchi(corsa, p[0], x, verticale=False), giu):
        candidata = spezzata(quota)
        c = costa(candidata)
        if c < suo_costo:
            migliore, suo_costo = candidata, c
        if not suo_costo:
            return migliore

    # 2. L'ingresso di fianco: si scende in una corsia verticale libera
    #    accanto alla colonna d'arrivo e si entra nella casella dal suo
    #    lato. Serve quando la colonna d'arrivo è occupata **sopra** la
    #    casella — una US in mezzo a una pila — e nessuna quota può
    #    aiutare, perché la discesa finale passerebbe comunque attraverso
    #    chi sta sopra. Una freccia che arriva di fianco è ordinaria nella
    #    matrice di Harris; una che passa sotto a un nodo non lo è.
    meta_b = b.y + b.h / 2.0
    quote = _spiraglio(_blocchi(corsa, p[0], x, verticale=False), giu)
    for quota in quote:
        # Tutta la larghezza, non una finestra: la corsia libera può stare
        # lontano quanto il disegno è largo, e con una finestra di qualche
        # centinaio di pixel `_blocchi` vedeva un pezzo di fila e
        # `_spiraglio` proponeva una corsia che fuori dalla finestra era
        # occupata (su quattrocento unità tornavano gli attraversamenti).
        # È una interrogazione per quota, e le quote sono al massimo due.
        giu_su = vicini(quota, meta_b, -_MOLTO, _MOLTO)
        corsie = _spiraglio(_blocchi(giu_su, quota, meta_b, verticale=True),
                            b.x + b.w / 2.0)
        for corsia in sorted(corsie, key=lambda v: abs(v - (b.x + b.w / 2.0))):
            entrata = b.x + b.w if corsia > b.x + b.w / 2.0 else b.x
            punti = [p, (p[0], quota), (corsia, quota),
                     (corsia, meta_b), (entrata, meta_b)]
            c = costa(punti)
            if c < suo_costo:
                migliore, suo_costo = punti, c
            if not suo_costo:
                return migliore
    return migliore

    meta_b = b.y + b.h / 2.0
    for quota in sorted(set([giu] + (vicine or corridoi)),
                        key=lambda c: abs(c - giu))[:8]:
        for corsia in _corsie_verticali(b, ostacoli):
            entrata = b.x + b.w if corsia > b.x + b.w / 2.0 else b.x
            punti = [p, (p[0], quota), (corsia, quota),
                     (corsia, meta_b), (entrata, meta_b)]
            costo = attraversa(punti, ostacoli)
            if costo < suo_costo:
                migliore, suo_costo = punti, costo
                if not costo:
                    return migliore
    return migliore


def _anno(valore: float) -> str:
    anno = int(round(valore))
    return "%d a.C." % abs(anno) if anno < 0 else "%d" % anno
