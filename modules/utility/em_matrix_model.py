"""Quello che serve per disegnare la matrice, letto da un em.json.

Il pannello della matrice parte dal **file**, non dal grafo in memoria:
così quello che l'archeologo vede dentro QGIS è esattamente quello che
viaggia nell'em.json e che aprirebbe EMStudio. Se il file è sbagliato si
vede subito, invece di scoprirlo altrove.

Forma e colori di ogni tipo di nodo vengono dalle regole visive della
libreria (``ext_libs/s3dgraphy/JSON_config/em_visual_rules.json``), che
sono la simbologia canonica dell'Extended Matrix: una tabella nostra
prima o poi divergerebbe da quella di EMStudio.

Questo modulo non importa Qt: si prova headless, e la vista disegna
quello che l'impaginatore decide a partire da qui.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

#: I tipi di arco che sono rapporti stratigrafici, cioè le frecce della
#: matrice. Tutto il resto (proprietà, documentazione, aree, autori,
#: epoche) descrive l'unità, non la sua posizione nella sequenza.
STRATIGRAPHIC_KINDS = frozenset({
    "overlies", "covers", "cuts", "fills", "abuts", "leans_on",
    "is_after", "equals", "bonded_to", "has_same_time",
    "is_physically_equal_to", "is_bonded_to", "generic_connection",
    "extracted_from", "combines", "has_data_provenance", "contrasts_with",
    "changed_from",
})

#: L'arco che dice in quale epoca è nata l'unità.
FIRST_EPOCH_KIND = "has_first_epoch"

#: I nostri ``node_type`` contro le sigle di em_visual_rules.json.
_STYLE_ALIASES = {
    "document": "DOC", "extractor": "EXT", "combiner": "COMB",
    "property": "PROP", "EpochNode": "EP", "author": "AUTH",
    "geo_position": "GEO",
}

#: I tipi che non sono unità da disegnare come caselle della matrice.
_NOT_A_UNIT = frozenset({
    "EpochNode", "LocationNodeGroup", "ActivityNodeGroup",
    "ParadataNodeGroup", "TimeBranchNodeGroup",
    "RepresentationModelNodeGroup", "geo_position", "author", "GraphNode",
})


@dataclass(frozen=True)
class Style:
    """Come si disegna un tipo di nodo."""
    shape: str
    fill: str
    stroke: str
    dash: str = "solid"
    width: float = 2.0


#: Quando il tipo non è in tabella: un rettangolo neutro, mai un'eccezione.
_FALLBACK = Style(shape="rectangle", fill="#FFFFFF", stroke="#8C8C8C")

_RULES_CACHE: Dict[str, Style] = {}


def _rules_path() -> Path:
    return (Path(__file__).resolve().parents[2] / "ext_libs" / "s3dgraphy"
            / "JSON_config" / "em_visual_rules.json")


def _load_rules() -> Dict[str, Style]:
    if _RULES_CACHE:
        return _RULES_CACHE
    try:
        raw = json.loads(_rules_path().read_text(encoding="utf-8"))
        styles = raw.get("node_styles") or {}
    except Exception:                               # noqa: BLE001
        styles = {}                                 # senza regole si disegna lo stesso
    for tipo, blocco in styles.items():
        s = (blocco or {}).get("style") or {}
        if not s.get("shape"):
            continue
        _RULES_CACHE[tipo] = Style(
            shape=str(s.get("shape")),
            fill=str(s.get("fill_color") or _FALLBACK.fill),
            stroke=str(s.get("border_color") or _FALLBACK.stroke),
            dash=str(s.get("border_style") or "solid"),
            width=float(s.get("border_width") or 2.0),
        )
    return _RULES_CACHE


def style_for(node_type: str) -> Style:
    """Forma e colori del tipo, o il ripiego neutro se non si sa."""
    rules = _load_rules()
    chiave = _STYLE_ALIASES.get(node_type, node_type)
    return rules.get(chiave) or rules.get(node_type) or _FALLBACK


@dataclass(frozen=True)
class Unit:
    node_id: str
    label: str
    node_type: str
    epoch_id: Optional[str]
    description: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    @property
    def style(self) -> Style:
        return style_for(self.node_type)


@dataclass(frozen=True)
class Epoch:
    node_id: str
    name: str
    start: float
    end: float
    color: str = "#F5F5F5"


@dataclass(frozen=True)
class Relation:
    source: str
    target: str
    kind: str


@dataclass
class MatrixModel:
    units: List[Unit]
    epochs: List[Epoch]
    relations: List[Relation]
    title: str = ""
    warnings: List[str] = field(default_factory=list)

    def unit_by_id(self) -> Dict[str, Unit]:
        return {u.node_id: u for u in self.units}


def _ends(edge) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    return (edge.get("source") or edge.get("edge_source"),
            edge.get("target") or edge.get("edge_target"),
            edge.get("type") or edge.get("edge_type"))


def read_em_json(source) -> MatrixModel:
    """Il modello della matrice da un em.json (percorso o dizionario).

    Solleva ``ValueError`` se il file non si legge o non è un em.json:
    chi chiama lo dice all'utente in una frase.
    """
    if isinstance(source, dict):
        raw = source
        titolo = ""
    else:
        percorso = Path(source)
        try:
            raw = json.loads(percorso.read_text(encoding="utf-8"))
        except Exception as e:                      # noqa: BLE001
            raise ValueError(
                "«%s» non si legge come em.json: %s" % (percorso.name, e)
            ) from e
        titolo = percorso.stem
    grafi = raw.get("graphs") if isinstance(raw, dict) else None
    if not isinstance(grafi, dict) or not grafi:
        raise ValueError("Il file non è un em.json: manca la sezione «graphs».")
    attivo = raw.get("active_graph_id")
    grafo = grafi.get(attivo) or list(grafi.values())[0]
    titolo = str(attivo or titolo or "")

    nodi = grafo.get("nodes") or []
    archi = grafo.get("edges") or []

    epoche: List[Epoch] = []
    unita_grezze: Dict[str, Dict[str, Any]] = {}
    for n in nodi:
        tipo = str(n.get("node_type") or "")
        dati = n.get("data") or {}
        if tipo == "EpochNode":
            epoche.append(Epoch(
                node_id=str(n.get("id")),
                name=str(n.get("name") or "epoca"),
                start=float(dati.get("start_time") or 0.0),
                end=float(dati.get("end_time") or 0.0),
                color=str(dati.get("color") or "#F5F5F5")))
        elif tipo not in _NOT_A_UNIT:
            unita_grezze[str(n.get("id"))] = n

    prima_epoca: Dict[str, str] = {}
    relazioni: List[Relation] = []
    id_epoche = {e.node_id for e in epoche}
    for e in archi:
        s, t, k = _ends(e)
        if not s or not t or not k:
            continue
        if k == FIRST_EPOCH_KIND and t in id_epoche:
            prima_epoca.setdefault(s, t)
        elif k in STRATIGRAPHIC_KINDS and s in unita_grezze and t in unita_grezze:
            relazioni.append(Relation(source=s, target=t, kind=k))

    # Si disegna chi è una riga della scheda (``data.us``) o chi partecipa
    # a un rapporto: un documento appeso a una US con «has_documentation»
    # è decorazione della scheda, non un nodo della matrice. Senza questa
    # stretta le cinque voci di spunta del sito di esempio (Fotografie,
    # Planimetrie…) comparirebbero fra le unità.
    in_relazione = {r.source for r in relazioni} | {r.target for r in relazioni}
    unita = [
        Unit(node_id=i,
             label=str(n.get("name") or i),
             node_type=str(n.get("node_type") or ""),
             epoch_id=prima_epoca.get(i),
             description=str(n.get("description") or ""),
             data=dict(n.get("data") or {}))
        for i, n in unita_grezze.items()
        if (n.get("data") or {}).get("us") or i in in_relazione
    ]
    # Le fasce si leggono dall'alto come la stratigrafia: la più recente
    # in cima, come fanno EMStudio e la matrice di pyArchInit.
    epoche.sort(key=lambda e: (e.start, e.end), reverse=True)
    return MatrixModel(units=unita, epochs=epoche, relations=relazioni,
                       title=titolo)
