"""Checks before a site meets a room.

**Same number, different type** (s3dgraphy#40). pyArchInit's ``rapporti``
name the target unit as ``[type, us, area, site]`` — no ``unita_tipo`` — while
``us_table`` allows two units with the same number in the same area when
their types differ (UNIQUE is ``(sito, area, us, unita_tipo)``). When that
happens, a rapporto towards that number is ambiguous: the projection links it
to BOTH units and one of them borrows the other's epoch (measured on the
sample site with a ``US 900`` next to a ``Combinar 900``). Until s3dgraphy
decides how to choose, pyArchInit says so before sending, and which records'
rapporti point at the ambiguous number.

Qt-free.
"""
from __future__ import annotations

import ast
from collections import defaultdict
from typing import Any, Dict, List


def ambiguous_numbers(connection_url: str, site: str) -> List[Dict[str, Any]]:
    """``[{area, us, types: [...], referenced_by: [«type us», ...]}]``."""
    from sqlalchemy import create_engine, text
    with create_engine(connection_url).connect() as conn:
        rows = conn.execute(text("SELECT us, area, unita_tipo, rapporti FROM us_table WHERE sito = :s"),
                            {"s": site}).fetchall()
    types = defaultdict(set)
    for us, area, ut, _r in rows:
        types[(str(area or ""), str(us or ""))].add(str(ut or "US"))
    ambiguous = {k: v for k, v in types.items() if len(v) > 1}
    if not ambiguous:
        return []
    refs = defaultdict(list)
    for us, area, ut, rapporti in rows:
        try:
            items = ast.literal_eval(rapporti) if isinstance(rapporti, str) and rapporti.strip() else []
        except (ValueError, SyntaxError):
            continue
        for x in items or []:
            if not isinstance(x, (list, tuple)) or len(x) < 2:
                continue
            t_area = str(x[2]).strip() if len(x) > 2 and str(x[2] or "").strip() else str(area or "")
            t_site = str(x[3]).strip() if len(x) > 3 and str(x[3] or "").strip() else site
            key = (t_area, str(x[1]).strip())
            if t_site == site and key in ambiguous:
                refs[key].append(f"{ut} {us}")
    return [{"area": a, "us": u, "types": sorted(ambiguous[(a, u)]),
             "referenced_by": sorted(set(refs.get((a, u), [])))}
            for a, u in sorted(ambiguous)]
