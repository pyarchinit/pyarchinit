"""us_table → operazioni per la stanza. Puro: niente Qt, niente rete, niente DB.

Porting dichiarato di ``pyarchinit_mini/connector/us_ops.py`` (ramo
stratigraph/09-client-stanza), con le differenze NOSTRE scritte qui:

- il vocabolario è quello dev40: USM/USR/USS e i codici localizzati (WSU,
  MSE, …) viaggiano come ``US`` con ``stratigraphic_kind`` in ``data`` e il
  codice d'origine in ``source_code`` (``KIND_OF_CODE`` della libreria);
- USVA/USVB→USVs, USVC→USVn (la stessa mappa della migrazione vocabolario);
- i paradata (DOC, Combinar, Extractor, property, CON) NON diventano nodi
  stratigrafici della stanza: riportati in ``skipped``.

IL PAYLOAD VA DENTRO ``node``: il CRDT legge ``op["node"]`` e un ``node_type``
al top level viene accettato e PERSO in silenzio (misurato da mini,
crdt.py:727). L'id di un arco è ``source__edge_type__target`` — la stessa
convenzione di EMStudio, così l'arco disegnato a mano e il nostro sono UNO.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from s3dgraphy.contract.core import stable_id

ORIGIN = "pyarchinit"

#: unita_tipo → node_type della stanza. I codici-kind (USM, WSU, …) NON
#: stanno qui: li risolve KIND_OF_CODE come US+kind. None = paradata, mai
#: un nodo stratigrafico della stanza.
UNIT_TYPES: Dict[str, Optional[str]] = {
    "US": "US", "SF": "SF", "USD": "USD", "VSF": "VSF", "RSF": "RSF",
    "TSU": "TSU", "UL": "UL",
    "USVs": "USVs", "USVn": "USVn", "USVc": "USVn",
    "USVA": "USVs", "USVB": "USVs", "USVC": "USVn",
    "serSU": "serSU", "serUSVn": "serUSVn", "serUSVs": "serUSVs",
    "DOC": None, "Combinar": None, "Extractor": None, "property": None,
    "CON": None,
}
DEFAULT_UNIT_TYPE = "US"

#: colonna → nome nel ``data`` del nodo (il sottoinsieme che serve a chi
#: ragiona sulla stratigrafia; il resto resta nel database di scavo).
UNIT_FIELDS: Dict[str, str] = {
    "sito": "site", "area": "area", "us": "unit",
    "d_stratigrafica": "stratigraphic_definition",
    "d_interpretativa": "interpretive_definition",
    "descrizione": "description", "interpretazione": "interpretation",
    "periodo_iniziale": "period_start", "fase_iniziale": "phase_start",
    "periodo_finale": "period_end", "fase_finale": "phase_end",
    "anno_scavo": "excavation_year", "scavato": "excavated",
}


def normalize_area(area: Any) -> str:
    return "" if area is None else str(area).strip()


def _sid_part(value: Any) -> str:
    """stable_id unisce le parti con '|': un sito che lo contiene potrebbe
    collidere con un altro ('S|1','2' vs 'S','1|2') — si scappa prima."""
    return str(value).replace("\\", "\\\\").replace("|", "\\|")


def unit_id(sito: Any, area: Any, us: Any) -> str:
    return stable_id(ORIGIN, "us", _sid_part(str(sito or "").strip()),
                     _sid_part(normalize_area(area)),
                     _sid_part(str(us or "").strip()))


def edge_id(source: str, edge_type: str, target: str) -> str:
    return f"{source}__{edge_type}__{target}"


@dataclass
class Delivery:
    ops: List[Dict[str, Any]] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    counts: Dict[str, int] = field(default_factory=dict)

    def bump(self, key: str) -> None:
        self.counts[key] = self.counts.get(key, 0) + 1


def _resolve_type(declared: str):
    """(node_type, kind, source_code, canonicalized) per una unita_tipo,
    o (False, …) = sconosciuta: riportata, mai inventata."""
    if not declared:
        return DEFAULT_UNIT_TYPE, None, None, False
    if declared in UNIT_TYPES:
        return UNIT_TYPES[declared], None, None, False
    try:
        from s3dgraphy.nodes.stratigraphic_node import KIND_OF_CODE
        kind = KIND_OF_CODE.get(declared)
    except Exception:
        kind = None
    if kind:
        return "US", kind, declared, False
    # C2 (review 2026-10-07): le altre lingue scrivono 'US' come SU/SE/UE/ΣΜ
    # — canonical_unita_tipo le conosce già; senza questo passo un DB non
    # italiano perdeva ~80% delle unità.
    try:
        from s3dgraphy.rapporti import canonical_unita_tipo
        canonical = canonical_unita_tipo(declared)
    except Exception:
        canonical = declared
    if canonical != declared and canonical in UNIT_TYPES \
            and UNIT_TYPES[canonical]:
        return UNIT_TYPES[canonical], None, None, True
    return False, None, None, False


def _node_data(row: Dict[str, Any], kind, source_code) -> Dict[str, Any]:
    kept: Dict[str, Any] = {}
    for column, name in UNIT_FIELDS.items():
        value = row.get(column)
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        kept[name] = value.strip() if isinstance(value, str) else value
    if kind:
        kept["stratigraphic_kind"] = kind
        kept["source_code"] = source_code
    kept["origin"] = ORIGIN
    return kept


def ops_for_units(units: Iterable[Dict[str, Any]],
                  delivery: Optional[Delivery] = None,
                  lang: Optional[str] = None) -> Delivery:
    made = delivery if delivery is not None else Delivery()
    for row in units:
        sito, us = row.get("sito"), row.get("us")
        if not str(sito or "").strip() or not str(us or "").strip():
            made.skipped.append(
                "riga con sito=%r e us=%r: senza sito o numero una unità "
                "non è identificabile" % (sito, us))
            made.bump("units_unidentifiable")
            continue
        declared = str(row.get("unita_tipo") or "").strip()
        node_type, kind, source_code, canonicalized = _resolve_type(declared)
        if node_type is None:
            made.skipped.append(
                "%s/%s/%s: %r è paradata, non una unità della stanza"
                % (sito, normalize_area(row.get("area")), us, declared))
            made.bump("units_paradata_%s" % declared)
            continue
        if node_type is False:
            made.skipped.append(
                "%s/%s/%s: unita_tipo=%r senza corrispondente nel datamodel "
                "— lasciata fuori, mai approssimata"
                % (sito, normalize_area(row.get("area")), us, declared))
            made.bump("units_unmappable_type_%s" % declared)
            continue
        if not declared:
            made.bump("units_typed_by_default")
        elif canonicalized:
            made.bump("units_canonicalized_%s" % declared)
        elif declared in UNIT_TYPES and UNIT_TYPES[declared] != declared:
            made.bump("units_remapped_%s_to_%s"
                      % (declared, UNIT_TYPES[declared]))
        data = _node_data(row, kind, source_code)
        # dev40, decisione 12: la lingua di un nodo testuale viaggia
        # NELL'operazione e la decide il produttore; 'und' = non nota.
        data["lang"] = (lang or "und").strip() or "und"
        made.ops.append(_make_op(
            "add_node",
            id=unit_id(sito, row.get("area"), us),
            node={
                "node_type": node_type,
                "name": str(us).strip(),
                "description": (row.get("d_stratigrafica") or "").strip() or None,
                "data": data,
            },
        ))
        made.bump("units")
    return made


def _make_op(kind, **fields):
    """Il costruttore del contratto (crdt.make_op): valida — p.es. rifiuta un
    add_node testuale senza data.lang — e non scrive mai author/ts."""
    try:
        from s3dgraphy.crdt import make_op
        return make_op(kind, **fields)
    except ImportError:
        out = {"op": kind}
        out.update(fields)
        return out


SYMMETRIC = {"equals", "bonded_to", "has_same_time",
             "is_physically_equal_to", "is_bonded_to"}

#: parse_rapporti dà il verbo inverso come TIPO inverso (Coperto da →
#: is_overlain_by, swap=False — misurato): senza questa piega la coppia
#: reciproca diventa DUE archi nella stanza condivisa, per sempre (C1,
#: review 2026-10-07: 81 doppi sul solo sito campione).
INVERSE_TO_FORWARD = {
    "is_overlain_by": "overlies",
    "is_cut_by": "cuts",
    "is_filled_by": "fills",
    "is_abutted_by": "abuts",
    "is_leaned_on_by": "leans_on",
    "is_before": "is_after",
}


def _resolve_target(rel, known):
    """L'id del target, o (None, perché)."""
    sito = str(rel.get("target_sito") or rel.get("sito") or "").strip()
    area = normalize_area(rel.get("target_area"))
    us = str(rel.get("target_us") or "").strip()
    if area:
        hit = known.get((sito, area, us))
        return (hit, None) if hit else (
            None, "unità %s/%s/%s non consegnata" % (sito, area, us))
    hits = [v for (s, _a, u), v in known.items() if s == sito and u == us]
    if len(hits) == 1:
        return hits[0], None
    if not hits:
        return None, "unità %s/?/%s non consegnata" % (sito, us)
    return None, ("il numero %s/%s è ambiguo fra %d aree: il rapporto non "
                  "dice quale" % (sito, us, len(hits)))


def ops_for_relationships(relationships, known, delivery=None):
    """`add_edge` per ogni rapporto risolvibile, UNA volta per relazione.

    La coppia inversa (1 Copre 2 / 2 Coperto da 1) produce lo stesso arco
    orientato: dedup per ``edge_id``. Le simmetriche (equals, bonded_to…)
    viaggiano con gli estremi in ordine lessicografico, così la stessa
    relazione scritta dai due lati è UN arco.
    """
    made = delivery if delivery is not None else Delivery()
    seen = set()
    for rel in relationships:
        src = known.get((str(rel.get("sito") or "").strip(),
                         normalize_area(rel.get("area")),
                         str(rel.get("us") or "").strip()))
        if not src:
            made.skipped.append(
                "rapporto da %s/%s/%s: la riga stessa non è stata consegnata"
                % (rel.get("sito"), rel.get("area"), rel.get("us")))
            made.bump("edges_source_missing")
            continue
        dst, why = _resolve_target(rel, known)
        if not dst:
            made.skipped.append("rapporto %r di %s/%s/%s: %s"
                                % (rel.get("verb"), rel.get("sito"),
                                   rel.get("area"), rel.get("us"), why))
            made.bump("edges_unresolved")
            continue
        edge_type = rel["edge_type"]
        swap = bool(rel.get("swap"))
        # la piega degli inversi: stesso arco da qualsiasi lato lo si scriva
        if edge_type in INVERSE_TO_FORWARD:
            edge_type = INVERSE_TO_FORWARD[edge_type]
            swap = not swap
        source, target = (dst, src) if swap else (src, dst)
        if edge_type in SYMMETRIC and target < source:
            source, target = target, source
        eid = edge_id(source, edge_type, target)
        if eid in seen:
            made.bump("edges_deduplicated")
            continue
        seen.add(eid)
        made.ops.append(_make_op(
            "add_edge", id=eid,
            source=source, target=target, edge_type=edge_type,
            attributes={"pyarchinit_relationship": rel.get("verb") or ""},
        ))
        made.bump("edges")
    return made


def deliver(units, relationships=(), lang=None):
    """Tutto il sito in operazioni: prima i nodi, poi gli archi fra loro."""
    units = list(units)
    made = ops_for_units(units, lang=lang)
    known = {(str(r.get("sito") or "").strip(),
              normalize_area(r.get("area")),
              str(r.get("us") or "").strip()):
             unit_id(r.get("sito"), r.get("area"), r.get("us"))
             for r in units
             if str(r.get("sito") or "").strip()
             and str(r.get("us") or "").strip()}
    # solo le unità DIVENTATE nodi possono essere estremi
    delivered = {op["id"] for op in made.ops}
    known = {k: v for k, v in known.items() if v in delivered}
    return ops_for_relationships(relationships, known, made)
