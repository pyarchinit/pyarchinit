"""Generate the AI04 external-graph test fixtures.

Reads mini_volterra.sqlite, projects it via GraphProjector, then
emits two GraphML files:

1. mini_volterra_external.graphml — projection with one node's
   d_stratigrafica mutated; ingesting this back should produce
   exactly one ConflictRecord and one updated row.

2. mini_volterra_external_with_new_epoch.graphml — projection plus
   one synthetic EpochNode (periodo=99, fase='9.9') NOT in
   periodizzazione_table; used by the create-missing-epochs test.

Run: python tests/sync/fixtures/build_mini_volterra_external.py
Idempotent — re-running produces structurally identical files.

The fixture mini_volterra.sqlite needs the Phase 1 node_uuid
migration applied; this script applies it to a temp copy so the
on-disk fixture stays unchanged.
"""
from __future__ import annotations
import shutil
import sys
import tempfile
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
# Ensure plugin root is on path so `modules.*` resolves.
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))
# Pre-import system pandas / lxml BEFORE ext_libs goes on sys.path,
# so the bundled (often platform-mismatched) pandas in ext_libs does
# not shadow the working system pandas.
import pandas  # noqa: F401
from lxml import etree as _etree  # noqa: F401
# Now make ext_libs available so `s3dgraphy` (vendored) resolves.
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

from modules.s3dgraphy.sync.graph_projector import GraphProjector

FIX = PLUGIN_ROOT / "tests" / "sync" / "fixtures"
SRC = FIX / "mini_volterra.sqlite"


def _migrated_copy() -> Path:
    """Copy SRC to a tmp path with the Phase 1 node_uuid migration applied."""
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    tmp = Path(tempfile.mkdtemp()) / "mini_volterra.sqlite"
    shutil.copy2(SRC, tmp)
    add_columns(tmp)
    backfill_uuids(tmp)
    return tmp


def _write_graphml(graph, out: Path) -> None:
    """Serialise via s3dgraphy GraphMLExporter, then run the
    _embed_pyarchinit_data_keys post-processor so the fixture
    carries the data keys AI04 import can recover."""
    from s3dgraphy.exporter.graphml.graphml_exporter import GraphMLExporter
    from modules.s3dgraphy.sync.graphml_writer import (
        _embed_pyarchinit_data_keys)
    exporter = GraphMLExporter(graph)
    exporter.export(str(out), persist_auxiliary=False)
    _embed_pyarchinit_data_keys(graph, out)


def main() -> int:
    import sqlite3
    db = _migrated_copy()
    conn = sqlite3.connect(db)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()

    p = GraphProjector()

    # 1. base external graph (mutate one d_stratigrafica)
    graph = p.populate_graph(db, sito=sito)
    for n in graph.nodes:
        attrs = getattr(n, "attributes", None) or {}
        if attrs.get("us"):
            attrs["d_stratigrafica"] = "EXT_GRAPH_VALUE"
            break
    _write_graphml(graph, FIX / "mini_volterra_external.graphml")
    print("OK — mini_volterra_external.graphml written")

    # 2. external with new epoch
    graph2 = p.populate_graph(db, sito=sito)
    from s3dgraphy.nodes.epoch_node import EpochNode
    e = EpochNode(node_id="epoch_99_9_9_synthetic",
                  name="Synthetic Period 99 Phase 9.9",
                  start_time=0.0, end_time=0.0)
    e.attributes = {"periodo": 99, "fase": "9.9"}
    graph2.add_node(e)
    _write_graphml(graph2,
                   FIX / "mini_volterra_external_with_new_epoch.graphml")
    print("OK — mini_volterra_external_with_new_epoch.graphml written")

    # 3. pre-cooked paradata fixture
    _emit_paradata_fixture()

    # 4. pre-cooked groups fixture
    _emit_groups_fixture()
    return 0


def _emit_paradata_fixture():
    """Generate paradata_volterra.graphml — pre-cooked Author/License/Embargo
    fixture used by AI05 round-trip tests."""
    import sqlite3
    import shutil
    import tempfile
    from pathlib import Path

    PLUGIN_ROOT = Path(__file__).resolve().parents[3]
    SRC_DB = PLUGIN_ROOT / "tests" / "sync" / "fixtures" / "mini_volterra.sqlite"

    # Apply Phase 1 migration to a tmp copy so ParadataStore has a valid DB.
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids,
    )
    tmp_db = Path(tempfile.mkdtemp()) / "mini_volterra.sqlite"
    shutil.copy2(SRC_DB, tmp_db)
    add_columns(tmp_db); backfill_uuids(tmp_db)

    sito = sqlite3.connect(tmp_db).execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]

    # Use ParadataStore to seed the file with controlled UUIDs.
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(tmp_db, sito)
    store.add_author("Marco Pacifico", orcid="0000-0002-1234-5678",
                     role="curator")
    store.add_author("Maria Bianchi", orcid="0000-0001-9876-5432",
                     role="contributor")
    store.add_license("CC-BY-NC-4.0",
                      url="https://creativecommons.org/licenses/by-nc/4.0/")
    store.add_embargo("2030-12-31", reason="Volterra dataset embargo")

    # Copy the generated file into the fixtures directory under a
    # canonical name (the slug-based name depends on sito; we use a
    # site-agnostic filename for the test fixture).
    out = PLUGIN_ROOT / "tests" / "sync" / "fixtures" / "paradata_volterra.graphml"
    shutil.copy2(store.file_path, out)
    print(f"OK — paradata_volterra.graphml ({out.stat().st_size} bytes)")


def _emit_groups_fixture():
    """Generate groups_volterra.graphml — pre-cooked ad-hoc group
    fixture used by AI06 round-trip / idempotent tests."""
    import sqlite3
    import shutil
    import tempfile
    from pathlib import Path

    PLUGIN_ROOT = Path(__file__).resolve().parents[3]
    SRC_DB = PLUGIN_ROOT / "tests" / "sync" / "fixtures" / "mini_volterra.sqlite"

    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids,
    )
    tmp_db = Path(tempfile.mkdtemp()) / "mini_volterra.sqlite"
    shutil.copy2(SRC_DB, tmp_db)
    add_columns(tmp_db); backfill_uuids(tmp_db)

    sito = sqlite3.connect(tmp_db).execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]

    # Pick 3 real US node_uuids
    conn = sqlite3.connect(tmp_db)
    rows = conn.execute(
        "SELECT node_uuid FROM us_table WHERE sito=? LIMIT 3",
        (sito,)).fetchall()
    member_uuids = [r[0] for r in rows]
    conn.close()

    from modules.s3dgraphy.sync.group_store import GroupStore
    store = GroupStore(tmp_db, sito)
    store.add_group(
        "restauri-2023",
        group_kind="adhoc",
        member_us_uuids=member_uuids,
        description="Restauri eseguiti nel 2023",
    )

    out = PLUGIN_ROOT / "tests" / "sync" / "fixtures" / "groups_volterra.graphml"
    shutil.copy2(store.file_path, out)
    print(f"OK — groups_volterra.graphml ({out.stat().st_size} bytes)")


def _emit_toponym_volterra():
    """Generate toponym_volterra.sqlite — variant with site_table
    populated so AC-15 (round-trip identity) and AC-20 (cross-site
    dedupe) tests have a fixture with non-empty admin levels.

    Three sites are inserted:
    - Volterra: full chain (Italia/Toscana/Pisa/Volterra)
    - Volterra2: shares comune='Volterra' with site #1 (AC-20 dedupe)
    - Pompei_test: empty provincia (AC-15 skip-empty)

    The Phase-1 node_uuid migration is applied so the fixture is a
    drop-in input to GraphProjector.populate_graph (strict_schema=True).
    """
    import sqlite3
    import shutil
    from pathlib import Path

    PLUGIN_ROOT = Path(__file__).resolve().parents[3]
    SRC_DB = PLUGIN_ROOT / "tests" / "sync" / "fixtures" / "mini_volterra.sqlite"
    out = PLUGIN_ROOT / "tests" / "sync" / "fixtures" / "toponym_volterra.sqlite"

    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids,
    )

    if out.exists():
        out.unlink()
    shutil.copy2(SRC_DB, out)
    add_columns(out)
    backfill_uuids(out)

    conn = sqlite3.connect(str(out))
    try:
        # Site #1: full toponym chain (Italia/Toscana/Pisa/Volterra)
        conn.execute(
            "INSERT OR IGNORE INTO site_table "
            "(sito, nazione, regione, provincia, comune, descrizione) "
            "VALUES ('Volterra', 'Italia', 'Toscana', 'Pisa', 'Volterra', "
            "        'Volterra full toponym chain')"
        )
        # Site #2: shares comune='Volterra' with site #1 (AC-20 dedupe)
        conn.execute(
            "INSERT OR IGNORE INTO site_table "
            "(sito, nazione, regione, provincia, comune, descrizione) "
            "VALUES ('Volterra2', 'Italia', 'Toscana', 'Pisa', 'Volterra', "
            "        'Second site for cross-site dedupe test')"
        )
        # Site #3: empty provincia (AC-15 skip-empty)
        conn.execute(
            "INSERT OR IGNORE INTO site_table "
            "(sito, nazione, regione, provincia, comune, descrizione) "
            "VALUES ('Pompei_test', 'Italia', 'Campania', '', 'Pompei', "
            "        'Site with empty provincia for skip-empty test')"
        )
        conn.commit()
    finally:
        conn.close()
    print(f"OK — toponym_volterra.sqlite ({out.stat().st_size} bytes)")


def _emit_legacy_5_5_x_fixture():
    """Hand-crafted GraphML mimicking AI06 output: 4 ActivityNodeGroup
    folders with pyarchinit.<kind> data attributes.

    AI07's on-read up-conversion (Group F) must promote 3 of these
    (struttura, area, settore) to LocationNodeGroup; attivita stays
    untouched per Q1.
    """
    HERE = Path(__file__).resolve().parent
    out = HERE / "legacy_5_5_x.graphml"
    template = '''<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key id="d_kind_attivita" for="node" attr.name="pyarchinit.attivita"/>
  <key id="d_kind_struttura" for="node" attr.name="pyarchinit.struttura"/>
  <key id="d_kind_area" for="node" attr.name="pyarchinit.area"/>
  <key id="d_kind_settore" for="node" attr.name="pyarchinit.settore"/>
  <key id="d_node_type" for="node" attr.name="_s3d_node_type"/>
  <graph id="G" edgedefault="directed">
    <node id="grp_attivita" yfiles.foldertype="group">
      <data key="d_node_type">ActivityNodeGroup</data>
      <data key="d_kind_attivita">Saggio_I</data>
    </node>
    <node id="grp_struttura" yfiles.foldertype="group">
      <data key="d_node_type">ActivityNodeGroup</data>
      <data key="d_kind_struttura">Basilica</data>
    </node>
    <node id="grp_area" yfiles.foldertype="group">
      <data key="d_node_type">ActivityNodeGroup</data>
      <data key="d_kind_area">A</data>
    </node>
    <node id="grp_settore" yfiles.foldertype="group">
      <data key="d_node_type">ActivityNodeGroup</data>
      <data key="d_kind_settore">Settore_N</data>
    </node>
  </graph>
</graphml>
'''
    out.write_text(template, encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    rc = main()
    _emit_toponym_volterra()
    _emit_legacy_5_5_x_fixture()
    raise SystemExit(rc)
