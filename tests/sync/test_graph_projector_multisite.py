"""A projection is ONE site (I1, one-bridge final review 2026-10-07).

On SQLite the library runs PyArchInitImporter with no site filter and
its post-filter keeps every dev40 node (they carry no attributes['sito']):
projecting one site of a multi-site DB returned every other site's units
too — 210 strat nodes instead of the site's own rows on the sample DB.
The wrapper must prune what the attribute pass did not claim.
"""
from __future__ import annotations

import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

from modules.s3dgraphy.sync.graph_projector import GraphProjector  # noqa: E402

SAMPLE_DB = PLUGIN_ROOT / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
SITO = "Scavo archeologico"


@pytest.fixture
def multisite_db(tmp_path):
    dst = tmp_path / "sample.sqlite"
    shutil.copy2(SAMPLE_DB, dst)
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    add_columns(dst)
    backfill_uuids(dst)
    return dst


def test_projecting_one_site_keeps_only_that_sites_units(multisite_db):
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode
    graph = GraphProjector().populate_graph(multisite_db, sito=SITO)
    strat = [n for n in graph.nodes if isinstance(n, StratigraphicNode)]
    foreign = [n for n in strat
               if (getattr(n, "attributes", None) or {}).get("sito") != SITO]
    assert not foreign, (
        "%d foreign/unclaimed strat nodes, e.g. %s"
        % (len(foreign), [n.name for n in foreign[:5]]))
    conn = sqlite3.connect(multisite_db)
    n_rows = conn.execute(
        "SELECT COUNT(*) FROM us_table WHERE sito=?", (SITO,)).fetchone()[0]
    conn.close()
    assert len(strat) == n_rows


def test_pruning_takes_the_orphans_with_it(multisite_db):
    """Property/epoch/group nodes that only served foreign units must not
    survive as dangling decoration."""
    graph = GraphProjector().populate_graph(multisite_db, sito=SITO)
    ids = {n.node_id for n in graph.nodes}
    for e in graph.edges:
        assert e.edge_source in ids and e.edge_target in ids
    by_type = {}
    for n in graph.nodes:
        by_type.setdefault(type(n).__name__, []).append(n)
    # the sample ships ~10 sites; one site's projection must not carry
    # the whole DB's property cloud (was 1010 pre-fix)
    assert len(by_type.get("PropertyNode", [])) < 300


def test_only_the_sites_epochs_travel(multisite_db):
    """Scoperto da Enzo sul demo (2026-10-07, EMStudio): le unità erano
    filtrate ma le EPOCHE no — 57 epoche in dieci lingue (le
    periodizzazioni degli altri siti) sopravvivevano alla potatura perché
    tengono archi fra sé e le proprie date. L'importer le firma per sito
    (epoch::sito::p::f): quelle d'altri siti non devono viaggiare."""
    import sqlite3
    graph = GraphProjector().populate_graph(multisite_db, sito=SITO)
    epochs = [n for n in graph.nodes if type(n).__name__ == "EpochNode"]
    foreign = [n.node_id for n in epochs
               if str(n.node_id).startswith("epoch::")
               and str(n.node_id).split("::")[1] != SITO]
    assert foreign == [], foreign[:5]
    conn = sqlite3.connect(multisite_db)
    n_periods = conn.execute(
        "SELECT COUNT(DISTINCT periodo || '/' || fase) "
        "FROM periodizzazione_table WHERE sito=?", (SITO,)).fetchone()[0]
    conn.close()
    assert len(epochs) <= n_periods + 2, (
        "%d epoche per %d periodi del sito" % (len(epochs), n_periods))
