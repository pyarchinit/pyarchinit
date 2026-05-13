# yE-D Pipeline + Policy — Execution Plan

**Spec**: `docs/superpowers/specs/2026-05-12-yed-import-pipeline-design.md` (amended 2026-05-13)
**Baseline**: `media-fk-migration-5.7.9.3-alpha` (commit `0919f5ce`, pushed)
**Target tag**: `yed-import-pipeline-5.8.0-alpha`
**Estimated**: ~4h end-to-end across 4 subagent-driven groups + USER GATE

---

## Pre-flight (Group 0 — orchestrator does this)

1. **Clean working tree** on `Stratigraph_00001`. `git status` clean except for any in-progress notes.
2. **Baseline tests**: `python -m pytest tests/sync/ tests/migrations/ -q` → must show **312 passed / 42 skipped** (post media-fk-migration baseline).
3. **Rollback safety tag**: `git tag pre-yed-d` (no push).
4. **Predecessor sanity**: `git log --oneline -1` shows `0919f5ce release(media-fk-migration): docs + version 5.7.9.3-alpha` at HEAD.
5. **Confirm fixture present**: `ls tests/sync/fixtures/em_demo_02_mini.graphml` — must exist (shipped in yE-C).

If any check fails → STOP and reconcile.

---

## Group A — `yed_rapporti_policy.py` (subagent)

**Subagent**: general-purpose
**Files created**:
- `modules/s3dgraphy/sync/yed_rapporti_policy.py` (~250 LOC)
- `tests/sync/test_yed_rapporti_policy.py` (7 L0 tests, ~200 LOC)

**Files modified**: none

**Commit message**: `feat(yE-D): folder-edge policy module with 4 active policies`

### Steps

1. Implement `FolderEdgePolicy` StrEnum + `FolderEdge` dataclass + `FolderEdgeReport` dataclass + `ExpandedRapporti` dataclass per spec § 5.
2. Implement `analyze_edges(graphml_path, classified, folders) → FolderEdgeReport`.
3. Implement `apply_policy(report, policy, *, all_folders, classified) → ExpandedRapporti` covering the 4 active branches SKIP / FAN_OUT / REPRESENTATIVE / SYNTHETIC.
4. SYNTHETIC branch returns ExpandedRapporti with `synthetic_us_rows: list[dict]` — each synthetic row has `node_uuid` (fresh UUID v7), `unita_tipo='VA'`, `us=<folder_label>`, plus the folder-edge rapporti rewired through this synthetic anchor.
5. Self-loop folder edges (source == target folder, e.g. nested folder member edge): MUST be filtered in ALL policies.
6. 7 L0 tests per spec § 5 line 198-206 (5 SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC + 1 folder-to-folder synthetic + 1 self-loop filter). Use the yE-C fixture `em_demo_02_mini.graphml` for `analyze_edges` count test; build minimal in-memory dataclass instances for the other 6.

### Acceptance

- 7 new L0 tests green.
- Suite: 312 → 319 passed locally.
- No file outside Group A scope touched.
- Subagent DOES NOT COMMIT — orchestrator reviews then commits.

---

## Group B — `yed_import_pipeline.py` (subagent)

**Subagent**: general-purpose
**Files created**:
- `modules/s3dgraphy/sync/yed_import_pipeline.py` (~400 LOC)
- `tests/sync/test_yed_import_pipeline.py` (8 L0 tests, ~250 LOC)

**Files modified**: none

**Commit message**: `feat(yE-D): import_yed_raw orchestrator + 5 write functions + paradata`

### Steps

1. Implement `_classify_destination(classified) → {sql_us, sql_inv, paradata, skipped}` per spec § 6.
2. Implement `_flatten_members(folder, all_folders) → list[str]` (recursive descent — folders can nest other folders).
3. Implement 5 standalone write functions:
   - `_write_us_rows(conn, ..., uuid_map_out)` — sql_us_classified + ParadataStore-equivalent for USV that ALSO need us_table rows. Returns `(count, uuid_map: dict[yed_id → node_uuid])`. Uses SQLAlchemy `text()` + named bind params (PG+SQLite compatible — N2 β).
   - `_write_inventario_rows(conn, ...)` — only SPECIAL_FIND kind.
   - `_write_periodizzazione_rows(conn, periods, sito)` — one row per PeriodCandidate. `datazione_iniziale` and `datazione_finale` stay NULL (period assignment without dates).
   - `_apply_yed_folder_dimensions(conn, folders, sito, uuid_map)` — UPDATE us_table SET <dim>=<value> via `WHERE node_uuid IN (...)` parameterized. Skip folders with `auto_dimension is None` or user_dimension == 'skip'.
   - `_write_rapporti(conn, expanded, sito, uuid_map)` — UPDATE us_table.rapporti via JSON array; also INSERT synthetic_us_rows when policy=SYNTHETIC. Each synthetic row gets node_uuid + unita_tipo='VA' + same sito.
4. Implement `_write_paradata_via_store(handle, paradata_classified, sito) → int` dispatching to ParadataStore API. **PropertyNode plan-time decision: Path B** — write PropertyNode standalone (no US linkage). Log warning per property: "PropertyNode `<label>` written without US linkage — yE-E dialog will let user assign target". This is the simpler + deferred-linkage path; saves ~60 LOC and matches the user's choice for no hooks (N6 α).
5. Implement `import_yed_raw(handle, graphml_path, sito, drafts, policy=SKIP, dry_run=False) → IngestResult`:
   - Single `engine.begin()` transaction (atomic per Q3 α).
   - Dispatch order: classify_destination → analyze_edges → apply_policy → write_us → write_inventario → write_periodizzazione → apply_folder_dimensions → write_rapporti → write_paradata.
   - On dry_run: raise `_DryRunRollback` after the last write (sentinel pattern from PG-C, reused in media-fk-migration).
   - On any Exception: transaction rolls back via `with engine.begin()` semantics; build `IngestResult(applied=0, errors=(str(e),), ...)` and return.
   - On success: build `IngestResult` with all counts + `parsed_drafts` populated from inputs.

6. 8 L0 tests per spec § 6 line 322-331 — use temp SQLite + tiny synthetic drafts; no need for em_demo_02 fixture at L0.

### Acceptance

- 8 new L0 tests green.
- Suite: 319 → 327 passed locally.
- DOES NOT COMMIT.

### Gotchas

- `_DryRunRollback` must be raised INSIDE `with engine.begin()` block and caught OUTSIDE (see `modules/s3dgraphy/sync/graph_ingestor.py` for the established pattern).
- `node_uuid` generation: import `uuid7` from `scripts/migrations/_2026_05_node_uuid_backfill_lib.py` to keep UUID consistency with backfill migration.
- `paradata.graphml` location for ParadataStore: use the existing `_workspace.py:_resolve_workspace_dir` resolver (no new path logic).

---

## Group C — Branch hook + vocab patch + L1 integration (subagent)

**Subagent**: general-purpose
**Files modified**:
- `modules/s3dgraphy/sync/graph_ingestor.py` — branch hook dispatch (lines 169-227) + add `"VirtualActivity": "VA"` to `_S3DGRAPHY_TYPE_TO_UNITA_TIPO` (line 1364)
- `gui/ui/Us_usm.ui` — add `<item><string>VA</string></item>` to `comboBox_unita_tipo` (near line 42712)

**Files created**:
- `tests/sync/test_yed_pipeline_integration.py` (7 L1 tests, ~400 LOC)

**Commit message**: `feat(yE-D): branch hook dispatch + VA vocab + 7 L1 integration tests`

### Steps

1. **Branch hook dispatch** in `graph_ingestor.py:169-227`:
   - Where `flavor = detect_flavor(graphml_path)` already detects "yed-raw", replace the current `_log_yed_summary(drafts)` + fall-through with: build the drafts dict + call `import_yed_raw(handle, graphml_path, sito, drafts, policy=SKIP, dry_run=dry_run)` + RETURN its IngestResult.
   - Sacred: pyarchinit-projected branch UNCHANGED.
   - Defensive: if `import_yed_raw` returns IngestResult with `applied=0` AND `errors`, return as-is (don't try to fall through).
2. **Vocab patch** — 2 lines total:
   - `graph_ingestor.py:1364` add `"VirtualActivity": "VA",` to the dict.
   - `gui/ui/Us_usm.ui` near line 42712 add the new combobox item. Verify the resulting XML is well-formed via `python -c "import xml.etree.ElementTree as ET; ET.parse('gui/ui/Us_usm.ui')"`.
3. **L1 integration tests** in `tests/sync/test_yed_pipeline_integration.py`:
   - `test_yed_d_end_to_end_skip_policy` — full import of `em_demo_02_mini.graphml` with SKIP, assert us_table populated correctly, no folder-edge rapporti written.
   - `test_yed_d_end_to_end_fan_out_policy` — same but FAN_OUT, assert N×M rapporti written.
   - `test_yed_d_end_to_end_representative_policy` — REPRESENTATIVE, assert first-member proxy used.
   - `test_yed_d_end_to_end_synthetic_policy` — SYNTHETIC, assert VA rows inserted + folder rapporti rewired through them.
   - `test_yed_d_paradata_written_via_store` — assert ParadataStore created paradata.graphml with N nodes.
   - `test_yed_d_dry_run_rolls_back` — full pipeline dry_run, assert empty DB after.
   - `test_yed_d_idempotent_on_re_run` — run twice, second run must error cleanly (UNIQUE constraint on (sito, us, area, unita_tipo)) without partial writes.
4. SQLite-only L1 tests (PG L1 via DbHandle is covered at unit level in Group B).

### Acceptance

- 9 new tests (2 vocab/hook L0 + 7 L1).
- Suite: 327 → 336 passed locally.
- AC-2: pyarchinit-projected branch unchanged — verify with `git diff modules/s3dgraphy/sync/graph_ingestor.py` showing only the yEd-raw branch + vocab map touched.
- UI XML still valid (etree parse succeeds).
- DOES NOT COMMIT.

### Gotchas

- `graph_ingestor.py:169-227` is delicate — read the FULL function before edit. Pyarchinit-projected branch lives in the same function; AC-2 requires it byte-identical.
- The UI XML edit must preserve indentation + line-ending style. Use grep to find the exact location of an existing `<item><string>` line and mirror its formatting.

---

## Group D — CLI + docs + version bump + tag (orchestrator does this)

**Files created**:
- `scripts/import_yed_graphml.py` (~150 LOC)
- `tests/sync/test_import_yed_graphml_cli.py` (2 tests, ~80 LOC)

**Files modified**:
- `metadata.txt` (5.7.9.3-alpha → 5.8.0-alpha)
- `dev_logs/CHANGELOG.md` (prepend `[5.8.0-alpha]` IT+EN entry)
- Memory files (`project_yed_import_progress.md` + `MEMORY.md`)

**Commit messages** (2 commits):
- `feat(yE-D): cli scripts/import_yed_graphml.py + 2 cli tests`
- `release(yE-D): docs + version 5.8.0-alpha`

### Steps

1. **CLI** per spec § 8 (argparse + dispatch + IngestResult summary). Mirror style of `scripts/migrations/2026_05_media_fk_cascade.py` (recent precedent) and `scripts/migrations/2026_05_node_uuid_backfill.py` (DbHandle pattern + `--db`/`--conn-str` mutex).
2. **2 CLI tests** per spec § 8 line 374-376.
3. **Version bump** 5.7.9.3 → 5.8.0-alpha.
4. **CHANGELOG IT+EN** — comprehensive section documenting: root cause (yE-C drafts had nowhere to land), 4 commit groups, 24 tests, no AC-2 regression, predecessor chain.
5. **Memory snapshot**: `project_yed_import_progress.md` table → yE-D row status PENDING → SHIPPED with tag + commits.
6. **Tag annotated**: `git tag -a yed-import-pipeline-5.8.0-alpha -m "..."`.
7. **USER GATE**: pause for manual QGIS smoke test:
   - Open SQLite project (fresh DB).
   - Menu → Import GraphML → select `em_demo_02_mini.graphml` (or similar yEd-raw).
   - Expected: dialog/progress shows import succeeds; verify us_table populated; verify no error log.
   - Open Pottery form on khutm2 PG; verify NO regression (still loads media — the AC-2 sacred check).
8. On `approvato`: `git push origin Stratigraph_00001 yed-import-pipeline-5.8.0-alpha`.

### Acceptance

- 2 new CLI tests + the previously merged content all green.
- Final suite: 336 → 338 passed locally / 343 online (PG-L1 of Group B run online).
- 2 commits + tag pushed.
- Memory updated.

---

## Test count progression

| Stage | Tests passed | Notes |
|---|---|---|
| Baseline (post media-fk-migration) | 312 | offline |
| After Group A | 319 | +7 L0 policy |
| After Group B | 327 | +8 L0 pipeline |
| After Group C | 336 | +2 vocab/hook L0 + +7 L1 integration |
| After Group D | 338 | +2 CLI |

Online (psycopg2 + PG fixture) adds the 5 PG-L1 currently skipped → 343.

---

## Versioning timeline (no shift downstream)

```
5.7.9.3-alpha → media-fk-migration  (shipped 2026-05-13)
5.8.0-alpha   → yE-D Pipeline       (THIS milestone)
5.8.1-alpha   → yE-E Dialog         (next, hooks rewire in import_yed_raw signature)
5.8.2-alpha   → yE-Closure          (docs + tutorials + RTD)
```

---

## Open plan-time decisions resolved upfront

| Decision | Value | Reason |
|---|---|---|
| **PropertyNode linkage** (spec § 6 Path A vs B) | **Path B** (standalone, no US linkage) | Aligns with N6 α (no hooks). yE-E dialog will let user assign target. Saves ~60 LOC. |
| **Vocab whitelist source** (spec § 7) | **Pure code edits** (UI XML + graph_ingestor dict) | No JSON file or DB CHECK constraint exists (verified during brainstorm). |
| **DbHandle for write functions** | **Yes** (N2 β) | Engine.begin() pattern works on both backends; ParadataStore already cross-backend (PG-D). |

---

## Rollback

- Pre-yE-D safety tag: `pre-yed-d` posted in Group 0.
- Each Group's commit is isolatable — `git revert <sha>` for any single group.
- If branch hook integration in Group C breaks pyarchinit-projected imports (AC-2 violation), `git revert <Group C sha>` brings the legacy path back without touching the new policy/pipeline modules.
