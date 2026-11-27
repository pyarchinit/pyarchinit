"""After a pull: the fields pyArchInit computes, computed again.

A pull writes the room into the records; three fields of a record are not
typed by anyone, pyArchInit derives them, and a pull can make them stale:

* ``datazione`` — the dating of the initial (and final) period, from the
  periodisation: ``update_us_dating_from_periodizzazione``;
* ``cont_per`` — the period code: ``update_cont_per`` (quiet: no message box);
* ``order_layer`` — the stratigraphic order, area by area: the same
  computation as the US form's button (``Order_layer_graph.compute``, without
  its progress window).

The same code as the US form, called the same way; nothing reimplemented.
The order uses Qt's event loop: call ``recompute`` on the GUI thread (the room
window does it when the pull has finished).
"""
from __future__ import annotations

from typing import Any, Dict


def recompute(connection_url: str, site: str, *, order: bool = True) -> Dict[str, Any]:
    """``{datazione, cont_per, order_layer: {area: units}, errors}``."""
    from sqlalchemy import text
    from modules.db.pyarchinit_db_manager import Pyarchinit_db_management

    report: Dict[str, Any] = {"datazione": 0, "cont_per": 0, "order_layer": {}, "errors": []}
    db = Pyarchinit_db_management(connection_url)
    db.connection()
    try:
        report["datazione"] = int(db.update_us_dating_from_periodizzazione(site) or 0)
    except Exception as e:  # noqa: BLE001
        report["errors"].append(f"datazione: {e}")
    outcome = db.update_cont_per(site, quiet=True) or {}
    report["cont_per"] = int(outcome.get("updated") or 0)
    report["errors"] += [f"cont_per: {m}" for m in (outcome.get("errors") or [])[:10]]
    if not order:
        return report
    from modules.gis.pyarchinit_pyqgis import Order_layer_graph
    with db.engine.connect() as conn:
        areas = [str(a) for (a,) in conn.execute(
            text("SELECT DISTINCT area FROM us_table WHERE sito = :s AND area IS NOT NULL"), {"s": site})]
    for area in sorted(areas):
        graph = Order_layer_graph(db, site, area)
        levels = graph.compute(reverse_order=True)
        if levels == "error":
            report["errors"].append(f"order_layer: area {area} not computed (see the order log)")
            continue
        report["order_layer"][area] = int(graph.update_database_with_order(db, None, None, site, area) or 0)
    return report
