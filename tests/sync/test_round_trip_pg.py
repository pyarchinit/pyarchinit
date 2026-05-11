# tests/sync/test_round_trip_pg.py
"""PG-C AC-2 cousin: round-trip identity on PostgreSQL.

THE gate test for PG-C. Verifies that the import path on PG produces
a database state equivalent to a fresh export — i.e., the bridge is
idempotent end-to-end on PG.

Flow:
  1. Seed PG with mini_volterra.sqlite data (pg_with_volterra fixture)
  2. Export PG → first.graphml
  3. Import first.graphml back into the SAME PG (re-write)
  4. Re-export PG → second.graphml
  5. Compare structural fingerprints of first.graphml and second.graphml

If the import pipeline drops or mutates data, the second export will
diverge from the first. Reuses _structure() from the existing AC-2
test to ensure identical fingerprint definition.

Skipped cleanly when PG offline / psycopg2 missing.
"""
from __future__ import annotations

import pytest

# Import fixtures explicitly - conftest_pg.py is not auto-discovered
from tests.sync.conftest_pg import pg_engine, pg_with_volterra  # noqa: F401


def test_round_trip_pg_identity(pg_with_volterra, tmp_path):
    """Full round-trip on PG: seed PG with mini_volterra → export →
    import the exported GraphML back into the SAME PG → re-export →
    compare structural fingerprints.

    THE gate for PG-C."""
    from tests.sync.test_ai03_export_byte_identical import _structure
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor

    handle = DbHandle.from_engine(pg_with_volterra,
                                   str(pg_with_volterra.url))

    out1 = tmp_path / "first.graphml"
    export_graphml(db_path=handle, mapping="pyarchinit_us_mapping",
                   output_path=out1, site_filter="Volterra")

    # Import first.graphml back into the same PG (re-write path).
    # This exercises the entire populate_list pipeline: SELECT, UPDATE
    # for existing rows, ConflictResolver, etc.
    GraphIngestor().populate_list(
        graph=out1, db_path=handle, sito="Volterra",
        dry_run=False, graphml_path=out1,
    )

    out2 = tmp_path / "second.graphml"
    export_graphml(db_path=handle, mapping="pyarchinit_us_mapping",
                   output_path=out2, site_filter="Volterra")

    fp1 = _structure(out1.read_text(encoding="utf-8"))
    fp2 = _structure(out2.read_text(encoding="utf-8"))

    assert fp1 == fp2, (
        f"PG round-trip not idempotent.\n"
        f"  fp1 (post-export):   {fp1!r}\n"
        f"  fp2 (post-reimport): {fp2!r}\n\n"
        f"This is THE PG-C gate. If this fails, the import pipeline "
        f"has regressed on PG. Compare each key (node_count, "
        f"edge_count, labels, row_count, table_count) to find which "
        f"part of the pipeline diverged."
    )
