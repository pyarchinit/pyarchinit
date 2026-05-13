"""Library for the media-fk-cascade migration (5.7.9.3-alpha milestone).

Heals existing PostgreSQL pyarchinit databases that still ship the legacy
killer triggers ``delete_media_table`` + ``delete_media_to_entity_table``
(both fire on ``media_thumb_table`` AFTER UPDATE OR DELETE) by:

  1. Dropping both triggers + their backing plpgsql functions
  2. Deleting orphan rows in ``media_thumb_table`` + ``media_to_entity_table``
     (id_media values without a matching ``media_table.id_media``)
  3. Installing proper ``FOREIGN KEY ... ON DELETE CASCADE`` in the
     natural master -> derived direction.

PG-only — invoking any of the 4 public functions with a non-PostgreSQL
``DbHandle`` raises ``RuntimeError``. SQLite is out of scope for this
milestone (FK retrofit on SQLite requires a table-recreate dance).

Pattern: mirrors ``_2026_05_node_uuid_backfill_lib.py`` (PG-A 5.7.0-alpha).
Single-transaction apply via ``handle.engine.begin()``. Dry-run is
implemented via the ``_DryRunRollback`` sentinel pattern from
``GraphIngestor`` (PG-C 5.7.2-alpha) — raise inside the begin() block to
force rollback, swallow outside the block.

Background: on 2026-05-13 a pyarchinit production PG database (khutm2)
silently lost ~5156 media + ~5758 MTE rows because the trigger function
body contained the tautology ``IF OLD.id_media != OLD.id_media THEN ...
ELSE DELETE FROM media_table ...`` which made the cascade-DELETE branch
fire on every UPDATE/DELETE against ``media_thumb_table``. See the spec
(``docs/superpowers/specs/2026-05-13-media-fk-migration-design.md``) for
the full root-cause analysis.
"""
from __future__ import annotations

from sqlalchemy import text

from modules.s3dgraphy.sync._db_handle import DbHandle


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Names of the legacy killer triggers on ``media_thumb_table`` we need to
#: detect and drop. Both are AFTER UPDATE OR DELETE row triggers backed by
#: a plpgsql function of the same name.
_KILLER_TRIGGER_NAMES: tuple[str, ...] = (
    "delete_media_table",
    "delete_media_to_entity_table",
)

#: Replacement FK names. ON DELETE CASCADE in the natural master -> derived
#: direction (``media_table`` -> ``media_thumb_table`` /
#: ``media_to_entity_table``).
_FK_THUMB_NAME = "fk_media_thumb_to_media"
_FK_MTE_NAME = "fk_mte_to_media"


class _DryRunRollback(Exception):
    """Internal sentinel used to force a rollback at the end of a dry-run.

    SQLAlchemy ``engine.begin()`` commits on clean exit and rolls back on
    any raised exception. To preserve dry-run semantics (execute the whole
    block, gather the result dict, then roll back) we raise this sentinel
    after the last DDL inside the ``begin()`` block, and swallow it just
    outside. Same pattern as ``GraphIngestor._DryRunRollback`` (PG-C).
    """


# ---------------------------------------------------------------------------
# Backend guard
# ---------------------------------------------------------------------------

def _require_postgres(handle: DbHandle) -> None:
    """Raise ``RuntimeError`` unless ``handle`` wraps a PostgreSQL engine.

    Centralised because every public function in this module is PG-only;
    a non-PG handle is always a programming error (we never want to
    silently no-op on SQLite — the user must be told to use the SQLite
    template migration path instead).
    """
    if not handle.is_postgres:
        raise RuntimeError("media-fk-migration is PostgreSQL-only")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_killer_triggers(handle: DbHandle) -> dict:
    """Detect the presence of the legacy killer triggers on the PG handle.

    Returns:
        ``{'has_triggers': bool, 'trigger_names': [str, ...]}``.
        ``has_triggers`` is True iff at least one of the two legacy
        triggers is currently installed on ``media_thumb_table``;
        ``trigger_names`` lists the names that were actually found
        (subset of ``_KILLER_TRIGGER_NAMES``).

    Read-only: uses ``engine.connect()`` (no transaction). Idempotent.
    """
    _require_postgres(handle)
    with handle.engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT trigger_name FROM information_schema.triggers "
                "WHERE event_object_table = 'media_thumb_table' "
                "AND trigger_name IN ('delete_media_table', "
                "'delete_media_to_entity_table')"
            )
        ).fetchall()
    # Trigger can appear once per event (UPDATE + DELETE); de-dup by name.
    found = sorted({r[0] for r in rows})
    return {"has_triggers": bool(found), "trigger_names": found}


def count_orphans(handle: DbHandle) -> dict:
    """Return counts + samples of orphan rows in thumb + MTE tables.

    An "orphan" is a row in ``media_thumb_table`` or
    ``media_to_entity_table`` whose ``id_media`` value has no matching
    ``media_table.id_media``. Pre-FK these can exist because nothing
    enforced referential integrity (the killer triggers fired on
    deletes but did not prevent orphan inserts).

    Returns:
        ``{'thumb_orphans': N, 'mte_orphans': M,
           'thumb_samples': [(id_media_thumb, id_media), ...],
           'mte_samples': [(id_mediaToEntity, id_media, entity_type), ...]}``.
        Samples are capped at 5 rows each (ORDER BY the local PK).

    Read-only — uses ``engine.connect()``. Safe for production.
    """
    _require_postgres(handle)
    with handle.engine.connect() as conn:
        thumb_count = conn.execute(text(
            "SELECT COUNT(*) FROM media_thumb_table "
            "WHERE id_media NOT IN (SELECT id_media FROM media_table)"
        )).scalar() or 0
        mte_count = conn.execute(text(
            "SELECT COUNT(*) FROM media_to_entity_table "
            "WHERE id_media NOT IN (SELECT id_media FROM media_table)"
        )).scalar() or 0
        thumb_samples = conn.execute(text(
            "SELECT id_media_thumb, id_media FROM media_thumb_table "
            "WHERE id_media NOT IN (SELECT id_media FROM media_table) "
            "ORDER BY id_media_thumb LIMIT 5"
        )).fetchall()
        mte_samples = conn.execute(text(
            'SELECT "id_mediaToEntity", id_media, entity_type '
            "FROM media_to_entity_table "
            "WHERE id_media NOT IN (SELECT id_media FROM media_table) "
            'ORDER BY "id_mediaToEntity" LIMIT 5'
        )).fetchall()
    return {
        "thumb_orphans": int(thumb_count),
        "mte_orphans": int(mte_count),
        "thumb_samples": [tuple(r) for r in thumb_samples],
        "mte_samples": [tuple(r) for r in mte_samples],
    }


def _existing_killer_triggers(conn) -> list[str]:
    """Return the deduplicated list of killer trigger names currently
    installed on ``media_thumb_table`` (subset of
    ``_KILLER_TRIGGER_NAMES``). Used internally during apply_migration to
    avoid double-counting when a trigger is registered against multiple
    events (UPDATE + DELETE)."""
    rows = conn.execute(text(
        "SELECT trigger_name FROM information_schema.triggers "
        "WHERE event_object_table = 'media_thumb_table' "
        "AND trigger_name IN ('delete_media_table', "
        "'delete_media_to_entity_table')"
    )).fetchall()
    return sorted({r[0] for r in rows})


def _existing_fk_names(conn) -> set[str]:
    """Return the set of replacement FK constraint names already installed.

    Used to make ``apply_migration`` idempotent: a re-run on a clean DB
    finds both FKs present and skips the ALTER TABLE step (``fks_installed``
    counter returns 0).
    """
    rows = conn.execute(text(
        "SELECT conname FROM pg_constraint "
        "WHERE conname IN ('fk_media_thumb_to_media', 'fk_mte_to_media')"
    )).fetchall()
    return {r[0] for r in rows}


def apply_migration(handle: DbHandle, *, dry_run: bool = False) -> dict:
    """Apply the migration in a single transaction.

    Order matters:
      1. ``DROP TRIGGER delete_media_table ON media_thumb_table``
         (IF EXISTS)
      2. ``DROP TRIGGER delete_media_to_entity_table ON media_thumb_table``
         (IF EXISTS)
      3. ``DROP FUNCTION delete_media_table()`` (IF EXISTS, no args)
      4. ``DROP FUNCTION delete_media_to_entity_table()`` (IF EXISTS)
      5. ``DELETE FROM media_thumb_table`` orphans
         (id_media NOT IN SELECT FROM media_table)
      6. ``DELETE FROM media_to_entity_table`` orphans
      7. ``ALTER TABLE media_thumb_table ADD CONSTRAINT
         fk_media_thumb_to_media FOREIGN KEY (id_media)
         REFERENCES media_table(id_media) ON DELETE CASCADE``
         — guarded by name lookup so re-runs are no-ops.
      8. Same for ``media_to_entity_table`` / ``fk_mte_to_media``.

    The trigger + function drops MUST happen before the orphan cleanup;
    otherwise the killer triggers would fire on the DELETE statements
    and cascade-delete master rows. The orphan cleanup MUST happen
    before the ALTER TABLE; otherwise PostgreSQL rejects the FK
    creation on the existing orphan rows.

    Args:
        handle: PG-backed ``DbHandle``. Non-PG raises ``RuntimeError``.
        dry_run: If True, raise ``_DryRunRollback`` after step 8 to
            force the transaction to roll back. The returned dict still
            reflects what *would* have happened.

    Returns:
        ``{
            'triggers_dropped': int,     # 0..2 — count of distinct
                                         #        killer triggers
                                         #        actually present and
                                         #        dropped this run
            'thumb_orphans_deleted': int,
            'mte_orphans_deleted': int,
            'fks_installed': int,        # 0..2 — count of NEW FKs added
            'dry_run': bool,
        }``.

    Idempotent: a second run on a clean DB returns all zeros (no
    triggers found, no orphans, both FKs already present).
    """
    _require_postgres(handle)

    result = {
        "triggers_dropped": 0,
        "thumb_orphans_deleted": 0,
        "mte_orphans_deleted": 0,
        "fks_installed": 0,
        "dry_run": bool(dry_run),
    }

    try:
        with handle.engine.begin() as conn:
            # Step 1+2: drop the triggers (idempotent via IF EXISTS).
            # Count only the ones that were actually present, so callers
            # can tell "we fixed something" vs "DB already clean".
            present = _existing_killer_triggers(conn)
            result["triggers_dropped"] = len(present)
            for trig in _KILLER_TRIGGER_NAMES:
                conn.execute(text(
                    f"DROP TRIGGER IF EXISTS {trig} ON media_thumb_table"
                ))

            # Step 3+4: drop the backing functions.
            # Empty parens are REQUIRED — DROP FUNCTION needs the arg
            # list, and these functions take no args.
            for fn in _KILLER_TRIGGER_NAMES:
                conn.execute(text(f"DROP FUNCTION IF EXISTS {fn}()"))

            # Step 5+6: delete orphans BEFORE the ALTER (else FK fails).
            thumb_del = conn.execute(text(
                "DELETE FROM media_thumb_table "
                "WHERE id_media NOT IN (SELECT id_media FROM media_table)"
            ))
            result["thumb_orphans_deleted"] = int(thumb_del.rowcount or 0)
            mte_del = conn.execute(text(
                "DELETE FROM media_to_entity_table "
                "WHERE id_media NOT IN (SELECT id_media FROM media_table)"
            ))
            result["mte_orphans_deleted"] = int(mte_del.rowcount or 0)

            # Step 7+8: install the FKs, guarded by name (idempotent).
            existing_fks = _existing_fk_names(conn)
            if _FK_THUMB_NAME not in existing_fks:
                conn.execute(text(
                    f"ALTER TABLE media_thumb_table "
                    f"ADD CONSTRAINT {_FK_THUMB_NAME} "
                    f"FOREIGN KEY (id_media) "
                    f"REFERENCES media_table(id_media) ON DELETE CASCADE"
                ))
                result["fks_installed"] += 1
            if _FK_MTE_NAME not in existing_fks:
                conn.execute(text(
                    f"ALTER TABLE media_to_entity_table "
                    f"ADD CONSTRAINT {_FK_MTE_NAME} "
                    f"FOREIGN KEY (id_media) "
                    f"REFERENCES media_table(id_media) ON DELETE CASCADE"
                ))
                result["fks_installed"] += 1

            # Dry-run rollback sentinel — must be the very LAST statement
            # inside the begin() block so the result dict is fully
            # populated before the rollback fires.
            if dry_run:
                raise _DryRunRollback()
    except _DryRunRollback:
        # Dry-run completed; rollback already happened on raise. The
        # populated ``result`` dict is what the caller wants — return it.
        pass

    return result


def verify_post_migration(handle: DbHandle) -> dict:
    """Return the post-migration state of the DB.

    Returns:
        ``{
            'killer_triggers_present': [str, ...],  # ideally empty
            'fks_installed': [str, ...],            # ideally both names
            'is_clean': bool,                       # True iff fully migrated
        }``.

    ``is_clean`` is True iff there are zero killer triggers AND both
    replacement FKs (``fk_media_thumb_to_media`` + ``fk_mte_to_media``)
    are installed. Useful as the AC-1 assertion for the milestone.
    """
    _require_postgres(handle)
    with handle.engine.connect() as conn:
        killers = _existing_killer_triggers(conn)
        fks = sorted(_existing_fk_names(conn))
    is_clean = (
        len(killers) == 0
        and _FK_THUMB_NAME in fks
        and _FK_MTE_NAME in fks
    )
    return {
        "killer_triggers_present": killers,
        "fks_installed": fks,
        "is_clean": is_clean,
    }
