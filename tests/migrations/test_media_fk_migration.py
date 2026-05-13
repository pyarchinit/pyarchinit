"""media-fk-migration (5.7.9.3-alpha) L0 source-inspection guards.

Background: on 2026-05-13 a pyarchinit production PG database (khutm2)
silently lost ~5156 media + ~5758 MTE rows because of a buggy plpgsql
trigger shipped in the PG schema templates. The trigger function body
contained the tautology ``IF OLD.id_media != OLD.id_media THEN ...
ELSE DELETE FROM media_table ...`` which made the cascade-DELETE branch
fire on every UPDATE/DELETE against ``media_thumb_table``.

The Group A surgery removes both trigger functions + their CREATE TRIGGER
DO-blocks from ``pyarchinit_schema_clean.sql`` and
``pyarchinit_schema_updated.sql``, and replaces them with proper
``FOREIGN KEY ... ON DELETE CASCADE`` constraints in the natural
master -> derived direction (``media_table`` -> ``media_thumb_table`` +
``media_to_entity_table``).

These four L0 tests read the SQL files as plain text and assert the
killer trigger code is gone AND the FK constraints are in place. They
do NOT execute any SQL — they are pure source inspection, runnable
without a PG cluster.

See ``docs/superpowers/specs/2026-05-13-media-fk-migration-design.md``
and ``docs/superpowers/plans/2026-05-13-media-fk-migration.md``.
"""
from __future__ import annotations

import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLEAN_SQL = _REPO_ROOT / "resources" / "dbfiles" / "pyarchinit_schema_clean.sql"
_UPDATED_SQL = _REPO_ROOT / "resources" / "dbfiles" / "pyarchinit_schema_updated.sql"


def _read_lines(path: Path) -> list[str]:
    """Return file contents as a list of lines (preserves line numbers
    via 0-indexed offsets, so failures can pinpoint the offending line)."""
    assert path.exists(), f"schema file missing: {path}"
    return path.read_text(encoding="utf-8").splitlines()


def _non_comment_lines(lines: list[str]) -> list[tuple[int, str]]:
    """Strip out comment-only lines (lines whose first non-whitespace
    characters are ``--``). Returns ``[(lineno_1indexed, content), ...]``
    so a failure message can quote the offending line."""
    out: list[tuple[int, str]] = []
    for idx, raw in enumerate(lines, start=1):
        stripped = raw.lstrip()
        if stripped.startswith("--"):
            continue
        out.append((idx, raw))
    return out


# ---------------------------------------------------------------------------
# Killer-trigger absence guards
# ---------------------------------------------------------------------------

_KILLER_FN_RE = re.compile(
    r"^\s*CREATE\s+(OR\s+REPLACE\s+)?FUNCTION\s+delete_media(_to_entity)?_table\b",
    re.IGNORECASE,
)
_KILLER_TRIG_RE = re.compile(
    r"^\s*CREATE\s+TRIGGER\s+delete_media(_to_entity)?_table\b",
    re.IGNORECASE,
)


def _assert_no_killer_trigger(path: Path) -> None:
    """Fail if any non-comment line in ``path`` matches the legacy
    ``CREATE FUNCTION`` or ``CREATE TRIGGER`` killer-trigger pattern.
    Comment lines (starting ``--``) are skipped because we intentionally
    leave a descriptive block-comment behind to document the removal."""
    raw = _read_lines(path)
    survivors = _non_comment_lines(raw)
    offenders: list[str] = []
    for lineno, content in survivors:
        if _KILLER_FN_RE.match(content) or _KILLER_TRIG_RE.match(content):
            offenders.append(f"{path.name}:{lineno}: {content!r}")
    assert not offenders, (
        "Legacy killer-trigger code still present in "
        f"{path.name}. The Group A surgery must remove both "
        "delete_media_table and delete_media_to_entity_table function + "
        "trigger blocks. Offending lines:\n  " + "\n  ".join(offenders)
    )


def test_pg_schema_clean_has_no_killer_trigger():
    """``pyarchinit_schema_clean.sql`` must NOT contain active CREATE
    FUNCTION or CREATE TRIGGER statements for the legacy killer
    triggers. A descriptive comment block referring to them by name is
    permitted (and present)."""
    _assert_no_killer_trigger(_CLEAN_SQL)


def test_pg_schema_updated_has_no_killer_trigger():
    """Same guard for ``pyarchinit_schema_updated.sql``."""
    _assert_no_killer_trigger(_UPDATED_SQL)


# ---------------------------------------------------------------------------
# FK CASCADE presence guards
# ---------------------------------------------------------------------------

_FK_THUMB_RE = re.compile(
    r"ADD\s+CONSTRAINT\s+fk_media_thumb_to_media\b", re.IGNORECASE
)
_FK_MTE_RE = re.compile(
    r"ADD\s+CONSTRAINT\s+fk_mte_to_media\b", re.IGNORECASE
)
_CASCADE_RE = re.compile(
    r"REFERENCES\s+media_table\s*\(\s*id_media\s*\)\s+ON\s+DELETE\s+CASCADE",
    re.IGNORECASE,
)


def _assert_fk_cascade(path: Path) -> None:
    """Fail unless the file declares exactly one ``fk_media_thumb_to_media``
    constraint and one ``fk_mte_to_media`` constraint, and at least two
    ``REFERENCES media_table(id_media) ON DELETE CASCADE`` clauses (one
    for each FK)."""
    src = path.read_text(encoding="utf-8")

    thumb_hits = _FK_THUMB_RE.findall(src)
    mte_hits = _FK_MTE_RE.findall(src)
    cascade_hits = _CASCADE_RE.findall(src)

    assert len(thumb_hits) == 1, (
        f"{path.name} must declare ADD CONSTRAINT fk_media_thumb_to_media "
        f"exactly once; got {len(thumb_hits)} match(es). The FK is the "
        "replacement for the deleted killer trigger on media_thumb_table."
    )
    assert len(mte_hits) == 1, (
        f"{path.name} must declare ADD CONSTRAINT fk_mte_to_media exactly "
        f"once; got {len(mte_hits)} match(es). The FK is the replacement "
        "for the deleted killer trigger that targeted media_to_entity_table."
    )
    assert len(cascade_hits) >= 2, (
        f"{path.name} must contain at least two "
        "'REFERENCES media_table(id_media) ON DELETE CASCADE' clauses "
        f"(one per FK); got {len(cascade_hits)}. Without ON DELETE CASCADE "
        "the FK behaves as RESTRICT and the migration semantics break."
    )


def test_pg_schema_clean_has_fk_cascade():
    """``pyarchinit_schema_clean.sql`` must define both replacement FK
    constraints with ON DELETE CASCADE in the natural master -> derived
    direction (media_table -> media_thumb_table + media_to_entity_table)."""
    _assert_fk_cascade(_CLEAN_SQL)


def test_pg_schema_updated_has_fk_cascade():
    """Same guard for ``pyarchinit_schema_updated.sql``."""
    _assert_fk_cascade(_UPDATED_SQL)


# ---------------------------------------------------------------------------
# Group B — migration library + CLI L0 source-inspection guards
#
# These two tests confirm the public surface of the lib + CLI without
# importing them (some test environments lack psycopg2 / QGIS), by
# reading the source files as plain text.
# ---------------------------------------------------------------------------

_LIB_PATH = (
    _REPO_ROOT / "scripts" / "migrations"
    / "_2026_05_media_fk_cascade_lib.py"
)
_CLI_PATH = (
    _REPO_ROOT / "scripts" / "migrations"
    / "2026_05_media_fk_cascade.py"
)


def test_migration_lib_has_required_api():
    """``_2026_05_media_fk_cascade_lib.py`` must declare all 4 public
    functions + the ``_DryRunRollback`` sentinel, and the
    ``apply_migration`` body must execute DROP before DELETE before
    ALTER TABLE (the orphan cleanup MUST precede the FK install — else
    PostgreSQL rejects the ADD CONSTRAINT)."""
    assert _LIB_PATH.exists(), f"lib file missing: {_LIB_PATH}"
    src = _LIB_PATH.read_text(encoding="utf-8")
    for fn in (
        "def detect_killer_triggers(",
        "def count_orphans(",
        "def apply_migration(",
        "def verify_post_migration(",
    ):
        assert fn in src, f"missing public function declaration: {fn}"
    assert "class _DryRunRollback(" in src, (
        "_DryRunRollback sentinel class missing — dry-run cannot "
        "force rollback without it"
    )
    # Ordering inside apply_migration: DROP before DELETE before ALTER.
    # Scope the search to the apply_migration *executable* body only —
    # function docstrings reference DELETE / ADD CONSTRAINT in their
    # narrative and would skew the offsets. We anchor on the first
    # ``with handle.engine.begin()`` inside apply_migration.
    apply_start = src.find("def apply_migration(")
    assert apply_start > 0, "def apply_migration(...) missing"
    next_def = src.find("\ndef ", apply_start + 1)
    fn_body = src[apply_start:next_def] if next_def > 0 else src[apply_start:]
    begin_idx = fn_body.find("with handle.engine.begin()")
    assert begin_idx > 0, (
        "apply_migration must use ``with handle.engine.begin()`` for "
        "single-transaction atomicity"
    )
    body = fn_body[begin_idx:]
    drop_trig = body.find("DROP TRIGGER IF EXISTS")
    drop_fn = body.find("DROP FUNCTION IF EXISTS")
    delete_orphans = body.find("DELETE FROM media_thumb_table")
    add_constraint = body.find("ADD CONSTRAINT")
    assert drop_trig > 0, "DROP TRIGGER statement missing in apply_migration"
    assert drop_fn > 0, "DROP FUNCTION statement missing in apply_migration"
    assert delete_orphans > 0, (
        "DELETE orphans statement missing in apply_migration"
    )
    assert add_constraint > 0, (
        "ADD CONSTRAINT statement missing in apply_migration"
    )
    assert drop_trig < drop_fn < delete_orphans < add_constraint, (
        "wrong DDL order in apply_migration body: must be DROP "
        "TRIGGER -> DROP FUNCTION -> DELETE orphans -> ADD "
        "CONSTRAINT (got offsets: "
        f"drop_trig={drop_trig}, drop_fn={drop_fn}, "
        f"delete={delete_orphans}, add={add_constraint})"
    )


def test_cli_has_three_modes():
    """``2026_05_media_fk_cascade.py`` must define argparse flags for
    --detect, --dry-run, --apply and a --db/--conn-str mutex (PG-A
    pattern). Source-inspection so the test does not import the CLI."""
    assert _CLI_PATH.exists(), f"CLI file missing: {_CLI_PATH}"
    src = _CLI_PATH.read_text(encoding="utf-8")
    for flag in ('"--detect"', '"--dry-run"', '"--apply"',
                 '"--db"', '"--conn-str"'):
        assert flag in src, f"missing argparse flag declaration: {flag}"
    # The PG-A flag mutex pattern is required so the CLI can never be
    # invoked with both --db and --conn-str at once.
    assert "add_mutually_exclusive_group" in src, (
        "missing mutually-exclusive group construct — CLI must reject "
        "concurrent --db + --conn-str (and concurrent operation modes)"
    )


# ---------------------------------------------------------------------------
# Group B — L1 PG runtime tests (skip when psycopg2 / PG unavailable)
#
# All 5 PG-runtime tests share the same setup: load the mini_volterra
# fixture into PG via the pg_with_volterra fixture (yields an Engine),
# wrap that Engine in a DbHandle, then create the legacy killer triggers
# + the three media tables via raw SQL before exercising the migration.
#
# Note: pg_with_volterra is function-scoped, so each test starts from a
# clean PG state (no triggers, no media_* tables). The _bootstrap_*
# helpers below create everything the migration needs.
# ---------------------------------------------------------------------------

# Import pg_with_volterra fixture explicitly — conftest_pg.py is not
# auto-discovered (it is named conftest_pg, not conftest).
from tests.sync.conftest_pg import pg_engine, pg_with_volterra  # noqa: F401,E402

import pytest  # noqa: E402

# Verbatim plpgsql function + trigger sources from
# ``resources/dbfiles/pyarchinit_schema_clean.sql`` pre-Group-A, retained
# here so the L1 tests can resurrect the buggy state on a fresh fixture.
_INJECT_KILLER_FN_DELETE_MEDIA = """
CREATE OR REPLACE FUNCTION delete_media_table()
  RETURNS trigger AS
$BODY$
BEGIN
IF OLD.id_media!=OLD.id_media THEN
update media_table set id_media=OLD.id_media;
else
DELETE from media_table
where id_media = OLD.id_media ;
end if;
RETURN OLD;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
"""

_INJECT_KILLER_FN_DELETE_MTE = """
CREATE OR REPLACE FUNCTION delete_media_to_entity_table()
  RETURNS trigger AS
$BODY$
BEGIN
IF OLD.id_media!=OLD.id_media THEN
update media_to_entity_table set id_media=OLD.id_media;
else
DELETE from media_to_entity_table
where id_media = OLD.id_media ;
end if;
RETURN OLD;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
"""


def _bootstrap_media_tables(engine):
    """Create the three media_* tables (no FKs) on the PG fixture engine.

    Mirrors the column declarations in
    ``resources/dbfiles/pyarchinit_schema_clean.sql`` for media_table,
    media_thumb_table, media_to_entity_table. Plain BIGINT PK (not
    SERIAL) so test rows can pin specific id values. No constraints
    other than NOT NULL on PKs so each test can inject orphans / killer
    triggers as needed.
    """
    from sqlalchemy import text as _t
    with engine.begin() as conn:
        conn.execute(_t(
            "CREATE TABLE IF NOT EXISTS media_table ("
            "  id_media BIGINT NOT NULL PRIMARY KEY,"
            "  mediatype text,"
            "  filename text,"
            "  filetype varchar(10),"
            "  filepath text,"
            "  descrizione text,"
            "  tags text,"
            "  entity_uuid text"
            ")"
        ))
        conn.execute(_t(
            "CREATE TABLE IF NOT EXISTS media_thumb_table ("
            "  id_media_thumb BIGINT NOT NULL PRIMARY KEY,"
            "  id_media BIGINT,"
            "  mediatype text,"
            "  media_filename text,"
            "  media_thumb_filename text,"
            "  filetype varchar(10),"
            "  filepath text,"
            "  path_resize text,"
            "  entity_uuid text"
            ")"
        ))
        conn.execute(_t(
            "CREATE TABLE IF NOT EXISTS media_to_entity_table ("
            '  "id_mediaToEntity" BIGINT NOT NULL PRIMARY KEY,'
            "  id_entity BIGINT,"
            "  entity_type text,"
            "  table_name text,"
            "  id_media BIGINT,"
            "  filepath text,"
            "  media_name text,"
            "  entity_uuid text"
            ")"
        ))


def _teardown_media_tables(engine):
    """Drop the media_* tables + killer triggers/functions left over
    from a previous test (pg_with_volterra is function-scoped but the
    underlying pg_engine is session-scoped, so cruft can survive)."""
    from sqlalchemy import text as _t
    with engine.begin() as conn:
        conn.execute(_t(
            "DROP TRIGGER IF EXISTS delete_media_table ON media_thumb_table"
        ))
        conn.execute(_t(
            "DROP TRIGGER IF EXISTS delete_media_to_entity_table "
            "ON media_thumb_table"
        ))
        conn.execute(_t("DROP FUNCTION IF EXISTS delete_media_table()"))
        conn.execute(_t(
            "DROP FUNCTION IF EXISTS delete_media_to_entity_table()"
        ))
        conn.execute(_t("DROP TABLE IF EXISTS media_thumb_table CASCADE"))
        conn.execute(_t(
            "DROP TABLE IF EXISTS media_to_entity_table CASCADE"
        ))
        conn.execute(_t("DROP TABLE IF EXISTS media_table CASCADE"))


def _inject_killer_triggers(engine):
    """Install the legacy killer triggers verbatim from the pre-Group-A
    schema source. Both triggers fire AFTER UPDATE OR DELETE on
    ``media_thumb_table`` and call the same-named plpgsql function.

    Pre-condition: ``_bootstrap_media_tables`` has been called so the
    three media_* tables exist.
    """
    from sqlalchemy import text as _t
    with engine.begin() as conn:
        conn.exec_driver_sql(_INJECT_KILLER_FN_DELETE_MEDIA)
        conn.exec_driver_sql(_INJECT_KILLER_FN_DELETE_MTE)
        conn.execute(_t(
            "CREATE TRIGGER delete_media_table "
            "AFTER UPDATE OR DELETE ON media_thumb_table "
            "FOR EACH ROW EXECUTE FUNCTION delete_media_table()"
        ))
        conn.execute(_t(
            "CREATE TRIGGER delete_media_to_entity_table "
            "AFTER UPDATE OR DELETE ON media_thumb_table "
            "FOR EACH ROW EXECUTE FUNCTION "
            "delete_media_to_entity_table()"
        ))


def _wrap_handle(pg_engine_obj):
    """Wrap the function-scoped pg_with_volterra Engine in a DbHandle.

    Same pattern as ``tests/sync/test_pg_bv2_pg_importer.py`` tests 3+4.
    """
    from modules.s3dgraphy.sync._db_handle import DbHandle
    return DbHandle.from_engine(pg_engine_obj, str(pg_engine_obj.url))


def test_migration_detects_trigger_on_pg_fixture(pg_with_volterra):
    """``detect_killer_triggers`` must return ``has_triggers=True`` and
    list BOTH legacy trigger names when they are present on the DB."""
    pytest.importorskip("psycopg2")
    from scripts.migrations._2026_05_media_fk_cascade_lib import (
        detect_killer_triggers,
    )
    _teardown_media_tables(pg_with_volterra)
    _bootstrap_media_tables(pg_with_volterra)
    _inject_killer_triggers(pg_with_volterra)
    try:
        handle = _wrap_handle(pg_with_volterra)
        result = detect_killer_triggers(handle)
        assert result["has_triggers"] is True
        assert "delete_media_table" in result["trigger_names"]
        assert "delete_media_to_entity_table" in result["trigger_names"]
    finally:
        _teardown_media_tables(pg_with_volterra)


def test_migration_apply_drops_and_installs_fk(pg_with_volterra):
    """``apply_migration`` on a freshly-injected legacy DB must drop
    both triggers, install both FKs, and pass ``verify_post_migration``
    with ``is_clean=True``."""
    pytest.importorskip("psycopg2")
    from scripts.migrations._2026_05_media_fk_cascade_lib import (
        apply_migration, verify_post_migration,
    )
    _teardown_media_tables(pg_with_volterra)
    _bootstrap_media_tables(pg_with_volterra)
    _inject_killer_triggers(pg_with_volterra)
    try:
        handle = _wrap_handle(pg_with_volterra)
        result = apply_migration(handle, dry_run=False)
        assert result["triggers_dropped"] == 2, (
            f"expected 2 triggers dropped, got {result}"
        )
        assert result["fks_installed"] == 2, (
            f"expected 2 FKs installed, got {result}"
        )
        assert result["dry_run"] is False
        verify = verify_post_migration(handle)
        assert verify["is_clean"] is True, (
            f"post-migration not clean: {verify}"
        )
        assert verify["killer_triggers_present"] == []
        assert "fk_media_thumb_to_media" in verify["fks_installed"]
        assert "fk_mte_to_media" in verify["fks_installed"]
    finally:
        _teardown_media_tables(pg_with_volterra)


def test_migration_idempotent(pg_with_volterra):
    """Second call to ``apply_migration`` on the same DB must be a no-op:
    triggers_dropped=0, fks_installed=0, both runs succeed without
    raising. Idempotency is critical so a user can re-run the menu
    item safely after a partial failure."""
    pytest.importorskip("psycopg2")
    from scripts.migrations._2026_05_media_fk_cascade_lib import (
        apply_migration,
    )
    _teardown_media_tables(pg_with_volterra)
    _bootstrap_media_tables(pg_with_volterra)
    _inject_killer_triggers(pg_with_volterra)
    try:
        handle = _wrap_handle(pg_with_volterra)
        first = apply_migration(handle, dry_run=False)
        assert first["triggers_dropped"] == 2
        assert first["fks_installed"] == 2
        second = apply_migration(handle, dry_run=False)
        assert second["triggers_dropped"] == 0, (
            f"second run found triggers — idempotency broken: {second}"
        )
        assert second["fks_installed"] == 0, (
            f"second run reinstalled FKs — idempotency broken: {second}"
        )
        assert second["thumb_orphans_deleted"] == 0
        assert second["mte_orphans_deleted"] == 0
    finally:
        _teardown_media_tables(pg_with_volterra)


def test_migration_handles_orphans(pg_with_volterra):
    """When the DB carries the killer triggers AND orphan rows in both
    derived tables, ``apply_migration`` must (1) drop the triggers
    first so the orphan DELETE does not cascade, (2) delete exactly the
    orphan rows, (3) install both FKs cleanly (the ADD CONSTRAINT
    would fail if any orphan survived)."""
    pytest.importorskip("psycopg2")
    from sqlalchemy import text as _t
    from scripts.migrations._2026_05_media_fk_cascade_lib import (
        apply_migration,
    )
    _teardown_media_tables(pg_with_volterra)
    _bootstrap_media_tables(pg_with_volterra)
    _inject_killer_triggers(pg_with_volterra)
    try:
        # Seed: 1 valid media row + 3 thumb orphans + 2 MTE orphans.
        # The orphans have id_media values (101, 102, 103, 201, 202)
        # that don't exist in media_table.
        with pg_with_volterra.begin() as conn:
            conn.execute(_t(
                "INSERT INTO media_table (id_media, filename) "
                "VALUES (1, 'real.jpg')"
            ))
            for thumb_id, fake_media in [(11, 101), (12, 102), (13, 103)]:
                conn.execute(_t(
                    "INSERT INTO media_thumb_table "
                    "(id_media_thumb, id_media, media_filename) "
                    "VALUES (:t, :m, 'thumb.jpg')"
                ), {"t": thumb_id, "m": fake_media})
            for mte_id, fake_media in [(21, 201), (22, 202)]:
                conn.execute(_t(
                    'INSERT INTO media_to_entity_table '
                    '("id_mediaToEntity", id_media, entity_type) '
                    "VALUES (:e, :m, 'US')"
                ), {"e": mte_id, "m": fake_media})

        handle = _wrap_handle(pg_with_volterra)
        result = apply_migration(handle, dry_run=False)
        assert result["thumb_orphans_deleted"] == 3, (
            f"expected 3 thumb orphans deleted, got {result}"
        )
        assert result["mte_orphans_deleted"] == 2, (
            f"expected 2 MTE orphans deleted, got {result}"
        )
        assert result["fks_installed"] == 2, (
            f"FK install failed — orphans likely survived: {result}"
        )
    finally:
        _teardown_media_tables(pg_with_volterra)


def test_dry_run_rolls_back(pg_with_volterra):
    """``apply_migration(..., dry_run=True)`` must populate the result
    dict with what WOULD have happened, but leave the database state
    unchanged afterwards (killer triggers still present, orphan rows
    still there, no FKs installed)."""
    pytest.importorskip("psycopg2")
    from sqlalchemy import text as _t
    from scripts.migrations._2026_05_media_fk_cascade_lib import (
        apply_migration, detect_killer_triggers, verify_post_migration,
    )
    _teardown_media_tables(pg_with_volterra)
    _bootstrap_media_tables(pg_with_volterra)
    _inject_killer_triggers(pg_with_volterra)
    try:
        # Seed one orphan to verify rollback covers DELETE too.
        with pg_with_volterra.begin() as conn:
            conn.execute(_t(
                "INSERT INTO media_table (id_media, filename) "
                "VALUES (1, 'real.jpg')"
            ))
            conn.execute(_t(
                "INSERT INTO media_thumb_table "
                "(id_media_thumb, id_media, media_filename) "
                "VALUES (11, 999, 'thumb.jpg')"
            ))

        handle = _wrap_handle(pg_with_volterra)
        result = apply_migration(handle, dry_run=True)
        # Result reflects what WOULD have happened
        assert result["dry_run"] is True
        assert result["triggers_dropped"] == 2, (
            f"dry-run result must report 2 triggers, got {result}"
        )
        assert result["fks_installed"] == 2, (
            f"dry-run result must report 2 FKs, got {result}"
        )
        assert result["thumb_orphans_deleted"] == 1, (
            f"dry-run result must report 1 orphan deleted, got {result}"
        )

        # ...but the actual state is unchanged.
        verify = verify_post_migration(handle)
        assert verify["is_clean"] is False, (
            "dry-run leaked into actual DB state — rollback broken"
        )
        triggers = detect_killer_triggers(handle)
        assert triggers["has_triggers"] is True, (
            "trigger drop survived dry-run — rollback broken"
        )
        # Orphan still there
        with pg_with_volterra.connect() as conn:
            n = conn.execute(_t(
                "SELECT COUNT(*) FROM media_thumb_table "
                "WHERE id_media = 999"
            )).scalar()
            assert n == 1, (
                "orphan deletion survived dry-run — rollback broken"
            )
    finally:
        _teardown_media_tables(pg_with_volterra)


# ---------------------------------------------------------------------------
# Group C — SQLite template-binary guards (L1, no PG required)
#
# The two shipped SQLite template DBs (``resources/dbfiles/pyarchinit.sqlite``
# + ``resources/dbfiles/pyarchinit_db.sqlite``) were created decades ago and
# embed a SQLite-flavour version of the killer trigger
# ``delete_media_table`` (AFTER DELETE on media_thumb_table, cascading into
# media_table). On every fresh SQLite install the user inherited the bug.
#
# Group C drops the trigger from both binaries (in-place sqlite3 surgery,
# then VACUUM to compact). These two L1 tests open the binaries directly
# via the ``sqlite3`` stdlib module and assert ``sqlite_master`` carries
# no ``delete_media*`` triggers, so any future regeneration of the
# templates that re-introduces the trigger will fail CI immediately.
# ---------------------------------------------------------------------------


def test_sqlite_template_pyarchinit_has_no_killer_trigger():
    """The shipped pyarchinit.sqlite template (used by new SQLite
    installations) must not contain the killer trigger that ships
    pre-5.7.9.3-alpha. Reads the binary directly via sqlite3."""
    import sqlite3
    from pathlib import Path
    here = Path(__file__).resolve()
    plugin_root = here.parents[2]
    template = plugin_root / "resources" / "dbfiles" / "pyarchinit.sqlite"
    assert template.exists(), f"template missing: {template}"
    conn = sqlite3.connect(str(template))
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='trigger' "
            "AND name LIKE 'delete_media%'"
        ).fetchall()
    finally:
        conn.close()
    assert rows == [], (
        f"killer trigger(s) still present in template: {rows}. "
        "Regenerate per docs/superpowers/specs/"
        "2026-05-13-media-fk-migration-design.md"
    )


def test_sqlite_template_pyarchinit_db_has_no_killer_trigger():
    """Same guard for the second template pyarchinit_db.sqlite."""
    import sqlite3
    from pathlib import Path
    here = Path(__file__).resolve()
    plugin_root = here.parents[2]
    template = plugin_root / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
    assert template.exists(), f"template missing: {template}"
    conn = sqlite3.connect(str(template))
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='trigger' "
            "AND name LIKE 'delete_media%'"
        ).fetchall()
    finally:
        conn.close()
    assert rows == [], (
        f"killer trigger(s) still present in template: {rows}. "
        "Regenerate per docs/superpowers/specs/"
        "2026-05-13-media-fk-migration-design.md"
    )
