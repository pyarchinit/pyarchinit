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


def unit_id(sito: Any, area: Any, us: Any) -> str:
    return stable_id(ORIGIN, "us", str(sito or "").strip(),
                     normalize_area(area), str(us or "").strip())


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
    """(node_type, kind, source_code) per una unita_tipo, o (None, …) = skip."""
    if not declared:
        return DEFAULT_UNIT_TYPE, None, None
    if declared in UNIT_TYPES:
        return UNIT_TYPES[declared], None, None
    try:
        from s3dgraphy.nodes.stratigraphic_node import KIND_OF_CODE
        kind = KIND_OF_CODE.get(declared)
    except Exception:
        kind = None
    if kind:
        return "US", kind, declared
    return False, None, None          # sconosciuta: riportata, mai inventata


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
                  delivery: Optional[Delivery] = None) -> Delivery:
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
        node_type, kind, source_code = _resolve_type(declared)
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
        elif declared in UNIT_TYPES and UNIT_TYPES[declared] != declared:
            made.bump("units_remapped_%s_to_%s"
                      % (declared, UNIT_TYPES[declared]))
        made.ops.append({
            "op": "add_node",
            "id": unit_id(sito, row.get("area"), us),
            "node": {
                "node_type": node_type,
                "name": str(us).strip(),
                "description": (row.get("d_stratigrafica") or "").strip() or None,
                "data": _node_data(row, kind, source_code),
            },
        })
        made.bump("units")
    return made
