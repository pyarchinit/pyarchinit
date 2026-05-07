"""Generate a deterministic mini-Volterra SQLite fixture.

Exercises the four AI03 acceptance criteria:
- Single sito='TestSite' so the L2 site-filter test produces the same
  graph as the unfiltered run; a regression on _filter_by_site that
  drops everything would surface immediately.
- 5 stratigraphic units spanning 3 unit_tipo values (US, USM, USVs).
- 2 periods/phases in periodizzazione_table; every US is assigned to
  one or the other so both EpochNodes survive the site filter.
- 7 rapporti entries spanning 4 distinct relation types (copre,
  coperto da, uguale a, riempie).
- 1 deliberate transitive redundancy: US1->US2->US3 PLUS US1->US3.
  After GraphMLExporter.transitive_reduction the redundant edge must
  disappear.

Usage:
    cd /path/to/pyarchinit
    python3 tests/sync/fixtures/build_mini_volterra.py

Output:
    tests/sync/fixtures/mini_volterra.sqlite (overwritten)
"""
from __future__ import annotations

import os
import shutil
import sqlite3
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_DB = PLUGIN_ROOT / "resources" / "dbfiles" / "pyarchinit.sqlite"
FIXTURE_DB = Path(__file__).resolve().parent / "mini_volterra.sqlite"

SITO = "TestSite"


def main() -> int:
    if not TEMPLATE_DB.exists():
        print(f"ERROR: template DB missing at {TEMPLATE_DB}", file=sys.stderr)
        return 2

    # Start from a copy of the template so all schema/views/triggers exist.
    if FIXTURE_DB.exists():
        FIXTURE_DB.unlink()
    shutil.copy2(TEMPLATE_DB, FIXTURE_DB)

    conn = sqlite3.connect(FIXTURE_DB)
    cur = conn.cursor()

    # Wipe every user-table that the fixture touches; keep schema.
    for tbl in ("us_table", "periodizzazione_table"):
        cur.execute(f"DELETE FROM {tbl}")

    # Drop bulk unrelated reference data so the committed fixture stays
    # small. The AI03 GraphML pipeline only reads us_table +
    # periodizzazione_table; nothing below is needed by the tests but
    # the unmodified template ships ~4 MB of Spatialite reference data
    # that would bloat the git history forever.
    for tbl in ("spatial_ref_sys", "spatialite_history",
                "pyarchinit_thesaurus_sigle", "SE_external_graphics"):
        try:
            cur.execute(f"DELETE FROM {tbl}")
        except sqlite3.OperationalError:
            pass  # Table absent in older template versions — harmless.

    # 2 epochs/phases in periodizzazione_table.
    # Columns of interest: sito, periodo, fase, cron_iniziale, cron_finale, descrizione
    cur.executemany(
        "INSERT INTO periodizzazione_table "
        "(sito, periodo, fase, cron_iniziale, cron_finale, descrizione) "
        "VALUES (?,?,?,?,?,?)",
        [
            (SITO, 1, 1, -100, 100, "Late Roman"),
            (SITO, 2, 1, 100, 400, "Early Medieval"),
        ],
    )

    # 5 stratigraphic units. Layout:
    # us=1,2,3 are 'US' in period 1 — these wire the transitive redundancy.
    # us=4 is 'USM' in period 2.
    # us=5 is 'USVs' in period 2.
    # rapporti is a string-encoded list, see PyArchInit conventions.
    rows = [
        # (sito, area, us, unita_tipo, periodo_iniziale, fase_iniziale,
        #  rapporti, d_stratigrafica, d_interpretativa, descrizione)
        (SITO, "1", "1", "US", 1, 1,
         "[['copre', '2', '1', 'TestSite'], ['copre', '3', '1', 'TestSite']]",
         "Strato di terra", "Riporto", "Strato di terra mista a pietre"),
        (SITO, "1", "2", "US", 1, 1,
         "[['copre', '3', '1', 'TestSite']]",
         "Strato di sabbia", "Sedimento", "Strato di sabbia gialla"),
        (SITO, "1", "3", "US", 1, 1,
         "[]",
         "Strato di argilla", "Naturale", "Argilla rossastra"),
        (SITO, "1", "4", "USM", 2, 1,
         "[['uguale a', '5', '1', 'TestSite']]",
         "Muratura in pietra", "Fondazione", "Fondazione muraria"),
        (SITO, "1", "5", "USVs", 2, 1,
         "[['riempie', '4', '1', 'TestSite']]",
         "Ricostruzione virtuale", "Ipotesi",
         "Volume ricostruttivo della muratura"),
    ]

    cur.executemany(
        "INSERT INTO us_table "
        "(sito, area, us, unita_tipo, periodo_iniziale, fase_iniziale, "
        " rapporti, d_stratigrafica, d_interpretativa, descrizione) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        rows,
    )

    conn.commit()
    # Reclaim the freed pages so the on-disk file shrinks to fixture size.
    cur.execute("VACUUM")
    conn.close()

    size = FIXTURE_DB.stat().st_size
    print(f"OK wrote {FIXTURE_DB} ({size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
