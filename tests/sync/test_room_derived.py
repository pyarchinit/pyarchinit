"""After a pull, the computed fields computed again (room_derived).

Measured on the sample site (27 Nov 2026): the stored values were stale —
period codes «6» where the periodisation says «4», orders never computed —
and the dating doubled («Età contemporanea/Età contemporanea») when the
initial and final period are the same; fixed in
update_us_dating_from_periodizzazione, which the US form uses too.
"""
from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "mini_volterra.sqlite"


def test_dating_period_code_and_order_after_a_pull(tmp_path):
    db = tmp_path / "v.sqlite"
    shutil.copy(FIXTURE, db)
    con = sqlite3.connect(db)
    con.execute("UPDATE periodizzazione_table SET cont_per = '1', datazione_estesa = 'Età A' "
                "WHERE periodo = 1")
    con.execute("UPDATE periodizzazione_table SET cont_per = '2', datazione_estesa = 'Età B' "
                "WHERE periodo = 2")
    con.execute("UPDATE us_table SET periodo_finale = 2, fase_finale = 1 WHERE us = '1'")   # 1.1 → 2.1
    con.execute("UPDATE us_table SET periodo_finale = 1, fase_finale = 1 WHERE us = '2'")   # 1.1 → 1.1
    con.commit()
    con.close()
    from modules.stratigraph.room_derived import recompute
    report = recompute(f"sqlite:///{db}", "TestSite")
    assert report["errors"] == []
    rows = {us: (cp, dat, ol) for us, cp, dat, ol in sqlite3.connect(db).execute(
        "SELECT us, cont_per, datazione, order_layer FROM us_table")}
    assert rows["1"][:2] == ("1/2", "Età A/Età B")
    assert rows["2"][:2] == ("1", "Età A")                         # not «Età A/Età A»
    assert rows["3"][:2] == ("1", "Età A")
    # «1 copre 2», «1 copre 3», «2 copre 3»: 1 is above 2, which is above 3
    assert rows["1"][2] is not None and rows["2"][2] is not None and rows["3"][2] is not None
    assert len({rows["1"][2], rows["2"][2], rows["3"][2]}) == 3
    assert recompute(f"sqlite:///{db}", "TestSite")["datazione"] == 0              # nothing left to change
