"""Le coppie dei disegni ricavati dal 3D non vanno nell'em.json e non si
perdono reimportandolo (spec 2026-10-18, D11)."""
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
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

FIXTURE_DB = PLUGIN_ROOT / "tests" / "sync" / "fixtures" / "mini_volterra.sqlite"
CON_3D = "[['Fotografie', 'Si'], ['Prospetto', '3D-PRO-N']]"


@pytest.fixture
def db(tmp_path):
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    from scripts.migrations._2026_05_node_uuid_backfill_lib import add_columns, backfill_uuids
    add_columns(dst)
    backfill_uuids(dst)
    con = sqlite3.connect(dst)
    sito, id_us = con.execute("SELECT sito, id_us FROM us_table WHERE unita_tipo = 'US' LIMIT 1").fetchone()
    con.execute("UPDATE us_table SET documentazione = ? WHERE id_us = ?", (CON_3D, id_us))
    con.commit()
    con.close()
    return dst, sito, id_us


def test_export_senza_coppie_ricavate_e_reimport_che_le_tiene(db):
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    path, sito, id_us = db
    con = sqlite3.connect(path)
    uuid = con.execute("SELECT node_uuid FROM us_table WHERE id_us = ?", (id_us,)).fetchone()[0]
    con.close()
    grafo = GraphProjector().populate_graph(path, sito=sito)
    nodo = grafo.find_node_by_id(uuid)
    esportato = str((getattr(nodo, "attributes", None) or {}).get("documentazione"))
    assert "3D-PRO-N" not in esportato and "Fotografie" in esportato
    GraphIngestor().populate_list(grafo, path, sito=sito, dry_run=False, create_missing_epochs=True)
    con = sqlite3.connect(path)
    dopo = con.execute("SELECT documentazione FROM us_table WHERE id_us = ?", (id_us,)).fetchone()[0]
    con.close()
    assert "3D-PRO-N" in dopo and "Fotografie" in dopo
