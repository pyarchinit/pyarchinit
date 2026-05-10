# tests/sync/conftest_pg.py
"""PG-Compat Foundation: PostgreSQL test fixtures.

Shared fixtures used by every PG-aware test in tests/sync/. All
fixtures skip cleanly when PG is unreachable at localhost:5433, so
CI runs without a local PG see no failures.

Setup expected (USER pre-creates):
    psql -h localhost -p 5433 -U postgres \\
        -c "CREATE DATABASE pyarchinit_test_pg"

The pg_engine fixture creates the schema on first connection.
Subsequent test runs reuse it; clean_pg truncates between tests.
"""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


PG_CONN_STR = (
    "postgresql+psycopg2://postgres:postgres@localhost:5433/pyarchinit_test_pg"
)


def _apply_pyarchinit_schema(engine: Engine) -> None:
    """Apply minimal pyarchinit DDL to a PG database for testing.

    Foundation milestone: only us_table, site_table, periodizzazione_table
    with the columns the bridge actually reads/writes. Future PG-A/B/C
    milestones may extend this as needed.

    Idempotent: uses CREATE TABLE IF NOT EXISTS.
    """
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS us_table (
                id_us SERIAL PRIMARY KEY,
                sito TEXT,
                area TEXT,
                us TEXT,
                d_stratigrafica TEXT,
                d_interpretativa TEXT,
                rapporti TEXT,
                periodo_iniziale TEXT,
                fase_iniziale TEXT,
                periodo_finale TEXT,
                fase_finale TEXT,
                struttura TEXT,
                attivita TEXT,
                settore TEXT,
                ambient TEXT,
                saggio TEXT,
                quad_par TEXT,
                unita_tipo TEXT DEFAULT 'US',
                node_uuid TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS site_table (
                id_sito SERIAL PRIMARY KEY,
                sito TEXT UNIQUE,
                nazione TEXT,
                regione TEXT,
                provincia TEXT,
                comune TEXT,
                descrizione TEXT,
                node_uuid TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS periodizzazione_table (
                id_perfas SERIAL PRIMARY KEY,
                sito TEXT,
                periodo INTEGER,
                fase TEXT,
                cron_iniziale INTEGER,
                cron_finale INTEGER,
                descrizione TEXT,
                datazione_estesa TEXT,
                node_uuid TEXT,
                CONSTRAINT pg_periodizzazione_unico UNIQUE (sito, periodo, fase)
            )
        """))


@pytest.fixture(scope="session")
def pg_engine():
    """Session-scoped PG engine. Skip cleanly if PG unreachable."""
    try:
        engine = create_engine(PG_CONN_STR)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        pytest.skip(
            f"PG not available at localhost:5433 ({type(e).__name__}: {e})"
        )
    _apply_pyarchinit_schema(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def clean_pg(pg_engine):
    """Truncate all stratigraphic tables before each test.

    Provides isolation between tests without paying schema-creation
    cost (which is amortised by the session-scoped pg_engine).
    """
    with pg_engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE us_table, site_table, periodizzazione_table "
            "RESTART IDENTITY CASCADE"
        ))
    yield pg_engine
