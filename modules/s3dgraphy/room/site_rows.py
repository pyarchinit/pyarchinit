"""us_table → righe per l'adapter. SQLAlchemy, un sito per consegna.

I rapporti si leggono dalla colonna TESTUALE ``us_table.rapporti`` con
``s3dgraphy.rapporti.parse_rapporti`` — il client mini li prendeva da una
tabella a interi e un'unità «12a» non poteva essere citata; da noi può.
``parse_rapporti`` dà ``(edge_type, target_us, area, sito, swap)`` già nelle
grafie canoniche, vecchie comprese.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

#: le colonne che l'adapter legge (UNIT_FIELDS + identità + rapporti)
_COLUMNS = ("sito", "area", "us", "unita_tipo", "rapporti",
            "d_stratigrafica", "d_interpretativa", "descrizione",
            "interpretazione", "periodo_iniziale", "fase_iniziale",
            "periodo_finale", "fase_finale", "anno_scavo", "scavato")


def load(conn_str: str, sito: str) -> Tuple[List[Dict[str, Any]],
                                            List[Dict[str, Any]],
                                            List[str]]:
    from sqlalchemy import create_engine, text

    from s3dgraphy.rapporti import parse_rapporti

    engine = create_engine(conn_str)
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(
                "SELECT %s FROM us_table WHERE sito = :s"
                % ", ".join(_COLUMNS)), {"s": sito}).fetchall()
    finally:
        engine.dispose()

    units: List[Dict[str, Any]] = []
    relationships: List[Dict[str, Any]] = []
    problems: List[str] = []
    for row in rows:
        unit = dict(zip(_COLUMNS, row))
        units.append(unit)
        raw = unit.get("rapporti")
        if not raw:
            continue
        entries = _entries(raw)
        if entries is None:
            problems.append(
                "US %s/%s/%s: colonna rapporti illeggibile (%.60r)"
                % (unit["sito"], unit["area"], unit["us"], raw))
            continue
        # UNA voce per volta: parse_rapporti scarta ciò che non riconosce
        # e uno zip su liste di lunghezza diversa disallineerebbe la
        # «parola dell'archeologo» (pinnato dal test del verbo inventato).
        for entry in entries:
            try:
                parsed = parse_rapporti([entry])
            except Exception:
                parsed = []
            if not parsed:
                problems.append(
                    "US %s/%s/%s: rapporto non riconosciuto %r"
                    % (unit["sito"], unit["area"], unit["us"],
                       str(entry[0]).strip()))
                continue
            edge_type, target_us, area, t_sito, swap = parsed[0]
            relationships.append({
                "sito": unit["sito"], "area": unit["area"], "us": unit["us"],
                "edge_type": edge_type, "target_us": target_us,
                "target_area": area, "target_sito": t_sito or unit["sito"],
                "swap": swap, "verb": str(entry[0]).strip(),
            })
    return units, relationships, problems


def _entries(raw):
    """Le voci grezze (primo campo non vuoto), o None = colonna illeggibile."""
    import ast
    import json
    try:
        entries = json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        try:
            entries = ast.literal_eval(raw)
        except Exception:
            return None
    return [e for e in entries or []
            if isinstance(e, (list, tuple)) and e
            and str(e[0] or "").strip()]
