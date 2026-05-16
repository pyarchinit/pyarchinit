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
                node_uuid TEXT,
                other_locations TEXT
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


# ---------------------------------------------------------------------------
# PG-B (5.7.1-alpha): load_sqlite_into_pg helper + pg_with_volterra fixture
#
# Used by the AC-2 cousin test (test_ai03_export_pg_structural.py) and by
# test_export_pg.py. Mirrors a SQLite fixture's schema + data into PG so
# end-to-end export tests can compare PG output against the SQLite baseline.
# ---------------------------------------------------------------------------
def _sqlite_type_to_pg(sqlite_type) -> str:
    """Map a SQLite column type to a PG-compatible declaration.

    pyarchinit uses only TEXT, INTEGER, REAL — trivially compatible with PG.
    Anything else falls back to TEXT for safety.
    """
    s = str(sqlite_type).upper()
    if "INT" in s:
        return "INTEGER"
    if "TEXT" in s or "CHAR" in s or "CLOB" in s:
        return "TEXT"
    if "REAL" in s or "FLOA" in s or "DOUB" in s:
        return "REAL"
    return "TEXT"


def load_sqlite_into_pg(sqlite_path, pg_engine, tables=None):
    """Mirror a SQLite fixture's schema + data into PG.

    For each user table in *sqlite_path*:
      1. Reflect columns via SQLAlchemy Inspector
      2. CREATE TABLE IF NOT EXISTS on PG with TEXT/INTEGER/REAL types
      3. TRUNCATE ... RESTART IDENTITY CASCADE
      4. INSERT every SQLite row via executemany

    Idempotent. Returns a dict {table: rows_loaded}.

    Args:
        sqlite_path: Path to the SQLite fixture file.
        pg_engine: SQLAlchemy Engine connected to PG.
        tables: Optional list of table names to limit the load.
                None (default) = all user tables (excludes sqlite_*).
    """
    from pathlib import Path
    from sqlalchemy import create_engine, inspect

    sqlite_engine = create_engine(f"sqlite:///{Path(sqlite_path)}")
    sqlite_inspector = inspect(sqlite_engine)
    all_tables = [
        t for t in sqlite_inspector.get_table_names()
        if not t.startswith("sqlite_")
    ]
    tables = list(tables) if tables else all_tables
    counts: dict = {}

    for table in tables:
        cols = sqlite_inspector.get_columns(table)
        if not cols:
            counts[table] = 0
            continue
        col_defs = ", ".join(
            f"{c['name']} {_sqlite_type_to_pg(c['type'])}"
            for c in cols
        )
        with pg_engine.begin() as conn:
            conn.execute(text(
                f"CREATE TABLE IF NOT EXISTS {table} ({col_defs})"
            ))
            conn.execute(text(
                f"TRUNCATE {table} RESTART IDENTITY CASCADE"
            ))

        with sqlite_engine.connect() as src:
            rows = src.execute(
                text(f"SELECT * FROM {table}")
            ).mappings().all()
        if rows:
            col_names = list(rows[0].keys())
            placeholders = ", ".join(f":{c}" for c in col_names)
            with pg_engine.begin() as conn:
                conn.execute(
                    text(
                        f"INSERT INTO {table} ({', '.join(col_names)}) "
                        f"VALUES ({placeholders})"
                    ),
                    [dict(r) for r in rows],
                )
        counts[table] = len(rows)

    sqlite_engine.dispose()
    return counts


@pytest.fixture
def pg_with_volterra(pg_engine):
    """PG seeded with the mini_volterra.sqlite fixture data.

    Used by tests that need a populated PG to compare against the
    SQLite baseline (AC-2 cousin, export_pg tests).
    """
    from pathlib import Path
    fixture = Path(__file__).parent / "fixtures" / "mini_volterra.sqlite"
    if not fixture.exists():
        pytest.skip(f"Fixture missing: {fixture}")
    load_sqlite_into_pg(fixture, pg_engine)
    yield pg_engine
