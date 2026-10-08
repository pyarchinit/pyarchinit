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


@dataclass
class Layout:
    bands: List[Band] = field(default_factory=list)
    boxes: List[Box] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    width: float = 0.0
    height: float = 0.0
    title: str = ""


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

    ordinanti = [(r.source, r.target) for r in model.relations
                 if r.kind not in SYMMETRIC_KINDS
                 and r.source in unita and r.target in unita]
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
    for epoca, dentro in gruppi:
        interni = [(s, t) for s, t in ordinanti if s in dentro and t in dentro]
        livello = _ranks(sorted(dentro), interni)
        per_livello: Dict[int, List[str]] = {}
        for i in sorted(dentro):
            per_livello.setdefault(livello.get(i, 0), []).append(i)
        _order_within_ranks(per_livello, vicini)

        righe = max(per_livello) + 1 if per_livello else 0
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

        for riga, ids in sorted(per_livello.items()):
            colonne_max = max(colonne_max, len(ids))
            for colonna, i in enumerate(ids):
                risultato.boxes.append(Box(
                    unit=unita[i],
                    x=(config.margin + config.band_label_w
                       + colonna * (config.box_w + config.h_gap)),
                    y=y + config.band_pad + riga * (config.box_h + config.v_gap),
                    w=config.box_w, h=config.box_h))
        y += altezza

    centro = {b.unit.node_id: b for b in risultato.boxes}
    for r in model.relations:
        a, b = centro.get(r.source), centro.get(r.target)
        if a is None or b is None:
            continue
        simmetrica = r.kind in SYMMETRIC_KINDS
        risultato.edges.append(Edge(
            kind=r.kind, symmetric=simmetrica,
            points=_route(a, b, simmetrica)))

    risultato.width = max(
        [config.margin * 2 + config.band_label_w
         + colonne_max * (config.box_w + config.h_gap)]
        + [b.x + b.w + config.margin for b in risultato.boxes])
    risultato.height = y + config.margin
    return risultato


def _route(a: Box, b: Box, simmetrica: bool) -> List[Tuple[float, float]]:
    """La spezzata da ``a`` a ``b``: giù, di lato, giù."""
    if simmetrica:
        return [(a.x + a.w, a.y + a.h / 2), (b.x, b.y + b.h / 2)]
    p = (a.x + a.w / 2, a.y + a.h)
    q = (b.x + b.w / 2, b.y)
    if abs(p[0] - q[0]) < 0.5:
        return [p, q]
    mezzo = (p[1] + q[1]) / 2
    return [p, (p[0], mezzo), (q[0], mezzo), q]


def _anno(valore: float) -> str:
    anno = int(round(valore))
    return "%d a.C." % abs(anno) if anno < 0 else "%d" % anno
