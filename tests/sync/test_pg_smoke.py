# tests/sync/test_pg_smoke.py
"""PG-Compat Foundation: smoke test for the pg_engine fixture.

Verifies:
  - pg_engine fixture connects (or skips cleanly if PG offline)
  - Schema bootstrap created the expected tables
  - _columns_of() works on PG via information_schema dispatch path

Skipped cleanly when PG is unreachable. CI without a local PG
sees no failures.
"""
from __future__ import annotations

# Import the fixture into the local namespace so pytest discovers it
# (conftest_pg.py is not an auto-discovered conftest.py)
from tests.sync.conftest_pg import pg_engine  # noqa: F401


def test_pg_smoke_columns_of_us_table(pg_engine):
    """pg_engine connects + schema bootstrap created us_table +
    _columns_of() returns the expected columns via information_schema."""
    from s3dgraphy.sync._db_handle import _columns_of
    cols = _columns_of(pg_engine, "us_table")
    # Foundation schema declares: id_us, sito, area, us, d_stratigrafica,
    # d_interpretativa, rapporti, periodo_iniziale, fase_iniziale,
    # periodo_finale, fase_finale, struttura, attivita, settore,
    # ambient, saggio, quad_par, unita_tipo, node_uuid
    expected = {
        "id_us", "sito", "area", "us", "d_stratigrafica",
        "d_interpretativa", "rapporti", "periodo_iniziale",
        "fase_iniziale", "periodo_finale", "fase_finale",
        "struttura", "attivita", "settore", "ambient", "saggio",
        "quad_par", "unita_tipo", "node_uuid",
    }
    assert cols == expected, (
        f"PG us_table columns mismatch.\n"
        f"  Expected: {sorted(expected)}\n"
        f"  Got:      {sorted(cols)}"
    )
