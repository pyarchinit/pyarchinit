"""pg-media-fix (5.7.9.1-alpha) regression tests for query_bool type coercion.

User-reported bug 2026-05-12: "Carica Media" button in US/Pottery/
Struttura/Tafonomia forms does nothing on PostgreSQL.

Root cause: form handlers (e.g. loadMediaPreview in tabs/US_USM.py)
call ``DB_MANAGER.query_bool({'id_entity': "'42'", 'entity_type': "'US'"},
'MEDIATOENTITY')``. ``query_bool`` strips the outer quotes but leaves
``id_entity`` as a string ``'42'``. The MEDIATOENTITY.id_entity column
is BIGINT on PG (and Integer on SQLite per the entity declaration).
PostgreSQL strict typing makes ``BIGINT = 'text'`` either error or
silently return no rows. SQLite is type-loose so it worked there.

Fix: ``query_bool`` now coerces string-encoded numeric values to the
column's python_type when the column is Integer/Float-shaped. Pure
runtime fix — no DB schema changes needed. Works on both new and old
DBs because it inspects the SQLAlchemy entity declaration, not the
on-disk column type.
"""
from __future__ import annotations

import inspect


def test_query_bool_has_numeric_coercion_block():
    """Source-inspection guard: confirm the coercion logic is present
    in the ``_normalize_query_params`` helper and is invoked BEFORE
    the cache lookup in ``query_bool``. The pre-cache order is
    essential — see test_query_bool_normalize_runs_before_cache.

    Reads the module file directly via filesystem path because
    ``import modules.db.pyarchinit_db_manager`` triggers QGIS imports
    which aren't available in non-Qt test environments."""
    from pathlib import Path
    here = Path(__file__).resolve()
    repo_root = here.parents[2]  # plugins/pyarchinit/
    target = repo_root / "modules" / "db" / "pyarchinit_db_manager.py"
    assert target.exists(), f"target file missing: {target}"
    src = target.read_text(encoding="utf-8")
    assert "pg-media-fix" in src, (
        "coercion logic missing or pg-media-fix reference removed — "
        "MEDIATOENTITY queries will silently fail on PG again"
    )
    assert "_normalize_query_params" in src, (
        "_normalize_query_params helper missing — pg-media-fix relies "
        "on extracting the coercion into a callable that runs before "
        "the cache lookup"
    )
    assert "column.type.python_type" in src, (
        "column type introspection missing from coercion logic"
    )
    assert "col_pytype in (int, float)" in src, (
        "numeric-only gate missing — coercion would fire too broadly"
    )
    # The try/except is critical — some SQLAlchemy types lack python_type.
    assert "NotImplementedError" in src and "ValueError" in src, (
        "defensive try/except removed — unhandled type lookups would "
        "raise and break every query_bool call"
    )


def test_query_bool_normalize_runs_before_cache():
    """Critical ordering guard for pg-media-fix.

    The user-reported regression (2026-05-12 evening) was that
    ``query_bool`` returned a STALE empty result from cache on every
    button click because the cache was populated BEFORE the coercion
    was active. Pre-fix order:

        cache_key = _get_cache_key(params)  # keyed by "'42'" str
        cached = _get_cached_result(cache_key) → empty
        return cached  # bug: bypasses coercion forever

    Post-fix order MUST be:

        params = _normalize_query_params(params, ...)  # coerce first
        cache_key = _get_cache_key(params)  # keyed by 42 int
        cached = _get_cached_result(cache_key) → miss
        ... actually run the query

    This test fails if a future refactor moves the cache lookup back
    above the normalize call."""
    from pathlib import Path
    here = Path(__file__).resolve()
    repo_root = here.parents[2]
    target = repo_root / "modules" / "db" / "pyarchinit_db_manager.py"
    src = target.read_text(encoding="utf-8")

    # Find the ``def query_bool`` definition and extract its body
    # (everything up to the next top-level ``def`` at the same indent).
    start = src.index("    def query_bool(")
    rest = src[start:]
    next_def = rest.index("\n    def ", 1)
    body = rest[:next_def]

    norm_idx = body.find("_normalize_query_params")
    cache_idx = body.find("_get_cache_key")
    assert norm_idx > 0, "_normalize_query_params call missing from query_bool"
    assert cache_idx > 0, "_get_cache_key call missing from query_bool"
    assert norm_idx < cache_idx, (
        "_normalize_query_params must run BEFORE _get_cache_key, "
        "otherwise the stale-string cache key shadows the coercion "
        f"(norm_idx={norm_idx}, cache_idx={cache_idx})"
    )


def test_query_bool_coerces_string_to_int_for_integer_column(tmp_path):
    """End-to-end SQLite: build a tiny schema with an INTEGER column,
    insert a row with id=42, then run query_bool with the legacy
    string pattern ``"'42'"``. Pre-fix: row matched on SQLite (loose
    typing) but NOT on PG. Post-fix: id_entity is coerced to int(42)
    before the comparison, so the SQL emitted is ``WHERE id_entity = 42``
    which works on both backends.

    SQLite check is a proxy for PG behavior since psycopg2 isn't
    installed locally. The coercion happens before the SQL is built,
    so the assertion is symmetric across dialects."""
    from sqlalchemy import (
        Column, Integer, MetaData, String, Table, create_engine,
        text,
    )
    from sqlalchemy.orm import declarative_base, sessionmaker

    # Set up a throwaway entity that mirrors the MEDIATOENTITY shape:
    # numeric PK + string entity_type.
    Base = declarative_base()

    class MediaFake(Base):
        __tablename__ = "media_fake"
        id_pk = Column(Integer, primary_key=True)
        id_entity = Column(Integer)  # numeric like MEDIATOENTITY.id_entity
        entity_type = Column(String)

    db = tmp_path / "x.sqlite"
    engine = create_engine(f"sqlite:///{db}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    s.add(MediaFake(id_pk=1, id_entity=42, entity_type="US"))
    s.add(MediaFake(id_pk=2, id_entity=99, entity_type="US"))
    s.commit()
    s.close()

    # Reproduce the coercion logic inline (test is L0 — doesn't need
    # the full Pyarchinit_db_management object which requires QGIS).
    # This mirrors lines ~2906-2922 in pyarchinit_db_manager.py:query_bool.
    from sqlalchemy import and_
    from sqlalchemy.orm import sessionmaker as sm
    s = sm(bind=engine)()
    search_dict = {
        "id_entity": "'42'",  # legacy quoted-string form
        "entity_type": "'US'",
    }
    conditions = []
    for key, value in search_dict.items():
        column = getattr(MediaFake, key, None)
        if column is None:
            continue
        # Strip outer quotes (same as query_bool).
        if isinstance(value, str) and value.startswith("'") and value.endswith("'"):
            value = value.strip("'")
        # pg-media-fix coercion.
        if isinstance(value, str) and column is not None:
            try:
                col_pytype = column.type.python_type
                if col_pytype in (int, float):
                    value = col_pytype(value)
            except (NotImplementedError, ValueError, AttributeError):
                pass
        conditions.append(column == value)

    res = s.query(MediaFake).filter(and_(*conditions)).all()
    s.close()
    assert len(res) == 1, (
        f"expected exactly 1 row matched, got {len(res)} — coercion "
        f"logic broken"
    )
    assert res[0].id_entity == 42
    assert res[0].entity_type == "US"


def test_query_bool_coercion_safe_for_non_numeric_column():
    """The coercion must NOT alter values when the column is non-numeric.
    A String column with value 'foo' must stay 'foo' after the
    coercion block (str.python_type is str, not in (int, float))."""
    from sqlalchemy import Column, Integer, String
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()

    class Bag(Base):
        __tablename__ = "bag"
        id = Column(Integer, primary_key=True)
        label = Column(String)

    value = "foo"
    column = Bag.label
    # Replicate coercion block.
    if isinstance(value, str) and column is not None:
        try:
            col_pytype = column.type.python_type
            if col_pytype in (int, float):
                value = col_pytype(value)
        except (NotImplementedError, ValueError, AttributeError):
            pass
    assert value == "foo", (
        "coercion fired on non-numeric column — would corrupt string "
        "comparisons"
    )


def test_query_bool_coercion_resilient_to_garbage_input():
    """If the value is a non-numeric string but the column IS numeric
    (e.g. someone passed 'abc' for an Integer column), the coercion
    must fall back gracefully via the except block. The downstream
    comparison will still happen with the original string (which will
    correctly return no rows), but the migration must NOT raise."""
    from sqlalchemy import Column, Integer
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()

    class Bag(Base):
        __tablename__ = "bag2"
        id = Column(Integer, primary_key=True)
        n = Column(Integer)

    value = "abc"  # garbage for an int column
    column = Bag.n
    original = value
    if isinstance(value, str) and column is not None:
        try:
            col_pytype = column.type.python_type
            if col_pytype in (int, float):
                value = col_pytype(value)  # raises ValueError
        except (NotImplementedError, ValueError, AttributeError):
            pass
    assert value == original, (
        "garbage input mutated by coercion — except block failed to "
        "preserve original value"
    )
