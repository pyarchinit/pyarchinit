"""The whole pyArchInit record of each unit, in the room.

The exporter writes into a unit's ``data`` the fields the graph needs
(number, type, definitions, periodisation, relations, location). A room
rebuilt from that alone gave back 15 of us_table's 131 columns: description,
interpretation, colour, levels, measures, the masonry fields… were lost
(measured 26 Nov 2026). Here every non-empty column of the unit's row joins
its ``data`` — without replacing what the exporter already wrote — so that
``pull_room`` rebuilds the record whole (the ingestor writes back every key
that is a real us_table column).

Qt-free.
"""
from __future__ import annotations

import datetime
import decimal
import json
from typing import Any, Dict

#: never travel: the local key, and what the graph already carries as identity
_NOT_SENT = frozenset({"id_us", "node_uuid", "sito"})


def _plain(value: Any) -> Any:
    """A JSON value: Decimal → float, dates → ISO text, bytes skipped."""
    if isinstance(value, decimal.Decimal):
        return float(value)
    if isinstance(value, (datetime.date, datetime.datetime, datetime.time)):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray, memoryview)):
        return None
    return value


def add_unit_records(em_json: str, connection_url: str, site: str) -> Dict[str, int]:
    """Fill the units' ``data`` in the exported em.json, in place."""
    from sqlalchemy import create_engine, text

    with open(em_json, encoding="utf-8") as fh:
        doc = json.load(fh)
    graphs = doc.get("graphs") or {}
    graphs = list(graphs.values()) if isinstance(graphs, dict) else list(graphs)
    with create_engine(connection_url).connect() as conn:
        result = conn.execute(text("SELECT * FROM us_table WHERE sito = :s"), {"s": site})
        keys = list(result.keys())
        rows = {str(r[keys.index("node_uuid")]): dict(zip(keys, r)) for r in result
                if r[keys.index("node_uuid")]}
    report = {"units": 0, "fields": 0}
    for graph in graphs:
        for node in graph.get("nodes") or []:
            data = node.get("data")
            if not isinstance(data, dict):
                continue
            row = rows.get(str(data.get("node_uuid") or ""))
            if row is None:
                continue
            added = 0
            for col, value in row.items():
                if col in _NOT_SENT or col in data:
                    continue
                value = _plain(value)
                if value in (None, "", "[]"):
                    continue
                data[col] = value
                added += 1
            report["units"] += 1
            report["fields"] += added
    with open(em_json, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False)
    return report
