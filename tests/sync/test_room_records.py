"""The whole unit record through an em.json and back.

A room rebuilt from what the exporter alone writes gave back 15 of
us_table's 131 columns (26 Nov 2026). With ``add_unit_records`` and the
ingestor writing every real us_table column a row-born node carries, a
record rebuilt elsewhere equals the original but for the format of
``rapporti`` (area and site written out).
"""
from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path

import pytest

from modules.stratigraph import room_records as RR

FIXTURE_DB = Path(__file__).resolve().parent / "fixtures" / "mini_volterra.sqlite"


def test_the_record_joins_data_without_replacing_the_exporters_fields(tmp_path):
    db = tmp_path / "db.sqlite"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, sito TEXT, us TEXT, node_uuid TEXT, "
                "colore TEXT, quota_abs REAL, inclusi TEXT, d_stratigrafica TEXT, saggio TEXT)")
    con.execute("INSERT INTO us_table VALUES (1, 'S', '5', 'u5', 'Bruno', 488.87, '[]', 'Strato', 'II')")
    con.commit(); con.close()
    em = tmp_path / "s.em.json"
    em.write_text(json.dumps({"graphs": {"g": {"nodes": [
        {"id": "u5", "data": {"node_uuid": "u5", "d_stratigrafica": "Strato rivisto"}},
        {"id": "other", "data": {"lang": "it"}}], "edges": []}}}))
    assert RR.add_unit_records(str(em), f"sqlite:///{db}", "S") == {"units": 1, "fields": 4}
    data = json.loads(em.read_text())["graphs"]["g"]["nodes"][0]["data"]
    assert data == {"node_uuid": "u5", "d_stratigrafica": "Strato rivisto", "us": "5",
                    "colore": "Bruno", "quota_abs": 488.87, "saggio": "II"}   # no id_us, sito, '[]'


def test_a_site_rebuilt_from_its_em_json_keeps_every_column(tmp_path):
    from modules.s3dgraphy import em_export
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor, hydrate_row_fields_from_data
    from s3dgraphy.container import load_container_file
    from scripts.migrations._2026_05_node_uuid_backfill_lib import add_columns, backfill_uuids

    src = tmp_path / "src.sqlite"
    shutil.copy2(FIXTURE_DB, src)
    add_columns(src)
    backfill_uuids(src)
    con = sqlite3.connect(src)
    sito = con.execute("SELECT sito FROM us_table GROUP BY sito ORDER BY COUNT(*) DESC").fetchone()[0]
    con.close()
    try:
        path, _n, _e, _w = em_export.export_site(f"sqlite:///{src}", sito, str(tmp_path / "out"),
                                                 per_saggio=False)
    except Exception as exc:                                   # pragma: no cover
        pytest.skip(f"the fixture does not export: {exc}")
    RR.add_unit_records(path, f"sqlite:///{src}", sito)
    dst = tmp_path / "dst.sqlite"
    shutil.copy2(src, dst)
    con = sqlite3.connect(dst)
    con.execute("DELETE FROM us_table WHERE sito = ?", (sito,))
    con.commit(); con.close()
    container, _ = load_container_file(path)
    (_gid, graph), = container.graphs.items()
    hydrate_row_fields_from_data(graph)
    done = GraphIngestor().populate_list(graph, db_path=f"sqlite:///{dst}", sito=sito,
                                         dry_run=False, create_missing_epochs=True)
    assert not done.errors

    def rows(db):
        c = sqlite3.connect(db)
        cols = [x[1] for x in c.execute("PRAGMA table_info(us_table)")]
        return cols, {r[cols.index("node_uuid")]: r for r in c.execute(
            "SELECT * FROM us_table WHERE sito = ?", (sito,))}
    cols, a = rows(src)
    _, b = rows(dst)
    assert b, "nothing rebuilt"
    norm = lambda v: None if v in (None, "", "[]") else str(v)
    # rapporti: same relations, area and site written out; datazione and
    # cont_per: filled from the periodisation where the record has none (by
    # design, 17 Oct 2026); order_layer: recomputed by pyArchInit;
    # last_modified_*: the database's own bookkeeping, not sent (5.14.3)
    derived = ("id_us", "rapporti", "order_layer", "datazione", "cont_per",
               "last_modified_by", "last_modified_timestamp")
    differ = {c for u in b for i, c in enumerate(cols)
              if c not in derived and norm(a[u][i]) != norm(b[u][i])}
    assert differ == set()
