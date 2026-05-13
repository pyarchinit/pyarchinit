# media-fk-migration design (5.7.9.3-alpha)

**Date**: 2026-05-13
**Predecessor**: `pg-bv2-hotfix-5.7.9.2-alpha` (commit `c26e7763`)
**Successor (next)**: `yed-import-pipeline-5.8.0-alpha` (yE-D, unchanged target)
**Trigger**: real disaster on khutm2 production DB 2026-05-13 — ~5156 media + ~5758 MTE rows cascade-deleted by a buggy plpgsql trigger with a tautology check (`OLD.id_media != OLD.id_media`). Recovered via `bk20260513.backup` + additive `ON CONFLICT DO NOTHING`. Investigation revealed the same trigger ships in **all** pyarchinit installations.

---

## 1. Problem statement

The pyarchinit PostgreSQL schema (`resources/dbfiles/pyarchinit_schema_clean.sql` and `pyarchinit_schema_updated.sql`) installs two AFTER DELETE OR UPDATE triggers on `media_thumb_table`:

```sql
CREATE TRIGGER delete_media_table AFTER DELETE OR UPDATE ON media_thumb_table
  FOR EACH ROW EXECUTE FUNCTION delete_media_table();
CREATE TRIGGER delete_media_to_entity_table AFTER DELETE OR UPDATE ON media_thumb_table
  FOR EACH ROW EXECUTE FUNCTION delete_media_to_entity_table();
```

Function body (same shape both):

```plpgsql
BEGIN
  IF OLD.id_media != OLD.id_media THEN     -- ⚠ TAUTOLOGY: always FALSE
    update media_table set id_media=OLD.id_media;
  ELSE                                      -- ⚠ always TRUE → cascade DELETE
    DELETE FROM media_table WHERE id_media = OLD.id_media;
  END IF;
END;
```

Effect: any UPDATE or DELETE on `media_thumb_table` cascade-deletes the matching row in `media_table` AND `media_to_entity_table`. The original intent was likely "propagate id_media rename" via a `NEW.id_media != OLD.id_media` check; the tautology made the cascade-DELETE branch always fire.

SQLite ships an analogous trigger (`AFTER DELETE` only, no UPDATE, only on `media_table` — not on MTE), so the blast radius on SQLite is smaller but the principle is still wrong: deleting a thumbnail should not cascade upward to delete the master media row.

---

## 2. Goals

1. **Source files clean**: PG schema templates emit FK ON DELETE CASCADE (master → derived direction), no killer triggers. SQLite binary templates have killer trigger dropped (no FK retrofit — out of scope for SQLite limitations).
2. **Existing PG DBs healed**: ship a migration that detects the killer trigger, cleans orphans, drops the trigger, installs the proper FK CASCADE. Wired in QGIS menu (manual trigger) + CLI script.
3. **Pattern reuse**: the migration follows the node_uuid backfill UX — explicit menu trigger, auto-backup before, dialog showing orphan count + sample, user confirms.
4. **Idempotent**: re-running the migration on an already-fixed DB is a no-op.
5. **No yE-D shift**: target `5.7.9.3-alpha` (patch on top of `5.7.9.2-alpha`).

## 3. Non-goals

- **SQLite existing DBs not migrated**: FK retrofit on SQLite requires table-recreate (`CREATE_NEW + COPY + DROP_OLD + RENAME`) which is invasive on live data. Damage on SQLite is mitigated (only DELETE, not UPDATE; only master, not MTE) and app code handles cleanup. Deferred.
- **Other PG DBs out-of-network**: only khutm2 verified live. Audit query for festos2025/pyarchinit_v2/etc. when reachable; documented in memory.
- **Trigger rewrite as "rename propagator"**: even with `NEW != OLD` fix, the rename use case is impractical (id_media is sequence-driven PK; renames never happen). Skip.

---

## 4. Architecture

### 4.1 Source schema changes (PG)

Both `pyarchinit_schema_clean.sql` and `pyarchinit_schema_updated.sql`:

- **Remove** lines around `CREATE OR REPLACE FUNCTION delete_media_table()` + `CREATE TRIGGER delete_media_table` (and the equivalent for `delete_media_to_entity_table`). Approximate line ranges: 3548-3635 in clean, 3524-3611 in updated.
- **Add** two FK constraints after the media-related table definitions:

```sql
ALTER TABLE media_thumb_table
  ADD CONSTRAINT fk_media_thumb_to_media
  FOREIGN KEY (id_media) REFERENCES media_table(id_media) ON DELETE CASCADE;

ALTER TABLE media_to_entity_table
  ADD CONSTRAINT fk_mte_to_media
  FOREIGN KEY (id_media) REFERENCES media_table(id_media) ON DELETE CASCADE;
```

### 4.2 SQLite binary template patch

Apply in-place to `resources/dbfiles/pyarchinit.sqlite` + `resources/dbfiles/pyarchinit_db.sqlite`:

```sql
DROP TRIGGER IF EXISTS delete_media_table;
DROP TRIGGER IF EXISTS delete_media_to_entity_table;
```

No FK added (SQLite limitation — would require table recreation; out of scope).

### 4.3 New migration module

`scripts/migrations/_2026_05_media_fk_cascade_lib.py` — pure functions, importable from CLI + QGIS handler. Mirrors structure of `_2026_05_node_uuid_backfill_lib.py`.

Public API:

```python
def detect_killer_triggers(handle: DbHandle) -> dict:
    """Return {'has_triggers': bool, 'trigger_names': [...]}.
    Raises on non-PG (this migration is PG-only)."""

def count_orphans(handle: DbHandle) -> dict:
    """Return {'thumb_orphans': N, 'mte_orphans': M, 'samples': [...]}.
    Read-only diagnostic."""

def apply_migration(handle: DbHandle, *, dry_run: bool = False) -> dict:
    """Single transaction:
      1. DROP TRIGGER delete_media_table + delete_media_to_entity_table
      2. DROP FUNCTION (same names)
      3. DELETE FROM media_thumb_table WHERE id_media NOT IN (SELECT id_media FROM media_table)
      4. DELETE FROM media_to_entity_table WHERE id_media NOT IN (SELECT id_media FROM media_table)
      5. ADD CONSTRAINT fk_media_thumb_to_media + fk_mte_to_media (ON DELETE CASCADE)
      6. Verify FK installed.
    If dry_run: rollback after step 5; return counts.
    Returns: {'triggers_dropped': N, 'thumb_orphans_deleted': N, 'mte_orphans_deleted': N, 'fks_installed': N}.
    Idempotent: trigger not present → step 1-2 no-op; FK already present → step 5 no-op (ON CONFLICT-like behavior)."""

def verify_post_migration(handle: DbHandle) -> bool:
    """Return True if both FK exist and no killer triggers remain."""
```

### 4.4 CLI

`scripts/migrations/2026_05_media_fk_cascade.py`:

```bash
# Detect only (read-only)
python scripts/migrations/2026_05_media_fk_cascade.py --detect --conn-str postgresql://...

# Dry-run (rollback at end)
python scripts/migrations/2026_05_media_fk_cascade.py --dry-run --conn-str postgresql://...

# Apply (writes)
python scripts/migrations/2026_05_media_fk_cascade.py --apply --conn-str postgresql://...
```

Auto-backup hook: when `--apply` and backend is PG, invoke the existing `auto_backup_postgres` helper from `_common.py` (already used by node_uuid migration). Same `PYARCHINIT_PG_DUMP_TIMEOUT` env override applies.

### 4.5 QGIS menu integration

Add menu entry next to "Migrazioni → Backfill node_uuid":

`Plugins → pyArchInit → Migrazioni → Fix trigger media (cascade pericoloso)`

Handler in `pyarchinitPlugin.py` (alongside `_run_uuid_backfill_migration`):

```python
def _run_media_fk_migration(self):
    """Detect, dialog confirm, run apply_migration with auto-backup."""
    # Same pattern as _run_uuid_backfill_migration:
    # 1. Resolve current DB connection from settings → DbHandle
    # 2. Check is_postgres; if not, info message "PG-only, skip"
    # 3. Call detect_killer_triggers → if not present, info "DB already clean"
    # 4. Call count_orphans → display dialog with counts + sample
    # 5. Confirm dialog: "Auto-backup eseguito, applicare fix? Sì/No"
    # 6. Call auto_backup_postgres
    # 7. Call apply_migration
    # 8. Show summary dialog
```

---

## 5. Test plan

### L0 — source inspection

1. `test_pg_schema_clean_has_no_killer_trigger`: read `pyarchinit_schema_clean.sql`, assert no `CREATE TRIGGER delete_media_table` or `CREATE FUNCTION delete_media_table` lines.
2. `test_pg_schema_updated_has_no_killer_trigger`: same on `pyarchinit_schema_updated.sql`.
3. `test_pg_schema_clean_has_fk_cascade`: assert two `FOREIGN KEY ... REFERENCES media_table(id_media) ON DELETE CASCADE` definitions.
4. `test_pg_schema_updated_has_fk_cascade`: same.
5. `test_migration_lib_has_required_api`: filesystem read, assert `_2026_05_media_fk_cascade_lib.py` defines all 4 public functions + correct DROP/cleanup/ADD ordering.
6. `test_cli_has_three_modes`: filesystem read of CLI, assert `--detect`, `--dry-run`, `--apply` flags.

### L1 — SQLite template guards

7. `test_sqlite_template_has_no_killer_trigger_clean`: `sqlite3.connect(pyarchinit.sqlite)`, query `sqlite_master` WHERE `name='delete_media_table'`, assert 0 rows.
8. `test_sqlite_template_has_no_killer_trigger_db`: same on `pyarchinit_db.sqlite`.

### L1 — PG migration on fixture (skip offline)

9. `test_migration_detects_trigger_on_legacy_fixture`: load Volterra mini-fixture into PG, inject killer trigger via raw SQL, run `detect_killer_triggers`, assert `has_triggers=True`.
10. `test_migration_apply_drops_and_installs_fk`: same fixture, run `apply_migration`, assert triggers gone + FK installed + verify_post_migration True.
11. `test_migration_idempotent`: run `apply_migration` twice, second run finds nothing to fix, returns zero counts.
12. `test_migration_handles_orphans`: inject orphan rows in media_thumb_table + MTE, run migration, assert orphans cleaned and FK installs successfully.

### L1 — dry-run safety

13. `test_dry_run_rolls_back`: run with `dry_run=True`, assert state unchanged after call (triggers still present, no orphan deletion, no FK).

---

## 6. Out of scope (for this milestone)

- SQLite existing DB migration (FK retrofit deferred).
- Auto-detect on DB open (deferred — current pattern is manual menu only, same as node_uuid).
- Audit + fix of other PG DBs (festos2025, pyarchinit_v2): documented in memory, applied per-DB when reachable.
- Rewriting the original "rename propagator" trigger with `NEW != OLD`: skipped, marginal utility.

---

## 7. Versioning

- Version bump: `5.7.9.2-alpha → 5.7.9.3-alpha` (patch).
- yE-D target unchanged: `5.8.0-alpha`.
- yE-E unchanged: `5.8.1-alpha`.
- yE-Closure unchanged: `5.8.2-alpha`.

## 8. AC

- **AC-1**: After applying migration on khutm2-shaped DB (post-disaster), the killer triggers are absent + the two FK are installed + no orphans remain.
- **AC-2**: New PG installations from updated schema files have FK in place + no triggers. Verified via inspection of a fresh `psql -f pyarchinit_schema_clean.sql` on a temp DB.
- **AC-3**: New SQLite installations from updated binary templates have no killer trigger.
- **AC-4**: Migration is idempotent — second run is a no-op.
- **AC-5**: 5.7.9.3-alpha tag pushed with all schema + migration code. No yE-D timeline shift.

## 9. Rollback

- Pre-migration auto-backup via `pg_dump` covers data restore.
- Tag `pre-media-fk-migration` before applying any code changes.
- If FK installation fails post-orphan cleanup, the transaction rolls back automatically; orphans are NOT lost (rolled back too).
