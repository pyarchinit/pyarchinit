# media-fk-migration execution plan (5.7.9.3-alpha)

**Spec**: `docs/superpowers/specs/2026-05-13-media-fk-migration-design.md`
**Baseline**: `pg-bv2-hotfix-5.7.9.2-alpha` (commit `c26e7763`)
**Target tag**: `media-fk-migration-5.7.9.3-alpha`
**Estimated**: ~2h end-to-end (4 commit groups)

---

## Pre-flight (Group 0)

Before any code touches:

1. Verify clean working tree on `Stratigraph_00001`: `git status` must show no uncommitted changes (the prior session committed pg-bv2-hotfix + pg-media-fix already).
2. Run baseline test suite: `python -m pytest tests/sync/ tests/migrations/ -q` — **must show 304 passed / 37 skipped** as the post-hotfix baseline. Save this number; final must be ≥ 304 + new tests.
3. Lay down rollback safety tag: `git tag pre-media-fk-migration` (no push needed).
4. Confirm SQLite templates currently contain the killer trigger (sanity check):
   ```bash
   sqlite3 resources/dbfiles/pyarchinit.sqlite "SELECT name FROM sqlite_master WHERE type='trigger' AND name='delete_media_table';"
   # Expected: prints "delete_media_table"
   ```

If baseline diverges → STOP and reconcile before proceeding.

---

## Group A — Source schema changes (PG SQL files)

**Subagent**: general-purpose
**Files touched**:
- `resources/dbfiles/pyarchinit_schema_clean.sql`
- `resources/dbfiles/pyarchinit_schema_updated.sql`

**Commit message**: `feat(media-fk-migration): replace killer triggers with FK ON DELETE CASCADE in PG schemas`

### Steps

1. In `pyarchinit_schema_clean.sql`, locate and **delete**:
   - The `CREATE OR REPLACE FUNCTION delete_media_table()` block (lines ~3548-3568).
   - The `ALTER FUNCTION delete_media_table()` line.
   - The DO $$ ... CREATE TRIGGER delete_media_table block (~3573-3580).
   - The `CREATE OR REPLACE FUNCTION delete_media_to_entity_table()` block.
   - The matching `ALTER FUNCTION` and DO $$ ... CREATE TRIGGER block.
   - Approximate range: lines 3548-3635. Verify by grep'ing for the trigger names after the edit — should return 0 matches.

2. Same surgery on `pyarchinit_schema_updated.sql` (lines ~3524-3611).

3. After the table definitions for `media_table`, `media_thumb_table`, `media_to_entity_table` in both files, append the FK CASCADE definitions:

   ```sql
   --
   -- media_fk_migration 5.7.9.3-alpha: master → derived cascade
   -- replaces the pre-5.7.9.3 killer triggers on media_thumb_table
   --
   ALTER TABLE media_thumb_table
     ADD CONSTRAINT fk_media_thumb_to_media
     FOREIGN KEY (id_media) REFERENCES media_table(id_media) ON DELETE CASCADE;

   ALTER TABLE media_to_entity_table
     ADD CONSTRAINT fk_mte_to_media
     FOREIGN KEY (id_media) REFERENCES media_table(id_media) ON DELETE CASCADE;
   ```

   Place after CREATE TABLE statements for all 3 tables but before any DATA loads.

4. Skip `pyarchinit_update_postgres.sql` — already has the trigger commented out (pre-existing fix attempt).

5. Verify result:
   ```bash
   grep -c "CREATE TRIGGER delete_media_table\|CREATE OR REPLACE FUNCTION delete_media_table" \
     resources/dbfiles/pyarchinit_schema_clean.sql \
     resources/dbfiles/pyarchinit_schema_updated.sql
   # Expected: 0 0
   grep -c "fk_media_thumb_to_media\|fk_mte_to_media" \
     resources/dbfiles/pyarchinit_schema_clean.sql \
     resources/dbfiles/pyarchinit_schema_updated.sql
   # Expected: 2 2
   ```

### Tests added (this commit)

- `tests/migrations/test_media_fk_migration.py`:
  - `test_pg_schema_clean_has_no_killer_trigger`
  - `test_pg_schema_updated_has_no_killer_trigger`
  - `test_pg_schema_clean_has_fk_cascade`
  - `test_pg_schema_updated_has_fk_cascade`

All 4 must pass.

### Acceptance

- All grep checks pass.
- 4 new L0 tests green.
- Existing 304-passed baseline unchanged.

---

## Group B — Migration library + CLI

**Subagent**: general-purpose
**Files created**:
- `scripts/migrations/_2026_05_media_fk_cascade_lib.py` (pure library)
- `scripts/migrations/2026_05_media_fk_cascade.py` (CLI)

**Files touched**:
- `tests/migrations/test_media_fk_migration.py` (extend)

**Commit message**: `feat(media-fk-migration): migration lib + CLI for legacy PG DBs`

### Steps

1. Create `_2026_05_media_fk_cascade_lib.py` with the 4 public functions from spec § 4.3. Each function takes a `DbHandle` (imported from `modules.s3dgraphy.sync._db_handle`). Internal helpers use raw SQL via `handle.engine.connect()` / `handle.engine.begin()`.

   Key implementation details:
   - `detect_killer_triggers`: query `information_schema.triggers` WHERE `event_object_table='media_thumb_table'` AND `trigger_name IN ('delete_media_table', 'delete_media_to_entity_table')`. Returns list of found names.
   - `count_orphans`: two `LEFT JOIN ... WHERE m.id_media IS NULL` queries against media_thumb_table and media_to_entity_table. Sample up to 5 rows per table.
   - `apply_migration`: single transaction via `engine.begin()`. Order matters: 1) DROP TRIGGER, 2) DROP FUNCTION, 3) DELETE orphans, 4) ADD CONSTRAINT, 5) verify. If `dry_run=True`, raise a custom `_DryRunRollback` sentinel after step 4 (same pattern as `GraphIngestor._DryRunRollback`).
   - `verify_post_migration`: query `pg_constraint` for the two FK names + `information_schema.triggers` for absence of killers.

2. Create CLI `2026_05_media_fk_cascade.py` with `argparse`:
   - Mutually exclusive `--detect / --dry-run / --apply`.
   - `--conn-str <pg-url>` required.
   - On `--apply`: invoke `auto_backup_postgres(conn_str)` from `_common.py` BEFORE running. Same env override `PYARCHINIT_PG_DUMP_TIMEOUT`.
   - Output JSON-line summary of the result dict.

3. Idempotency contract: if trigger absent and FK present, all functions return `{'no_op': True, ...}` with zero deletes.

### Tests added

Extend `tests/migrations/test_media_fk_migration.py`:
- `test_migration_lib_has_required_api` (source-inspection, L0)
- `test_cli_has_three_modes` (source-inspection, L0)
- `test_migration_detects_trigger_on_pg_fixture` (L1 PG, skip if `pg_with_volterra` unavailable)
- `test_migration_apply_drops_and_installs_fk` (L1 PG)
- `test_migration_idempotent` (L1 PG)
- `test_migration_handles_orphans` (L1 PG, injects orphans via raw SQL pre-apply)
- `test_dry_run_rolls_back` (L1 PG)

### Acceptance

- 10 total tests in `test_media_fk_migration.py`, all green (PG ones may skip if psycopg2 absent).
- `python scripts/migrations/2026_05_media_fk_cascade.py --detect --conn-str <khutm2>` returns `{has_triggers: false}` (already fixed live earlier today).
- 304 + 10 = 314 passed minimum (or 308 with 6 PG-L1 skipped offline).

---

## Group C — SQLite template patch + QGIS menu wire

**Subagent**: general-purpose
**Files touched**:
- `resources/dbfiles/pyarchinit.sqlite` (binary, in-place)
- `resources/dbfiles/pyarchinit_db.sqlite` (binary, in-place)
- `pyarchinitPlugin.py` (menu entry + handler)

**Commit message**: `feat(media-fk-migration): sqlite template cleanup + qgis menu wire`

### Steps

1. **Patch SQLite templates** (Python helper, NOT shipped — run once at commit time):

   ```python
   import sqlite3
   for db in ['resources/dbfiles/pyarchinit.sqlite',
              'resources/dbfiles/pyarchinit_db.sqlite']:
       conn = sqlite3.connect(db)
       conn.execute('DROP TRIGGER IF EXISTS delete_media_table')
       conn.execute('DROP TRIGGER IF EXISTS delete_media_to_entity_table')
       conn.commit(); conn.close()
   ```

   After running, verify:
   ```bash
   sqlite3 resources/dbfiles/pyarchinit.sqlite \
     "SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE 'delete_media%';"
   # Expected: empty
   ```

   Commit the binary template changes. (Binary diff is small — just removes the trigger metadata rows.)

2. **Add QGIS menu entry** in `pyarchinitPlugin.py`. Find the existing node_uuid migration menu wire (line ~2693) and add a sibling entry below:

   ```python
   action_media_fk = QAction(
       self.tr("Fix trigger media (cascade pericoloso)"),
       self.iface.mainWindow())
   action_media_fk.triggered.connect(self._run_media_fk_migration)
   migrations_menu.addAction(action_media_fk)
   ```

3. **Add handler** `_run_media_fk_migration` next to `_run_uuid_backfill_migration` (line ~2771). Structure (~80 LOC):

   - Resolve `db_manager` → `DbHandle` via `_resolve_db_handle`.
   - If not `handle.is_postgres`: show info `QMessageBox` "PG-only migration, skip" and return.
   - Call `detect_killer_triggers(handle)`. If empty: show info "DB già pulito" and return.
   - Call `count_orphans(handle)`. Build dialog text with counts + 3-sample preview.
   - Show `QMessageBox.question` with Sì/No.
   - On Yes: call `auto_backup_postgres(handle.conn_str)` → show backup path in progress.
   - Call `apply_migration(handle, dry_run=False)`.
   - Show summary dialog: triggers dropped + orphans cleaned + FK installed.

### Tests added

- `test_sqlite_template_has_no_killer_trigger_clean` (L1 SQLite, opens template, queries sqlite_master)
- `test_sqlite_template_has_no_killer_trigger_db` (L1 SQLite, same)

### Acceptance

- Both SQLite templates trigger-free (verified via sqlite_master query).
- QGIS plugin loads without errors.
- Menu entry visible and clickable (manual smoke).
- 2 new L1 SQLite tests green.

---

## Group D — Docs, version bump, tag, push

**Subagent**: general-purpose
**Files touched**:
- `metadata.txt` (version bump)
- `dev_logs/CHANGELOG.md` (bilingual IT + EN entry)
- Memory files (`MEMORY.md` index update + `project_khutm2_media_trigger_disaster.md` cross-link)

**Commit message**: `release(media-fk-migration): docs + version 5.7.9.3-alpha`

### Steps

1. Bump `metadata.txt`: `version=5.7.9.2-alpha → 5.7.9.3-alpha`.

2. Prepend new section to `dev_logs/CHANGELOG.md`:
   - Italian: root cause + cosa cambia (PG schema + SQLite template + migration lib + CLI + menu).
   - English: same.
   - Test count delta: 304 → 304+N passed.
   - Versioning note: no shift yE-D.

3. Update memory:
   - `MEMORY.md`: extend the trigger-disaster line with " — fix shipped as `media-fk-migration-5.7.9.3-alpha` (commit X, tag obj Y)".
   - `project_khutm2_media_trigger_disaster.md`: append "Fix shipped 2026-05-13 as `media-fk-migration-5.7.9.3-alpha`" section.

4. Tag: `git tag -a media-fk-migration-5.7.9.3-alpha -m "media-fk-migration: replace killer triggers with FK CASCADE"`.

5. **USER GATE**: pause for manual user smoke test in QGIS:
   - Open project on khutm2 (already fixed live earlier today).
   - Open `Plugins → pyArchInit → Migrazioni → Fix trigger media`.
   - Expected: dialog "DB già pulito" (since khutm2 was bonificato live).
   - Then test on another fresh PG DB that still has triggers: expected detect + dialog + apply success.

6. Only after user `approvato`: push branch + tag.

### Acceptance

- AC-1, AC-2, AC-3, AC-4, AC-5 from spec all met.
- User confirms in QGIS smoke test.
- Branch `Stratigraph_00001` + tag `media-fk-migration-5.7.9.3-alpha` pushed to `origin`.

---

## Group E (Optional) — Memory snapshot + close

**Files**:
- `~/.claude/projects/.../memory/project_khutm2_media_trigger_disaster.md` (cross-link to the tag)

**Steps**:
1. Record final state.
2. Mark task #288 completed.
3. Optionally: close out the milestone with a one-line update in MEMORY.md.

---

## Test count progression

| Stage | Tests passed | Notes |
|---|---|---|
| Baseline | 304 | post pg-bv2-hotfix |
| After Group A | 308 | +4 L0 schema checks |
| After Group B (offline) | 310 | +2 L0 (api + CLI), 6 PG-L1 skipped |
| After Group B (PG online) | 316 | all 6 PG-L1 run |
| After Group C | 312 (offline) / 318 (online) | +2 L1 SQLite template |
| Group D | unchanged | docs only |

---

## Versioning timeline (no shift)

```
5.7.9-alpha     → pg-bv2          (shipped 2026-05-12)
5.7.9.1-alpha   → pg-media-fix    (shipped 2026-05-13 morning)
5.7.9.2-alpha   → pg-bv2-hotfix   (shipped 2026-05-13 morning)
5.7.9.3-alpha   → media-fk-migration (THIS milestone)
5.8.0-alpha     → yE-D Pipeline   (next, unchanged)
5.8.1-alpha     → yE-E Dialog     (unchanged)
5.8.2-alpha     → yE-Closure      (unchanged)
```
