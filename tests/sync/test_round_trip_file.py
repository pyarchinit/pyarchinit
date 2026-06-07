"""File round-trip invariants — the bug behind 'import azzera le US'.

The in-memory round-trip (test_round_trip.py) keeps every node attribute
because GraphProjector sets them directly. The REAL user workflow is a
*file* round-trip:

    DB -> GraphProjector -> graphml_writer (.graphml FILE)
       -> GraphMLImporter.parse() -> GraphIngestor.populate_list -> DB'

Two bugs lived here:

1. **azzera** — importing a graph into a NEW target sito *moved* the
   source rows (``WHERE node_uuid = :uuid`` ignored sito, ``sito`` was
   forced to the target) instead of copying them. The source site was
   emptied.
2. **synthetic pollution** — the export materializes continuity into
   ``_synth_BR_*`` diamond nodes; on reimport they were inserted as bogus
   ``us='_synth_BR_1'`` rows.

The fix (graph_ingestor._resolve_target_row + _is_synthetic_node):
cross-site import COPIES with a fresh node_uuid, same-site import still
UPDATEs in place, and synthetic artifacts are skipped.
"""
from __future__ import annotations
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest
import pandas  # noqa: F401
from lxml import etree as _etree  # noqa: F401

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")


@pytest.fixture
def mini_volterra(tmp_path):
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    add_columns(dst)
    backfill_uuids(dst)
    return dst


def _imp():
    try:
        from s3dgraphy.importer.import_graphml import GraphMLImporter
    except ImportError:
        from s3dgraphy.importer.graphml_importer import GraphMLImporter
    return GraphMLImporter


def _read_sito(db):
    conn = sqlite3.connect(db)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    return sito


def _rows(db, sito):
    conn = sqlite3.connect(db)
    out = {r[0]: dict(zip(("us", "unita_tipo", "area", "rapporti", "node_uuid"), r[1:]))
           for r in conn.execute(
               "SELECT us, us, unita_tipo, area, rapporti, node_uuid "
               "FROM us_table WHERE sito=?", (sito,)).fetchall()}
    conn.close()
    return out


def _export(db, sito, out):
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    export_graphml(db_path=db, mapping="pyarchinit_us_mapping",
                   output_path=out, site_filter=sito)
    return out


def test_same_site_round_trip_no_synthetic_no_loss(tmp_path, mini_volterra):
    """Re-importing a site's own graphml into the SAME site preserves
    every real US and creates NO synthetic / spurious rows."""
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    sito = _read_sito(mini_volterra)
    before = _rows(mini_volterra, sito)
    out = _export(mini_volterra, sito, tmp_path / "e.graphml")

    g = _imp()(filepath=str(out)).parse()
    GraphIngestor().populate_list(g, mini_volterra, sito=sito,
                                  dry_run=False, graphml_path=out)
    after = _rows(mini_volterra, sito)

    # No _synth_BR_* rows leaked into us_table.
    assert not [u for u in after if str(after[u]["us"]).startswith("_synth")]
    # Same set of real US numbers, nothing lost or duplicated.
    assert {r["us"] for r in before.values()} == {r["us"] for r in after.values()}
    assert len(before) == len(after)


def test_import_into_new_sito_copies_not_moves(tmp_path, mini_volterra):
    """THE azzera regression: importing into a NEW sito must COPY, leaving
    the source site fully intact, and give the copies fresh node_uuids."""
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    src = _read_sito(mini_volterra)
    src_before = _rows(mini_volterra, src)
    out = _export(mini_volterra, src, tmp_path / "e.graphml")

    NEW = "NewSite"
    g = _imp()(filepath=str(out)).parse()
    GraphIngestor().populate_list(g, mini_volterra, sito=NEW, dry_run=False,
                                  graphml_path=out, create_missing_epochs=True)

    src_after = _rows(mini_volterra, src)
    new_rows = _rows(mini_volterra, NEW)

    # 1. Source site UNTOUCHED (this is the azzera guard).
    assert set(src_before) == set(src_after), "source site was azzerato/moved"
    assert {r["us"] for r in src_before.values()} == \
           {r["us"] for r in src_after.values()}

    # 2. New site got the real US (and ONLY real US — no synthetics).
    assert not [u for u in new_rows if str(new_rows[u]["us"]).startswith("_synth")]
    assert {r["us"] for r in src_before.values()} == \
           {r["us"] for r in new_rows.values()}

    # 3. Copies have FRESH, independent node_uuids (no cross-site sharing).
    src_uuids = {r["node_uuid"] for r in src_after.values()}
    new_uuids = {r["node_uuid"] for r in new_rows.values()}
    assert src_uuids.isdisjoint(new_uuids), "copy reused source node_uuid"

    # 4. rapporti retargeted to the new sito.
    for r in new_rows.values():
        if r["rapporti"] and r["rapporti"] != "[]":
            assert src not in r["rapporti"], "rapporti still reference source sito"
            assert NEW in r["rapporti"]


def test_import_into_new_sito_is_idempotent(tmp_path, mini_volterra):
    """Importing the same graphml into the same new sito twice must not
    duplicate rows or raise a UNIQUE violation."""
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    src = _read_sito(mini_volterra)
    out = _export(mini_volterra, src, tmp_path / "e.graphml")
    NEW = "NewSite"

    for _ in range(2):
        g = _imp()(filepath=str(out)).parse()
        GraphIngestor().populate_list(g, mini_volterra, sito=NEW,
                                      dry_run=False, graphml_path=out,
                                      create_missing_epochs=True)

    new_rows = _rows(mini_volterra, NEW)
    src_rows = _rows(mini_volterra, src)
    # Exactly one copy per real source US — no duplication on re-import.
    assert len(new_rows) == len(src_rows)
