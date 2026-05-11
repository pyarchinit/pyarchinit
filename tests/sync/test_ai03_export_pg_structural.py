# tests/sync/test_ai03_export_pg_structural.py
"""PG-B AC-2 cousin: PG export structural fingerprint == SQLite baseline.

This is THE gate for PG-B. If it passes, PG produces structurally
equivalent GraphML to SQLite for the mini_volterra fixture. If it
fails, PG-B has a regression in the export pipeline.

Reuses the _structure() helper from test_ai03_export_byte_identical.py
(the existing AC-2 test) to ensure both sides apply the SAME
fingerprint definition.

Skipped cleanly when PG offline / psycopg2 missing.
"""
from __future__ import annotations

import pytest

# Import fixtures explicitly - conftest_pg.py is not auto-discovered
from tests.sync.conftest_pg import pg_engine, pg_with_volterra  # noqa: F401


def test_pg_export_structural_fingerprint_matches_sqlite_baseline(
        pg_with_volterra, tmp_path):
    """The PG export of mini_volterra produces the same structural
    fingerprint as the committed SQLite baseline GraphML.

    Uses _structure() from test_ai03_export_byte_identical.py so the
    fingerprint definition is identical to AC-2.
    """
    from tests.sync.test_ai03_export_byte_identical import (
        _structure, BASELINE,
    )
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    from modules.s3dgraphy.sync._db_handle import DbHandle

    handle = DbHandle.from_engine(pg_with_volterra,
                                   str(pg_with_volterra.url))
    out = tmp_path / "out_pg.graphml"
    result = export_graphml(
        db_path=handle,
        mapping="pyarchinit_us_mapping",
        output_path=out,
        site_filter="Volterra",
    )

    actual = _structure(out.read_text(encoding="utf-8"))
    baseline = _structure(BASELINE.read_text(encoding="utf-8"))

    assert actual == baseline, (
        f"PG export structural fingerprint != SQLite baseline.\n"
        f"  actual:   {actual!r}\n"
        f"  baseline: {baseline!r}\n\n"
        f"This is THE PG-B gate. If this fails, the export pipeline "
        f"has regressed on PG. Compare each key (node_count, "
        f"edge_count, labels, row_count, table_count) to find which "
        f"part of the pipeline diverged."
    )
    assert result.node_count > 0
