# yE-D Pipeline + Policy — Design Spec

**Date:** 2026-05-12 (amended 2026-05-12 post PG-UIFix)
**Branch:** Stratigraph_00001
**Predecessor tag:** `pg-bv2-5.7.9-alpha` (commit TBD after Group A ships) — was previously `pg-uifix-5.7.8-alpha` then `pg-uuidfix-5.7.8.1-alpha` before PG-Bv2 interleaved
**Target tag:** `yed-import-pipeline-5.8.0-alpha` (shifted from `5.7.9-alpha` because PG-Bv2 reserved that tag 2026-05-12)

> **Note** — PG-UIFix milestone interleaved between yE-C and yE-D, reserving `pg-uifix-5.7.8-alpha`. PG-UUIDFix then reserved `pg-uuidfix-5.7.8.1-alpha`. PG-Bv2 then reserved `pg-bv2-5.7.9-alpha`. yE-D now shifts to: `yed-import-pipeline-5.8.0-alpha`. yE-E and yE-Closure also shift to `5.8.1-alpha` and `5.8.2-alpha`.

---

## 1. Goal

Ship the fourth milestone of the 6-milestone yEd-aware graphml import rollout. yE-D is the **biggest and most consequential milestone**: it introduces the FIRST real DB writes from the yEd-raw branch. After yE-D ships, importing `EM_demo_02.graphml` (or any yEd-raw file) will produce correctly populated `us_table` + `inventario_materiali_table` + `periodizzazione_table` + paradata, instead of the buggy 17-rows-in-us_table behavior from before.

Components shipped:

1. **`modules/s3dgraphy/sync/yed_rapporti_policy.py`** — `FolderEdgePolicy` enum with 4 active policies (SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC), `analyze_edges()`, `apply_policy()`
2. **`modules/s3dgraphy/sync/yed_import_pipeline.py`** — orchestrator `import_yed_raw()` + 5 standalone write functions + ParadataStore integration
3. **`scripts/import_yed_graphml.py`** — CLI wrapper for batch/CI use
4. **Vocab patch**: add `'VA'` (VirtualActivity) to `UNITA_TIPO` whitelist so SYNTHETIC policy can INSERT folder-derived synthetic US rows
5. **Branch hook MAJOR change** in `graph_ingestor.py:169-227`: dispatch to `import_yed_raw()` and RETURN its result (NO fall-through to legacy for yEd-raw)
6. **24 new tests**: 15 L0 + 7 L1 integration + 2 CLI

## 2. Decisions captured during brainstorming (2026-05-12)

7 delta questions resolved:

| Q | Decision | Rationale |
|---|---|---|
| Q1 DB-write strategy | **β — Standalone write functions** in `yed_import_pipeline.py` | AC-2 zero-risk, clean separation, no entanglement with legacy `_run()` |
| Q2 Folder dimension SQL | **β — New `_apply_yed_folder_dimensions()` function** | yEd-raw graphmls don't have `pyarchinit.<kind>` data keys → existing `_apply_group_folders_to_sql` doesn't apply; clean parallel path |
| Q3 Error policy | **α — Atomic only** (transaction rollback on any error) | Matches PG-C precedent; `failure_mode` flag deferred to Phase 4 |
| Q4 VSF/D/Property destination | **α — yE-D writes paradata via `ParadataStore` API** | User gets complete picture after import; scope grows but value justifies |
| Q5 SYNTHETIC policy | **β — Implement + vocab patch** | yE-D ships all 4 policies functional; vocab patch ~50 LOC |
| Q6 Single milestone vs split | **α — Single yE-D** | No clean file-boundary split possible; subagent capacity proven at ~1000 LOC in yE-C |
| Q7 L1 test strategy | **δ — 7 L1 tests** (5 per-policy E2E + 2 paradata) | First DB writes need serious coverage; per-policy diagnostic isolation |

## 3. Inherited from predecessors

- yE-A: `yed_detector.py` (flavor detection) — unchanged
- yE-B: `yed_classifier.py` (ClassificationKind + classify_leaves) — consumed by pipeline
- yE-C: `yed_table_parser.py` (PeriodCandidate) + `yed_group_walker.py` (FolderCandidate) — consumed by pipeline
- yE-C: `IngestResult.parsed_drafts: dict | None` field — populated by `import_yed_raw()` at end
- PG-C: `_DryRunRollback` sentinel pattern — reused for dry_run mode
- Phase 3: `DbHandle` + `_resolve_db_handle` from Foundation — pipeline consumes
- Phase 3: `_workspace.py:_resolve_workspace_dir` for paradata.graphml location

## 4. Architecture

### Files created (7)

| Path | Responsibility | LOC est |
|---|---|---|
| `modules/s3dgraphy/sync/yed_rapporti_policy.py` | `FolderEdgePolicy` StrEnum + dataclasses + `analyze_edges()` + `apply_policy()` (4 policies active) | ~250 |
| `modules/s3dgraphy/sync/yed_import_pipeline.py` | `import_yed_raw()` orchestrator + 5 SQL write functions + ParadataStore integration + helpers | ~400 |
| `scripts/import_yed_graphml.py` | CLI wrapper: argparse + invokes pipeline + prints `IngestResult` summary | ~150 |
| `tests/sync/test_yed_rapporti_policy.py` | 7 L0 tests | ~200 |
| `tests/sync/test_yed_import_pipeline.py` | 8 L0 tests (helpers + write functions in isolation) | ~250 |
| `tests/sync/test_yed_pipeline_integration.py` | 7 L1 integration tests on `em_demo_02_mini.graphml` | ~400 |
| `tests/sync/test_import_yed_graphml_cli.py` | 2 CLI tests via subprocess | ~80 |

### Files modified (5)

| Path | Change | LOC delta |
|---|---|---|
| `modules/s3dgraphy/sync/graph_ingestor.py:169-227` | **MAJOR CHANGE**: branch hook dispatches to `import_yed_raw()` and RETURNS its `IngestResult` (no fall-through to legacy for yEd-raw) | +30/-20 |
| Vocab source (located plan-time) | Add `'VA'` to `UNITA_TIPO` whitelist for SYNTHETIC policy | ~50 |
| `metadata.txt` | 5.7.9-alpha → 5.8.0-alpha | 1 |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.8.0-alpha]` section | ~60 |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Prepend yE-D section above yE-C | ~50 |

### Files NOT touched

- `yed_detector.py`, `yed_classifier.py`, `yed_table_parser.py`, `yed_group_walker.py` — inherited as-is
- `tests/sync/fixtures/em_demo_02_mini.graphml` — reused
- Pyarchinit-projected branch of `populate_list()` and `_run()` — sacred (AC-2)
- `ingest_result.py` — `parsed_drafts` already added in yE-C
- DB schema (no migrations; vocab is in-memory whitelist)
- `requirements.txt` (no new deps)

### Total LOC

- Production: ~880 (~800 new + ~80 modify)
- Test: ~930 (~450 L0 + ~480 L1+CLI)
- Docs: ~110
- **Grand total: ~1920 LOC** — biggest milestone in the rollout

### Data flow yE-D (dispatch instead of fall-through)

```
populate_list(graph, graphml_path=..., ...)
  → detect_flavor → "yed-raw"
  → import_yed_raw(handle, graphml_path, sito, drafts, policy=SKIP, dry_run)
    ↓
    classify_leaves + extract_periods + walk_folders (build drafts)
    classify_destination(classified) → {sql_us, sql_inv, paradata, skipped}
    analyze_edges(...) + apply_policy(...) → ExpandedRapporti
    ↓ (atomic transaction)
    1. _write_us_rows → assigns node_uuid to each US row
    2. _write_inventario_rows → inventario_materiali_table for SF*
    3. _write_periodizzazione_rows → periodizzazione_table for periods
    4. _apply_yed_folder_dimensions → UPDATE us_table SET <dim>=<value>
    5. _write_rapporti → UPDATE us_table.rapporti per policy
    6. _write_paradata_via_store → ParadataStore writes for USV/DOC/VSF/COMB/PROP
    ↓
    if dry_run: raise _DryRunRollback (auto-rollback)
    ↓
    return IngestResult with parsed_drafts populated
  → RETURN from populate_list() with yE-D result
  → legacy path NOT executed for yEd-raw
```

## 5. `yed_rapporti_policy.py` specification

### Public API

```python
from enum import StrEnum
from dataclasses import dataclass, field
from pathlib import Path


class FolderEdgePolicy(StrEnum):
    SKIP           = "skip"            # default
    FAN_OUT        = "fan_out"         # expand folder-edge to N×M leaf pairs
    REPRESENTATIVE = "representative"  # use first member of folder as proxy
    SYNTHETIC      = "synthetic"       # create us_table row per folder (unita_tipo='VA')


@dataclass
class FolderEdge:
    source_id: str
    target_id: str
    source_is_folder: bool
    target_is_folder: bool
    edge_type: str | None  # e.g., "covers" / "cuts" / None for generic


@dataclass
class FolderEdgeReport:
    total_edges: int
    leaf_to_leaf: list[tuple[str, str, str | None]]  # (src, tgt, edge_type)
    folder_touching: list[FolderEdge]


@dataclass
class ExpandedRapporti:
    rapporti: list[tuple[str, str, str | None]]
    synthetic_us_rows: list[dict] = field(default_factory=list)  # for SYNTHETIC
    skipped_count: int = 0


def analyze_edges(
    graphml_path: Path | str,
    folder_ids: set[str],
) -> FolderEdgeReport:
    """Parse graphml edges; classify each as leaf-to-leaf or folder-touching."""


def apply_policy(
    report: FolderEdgeReport,
    policy: FolderEdgePolicy,
    folder_members: dict[str, list[str]],  # folder_id → flattened descendants
) -> ExpandedRapporti:
    """Apply selected policy to folder-touching edges."""
```

### Policy semantics

- **SKIP**: `folder_touching` edges are dropped; only `leaf_to_leaf` survives in `ExpandedRapporti.rapporti`. `skipped_count = len(folder_touching)`.
- **FAN_OUT**: each `(folder_A, leaf_X)` with N flattened members → N edges `(m_i, X)` in `rapporti`. Folder-to-folder explodes to N×M pairs. `synthetic_us_rows = []`.
- **REPRESENTATIVE**: each folder-edge resolved to its first leaf-member (deterministic by document order). Folder-to-folder → first×first.
- **SYNTHETIC**: each folder produces a synthetic dict in `synthetic_us_rows` with `{us: <auto_value>, unita_tipo: 'VA', area: '1', sito: <sito>, ...}`. Edges to folders are translated to edges targeting the synthetic US. Requires vocab patch.

### 7 L0 tests

| # | Test name |
|---|---|
| 1 | `test_analyze_edges_em_demo_02_mini_counts` |
| 2 | `test_apply_skip_policy_drops_folder_edges` |
| 3 | `test_apply_fan_out_explodes_n_x_m` |
| 4 | `test_apply_representative_uses_first_member` |
| 5 | `test_apply_synthetic_creates_va_rows` |
| 6 | `test_apply_synthetic_with_folder_to_folder_edge` |
| 7 | `test_self_loop_folder_skipped_in_all_policies` |

## 6. `yed_import_pipeline.py` specification

### Destination groups (constants)

```python
_SQL_US_KINDS = {
    ClassificationKind.US_REAL,
    ClassificationKind.US_MASONRY,
    ClassificationKind.US_DOCUMENTARY,
}
_SQL_INVENTARIO_KINDS = {ClassificationKind.SPECIAL_FIND}
_PARADATA_KINDS = {
    ClassificationKind.USV_VIRTUAL,
    ClassificationKind.USV_FORMAL,
    ClassificationKind.VIRTUAL_FIND,
    ClassificationKind.DOCUMENT,
    ClassificationKind.COMBINER,
    ClassificationKind.PROPERTY,
}
```

### Public API

```python
def import_yed_raw(
    handle: DbHandle,
    graphml_path: Path | str,
    sito: str,
    drafts: dict,
    policy: FolderEdgePolicy = FolderEdgePolicy.SKIP,
    dry_run: bool = False,
) -> IngestResult:
    """Orchestrate yEd-raw graphml import.

    Args:
        handle: DbHandle for the target DB (SQLite or PostgreSQL).
        graphml_path: source .graphml file (already detected as yEd-raw).
        sito: target site name (forced onto every row).
        drafts: output from yE-C parsers (classified/periods/folders).
        policy: rapporti folder-edge policy (default SKIP).
        dry_run: if True, transaction is rolled back at the end via
            `_DryRunRollback` sentinel; IngestResult still reports counts.

    Returns:
        IngestResult with applied/inserted/updated/skipped counts +
        parsed_drafts populated with classified/periods/folders +
        rapporti_skipped + paradata_written.

    Error policy: atomic. On any exception, transaction rolls back and
    IngestResult.applied=0, errors=(str(e),).
    """
```

### 5 standalone SQL write functions

```python
def _classify_destination(classified: list[ClassifiedNode]) -> dict:
    """Split classified leaves into write destinations."""

def _flatten_members(folder: FolderCandidate,
                     all_folders: list[FolderCandidate]) -> list[str]:
    """Recursive flatten: direct members + nested folders' members."""

def _write_us_rows(conn, sql_us_classified, sito,
                   periods_map, folders_map) -> tuple[int, dict]:
    """INSERT INTO us_table. Returns (count, uuid_map: dict[yed_id → node_uuid])."""

def _write_inventario_rows(conn, sql_inv_classified, sito, ...) -> int:
    """INSERT INTO inventario_materiali_table for SF* leaves."""

def _write_periodizzazione_rows(conn, periods, sito) -> int:
    """INSERT INTO periodizzazione_table for each PeriodCandidate.
    datazione_iniziale + datazione_finale stay NULL."""

def _apply_yed_folder_dimensions(conn, folders, sito, uuid_map) -> int:
    """For each FolderCandidate with auto_dimension is not None and != 'skip':
    UPDATE us_table SET <user_dimension>=<user_value> WHERE node_uuid IN (
        <flatten_members(folder, all_folders)>
    )."""

def _write_rapporti(conn, expanded: ExpandedRapporti,
                    sito, uuid_map) -> int:
    """For each (src_leaf, tgt_leaf, edge_type) in expanded.rapporti:
    UPDATE us_table.rapporti to JSON list. Also INSERT synthetic_us_rows
    when policy=SYNTHETIC (each synthetic row gets node_uuid, unita_tipo='VA')."""
```

### ParadataStore integration

```python
def _write_paradata_via_store(handle, paradata_classified, sito) -> int:
    """For each paradata leaf, dispatch to ParadataStore API:
      USV_VIRTUAL / USV_FORMAL → store.add_virtual_us(label, ...)
      DOCUMENT                  → store.add_document(url=label, ...)
      VIRTUAL_FIND              → store.add_virtual_find(label, ...) (if API exists)
      COMBINER                  → store.add_combiner(label, ...) (if API exists)
      PROPERTY                  → see PropertyNode plan-time decision below

    Returns count of paradata writes attempted (regardless of API
    availability — unsupported ones logged as skip).
    """
```

### PropertyNode plan-time decision

Plan-writing must investigate `paradata_store.py` API surface and decide one of:

- **Path A**: yE-D writes PropertyNode with target US linkage (parse yEd edges to find which US the property describes). Requires edge parsing logic in pipeline. +60 LOC.
- **Path B**: yE-D writes PropertyNode standalone (no US linkage); log "PropertyNode `<label>` written without US linkage — yE-E dialog will let user assign target". Simpler, deferred linkage. +10 LOC.

Spec defers to plan-writing. Documented in §12 (out of scope) as: "PropertyNode linkage logic is plan-time decision based on `paradata_store.py` API capabilities".

### 8 L0 tests

| # | Test name |
|---|---|
| 1 | `test_classify_destination_splits_correctly` |
| 2 | `test_flatten_members_recursive` |
| 3 | `test_write_us_rows_assigns_node_uuid` |
| 4 | `test_write_inventario_rows_uses_special_find_kind` |
| 5 | `test_write_periodizzazione_rows_creates_one_per_period` |
| 6 | `test_apply_yed_folder_dimensions_updates_attivita_column` |
| 7 | `test_dry_run_rollback_sentinel_works` |
| 8 | `test_atomic_rollback_on_integrity_error` |

## 7. Vocab patch for SYNTHETIC policy

SYNTHETIC creates `us_table` rows with `unita_tipo='VA'`. The current `UNITA_TIPO` whitelist (location TBD plan-time, likely `vocab_provider.py` or JSON in `ext_libs/s3dgraphy/mappings/pyarchinit/`) does not include `'VA'`.

### Plan-time investigation steps

```bash
grep -rln "UNITA_TIPO\|unita_tipo.*whitelist\|UNITA_TIPI" modules/ ext_libs/s3dgraphy/mappings/
```

Find:
1. Whether whitelist is Python constant or JSON
2. Whether DB schema has CHECK constraint on `us_table.unita_tipo`
3. Whether `vocab_provider` validates incoming `unita_tipo` values

### Patch strategy

- **If pure Python whitelist**: add `'VA'` directly to the tuple/set definition + add a comment block: `# yE-D (5.8.0-alpha): 'VA' added for FolderEdgePolicy.SYNTHETIC` virtual activity rows`
- **If JSON**: add `'VA'` to the relevant JSON file; update vocab_provider to reload if needed
- **If DB CHECK constraint**: schema migration required → escalate to plan author, possibly defer SYNTHETIC implementation again

Documented as plan-time decision tree.

## 8. CLI wrapper `scripts/import_yed_graphml.py`

```bash
python -m scripts.import_yed_graphml /path/to/file.graphml \
    --site <sito> \
    --db /path/to/sqlite.db \    # OR --conn-str <postgres-url>
    --policy skip \              # skip / fan_out / representative / synthetic
    --auto-defaults \            # no prompts (uses auto_* values from classifier)
    --dry-run                    # transaction rollback at the end
```

Output: `IngestResult` summary printed to stdout (counts + parsed_drafts breakdown).

Logging at INFO level by default; `--verbose` raises to DEBUG.

### 2 CLI tests

| # | Test name |
|---|---|
| 1 | `test_cli_argparse_basic` (parse args, build context, no execution) |
| 2 | `test_cli_dry_run_subprocess_on_mini_fixture` (full subprocess.run + assert DB stays empty after --dry-run) |

## 9. Branch hook MAJOR change

The yE-C hook orchestrated drafts and logged a 3-line summary. yE-D **dispatches to the pipeline and returns its result** — no fall-through to legacy for yEd-raw graphmls.

### Code change (in `graph_ingestor.py:169-227`)

```python
# yE-A + yE-B + yE-C + yE-D: yEd-raw dispatched to dedicated pipeline.
# Returns import_yed_raw() result directly. Legacy path NOT executed
# for yEd-raw imports.
if graphml_path is not None:
    try:
        from .yed_detector import detect_flavor
        if detect_flavor(graphml_path) == "yed-raw":
            from .yed_classifier import classify_leaves
            from .yed_table_parser import extract_periods
            from .yed_group_walker import walk_folders
            from .yed_import_pipeline import (
                import_yed_raw, FolderEdgePolicy,
            )
            drafts = {
                "classified": classify_leaves(graphml_path),
                "periods": extract_periods(graphml_path),
                "folders": walk_folders(graphml_path),
            }
            # MVP: SKIP policy default. yE-E dialog will let user choose.
            return import_yed_raw(
                handle=handle, graphml_path=graphml_path,
                sito=sito, drafts=drafts,
                policy=FolderEdgePolicy.SKIP, dry_run=dry_run,
            )
    except Exception as e:
        # Pipeline crashed; degrade to legacy (logged but not user-visible
        # as error; user will see partial broken ingest from legacy).
        import logging
        logging.getLogger(__name__).warning(
            "yE-D pipeline failed: %s — falling through to legacy.", e,
        )
# -- pyarchinit-projected path UNCHANGED below --
```

**Key property**: when yEd-raw + pipeline succeeds → `return` from `populate_list()` immediately with the yE-D `IngestResult`. The legacy `_run()` is NOT called for yEd-raw. The pyarchinit-projected branch continues unchanged.

## 10. Test strategy global

### 7 L1 integration tests

| # | Test name | Verifies |
|---|---|---|
| 1 | `test_pipeline_em_demo_02_mini_end_to_end_skip_default` | E2E with SKIP: us_table 2 rows, inventario_materiali 1 row, periodizzazione_table 2 rows, folder dimensions populated, leaf-to-leaf rapporti only |
| 2 | `test_pipeline_em_demo_02_mini_fan_out` | FAN_OUT explodes folder edges to N×M leaf pairs |
| 3 | `test_pipeline_em_demo_02_mini_representative` | REPRESENTATIVE uses first folder member as proxy |
| 4 | `test_pipeline_em_demo_02_mini_synthetic` | SYNTHETIC creates us_table rows with `unita_tipo='VA'` for VA01/AR01 + edges connect to them |
| 5 | `test_pipeline_dry_run_rollback` | dry_run=True returns counts but us_table stays EMPTY |
| 6 | `test_pipeline_writes_paradata_node_types` | ParadataStore receives correct writes |
| 7 | `test_pipeline_propertynode_handling` | PROPERTY classification handled per plan-time decision |

### Total new tests

- L0 policy: 7
- L0 pipeline: 8
- L1 integration: 7
- L1 CLI: 2
- **Total: 24 new tests**

### Test count progression

| Milestone | Passed | Skipped |
|---|---|---|
| Pre yE-D | 289 | 33 |
| Post yE-D Group A | 313 | 33 |
| Post yE-D Group B/C | 313 | 33 |
| PG online + psycopg2 | 321 | 12 |

### Regression gates after Group A

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py tests/sync/test_round_trip.py tests/sync/test_round_trip_with_paradata.py tests/sync/test_round_trip_with_groups.py tests/sync/test_graph_projector_paradata.py -v   # AC-2 + 3 critical
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py tests/sync/test_group_store_pg.py -v   # 8 PG-D L2
PYTHONPATH="$PWD" python -m pytest tests/sync/test_yed_*.py tests/sync/test_table_parser_integration.py tests/sync/test_group_walker_integration.py tests/sync/test_yed_parsers_orchestration.py -v   # 57 yE-A/B/C/D tests
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no
```

## 11. Decomposition (5 Groups, same pattern as yE-A/B/C)

| Group | Scope | Subagent | LOC est |
|---|---|---|---|
| **Group 0** | Pre-flight + rollback tag `pre-yed-import-pipeline` + plan-time investigation (UNITA_TIPO whitelist location, ParadataStore API, mini fixture geometry validation) | Controller (pure git + grep) | — |
| **Group A** | Production: 2 new modules + CLI + vocab patch + hook MAJOR change + 15 L0 + 9 L1 tests. Single commit. | 1 subagent | ~880 prod + ~930 test |
| **Group B** | Docs: bump 5.7.9-alpha → 5.8.0-alpha + bilingual CHANGELOG + dev-log yE-D section above PG-Bv2 | 1 subagent | ~110 |
| **Group C** | Annotated tag `yed-import-pipeline-5.8.0-alpha` + USER APPROVAL GATE + push | 1 subagent (stop at C.4); controller pushes | — |
| **Memory** | Update `project_yed_import_progress.md` with yE-D SHIPPED + `MEMORY.md` index | Controller | — |

### Effort estimate

~3-4 person-days dev work + ~1 review/iteration = ~4-5 calendar days. yE-D is the biggest milestone.

## 12. Acceptance criteria

### Per Group A

- `yed_rapporti_policy.py` exists with `FolderEdgePolicy` (4 active), `analyze_edges`, `apply_policy`
- `yed_import_pipeline.py` exists with `import_yed_raw()` + 5 SQL write functions + ParadataStore integration
- `scripts/import_yed_graphml.py` CLI runs end-to-end on mini fixture
- Vocab patch allows `unita_tipo='VA'` in us_table
- Branch hook dispatches to `import_yed_raw()` and returns its result (no fall-through for yEd-raw)
- 15 L0 + 7 L1 + 2 CLI = 24 new tests pass with exact names from §5/§6/§8/§10
- AC-2 byte-identical preserved
- 3 critical SQLite regression gates preserved
- 5 yE-A + 12 yE-B + 16 yE-C tests preserved
- 8 PG-D L2 tests skip cleanly (or pass online)
- Full suite: 313 passed, 33 skipped (PG offline)
- Strict trailer check returns 0

### Per Group B

- `metadata.txt` shows `version=5.8.0-alpha`
- Bilingual CHANGELOG entry prepended
- Dev-log yE-D section above PG-Bv2
- Strict trailer check returns 0

### Per Group C

- Annotated tag `yed-import-pipeline-5.8.0-alpha` created (local first)
- Tag points to Group B commit
- Trailer check on tag message returns 0
- **STOP at Task C.4**: user manual test plan presented
- Push after `approvato`

## 13. Out of scope / explicitly deferred

### Deferred to yE-E (Dialog UX)

- User-selectable policy via Qt dialog (yE-D defaults to SKIP, no UI choice)
- Per-classification `user_kind` override
- Per-folder `user_dimension` override
- Per-period editable label / numerazione
- Dry-run preview UI (yE-D supports `dry_run=True` programmatically; yE-E adds checkbox)
- Reset to auto-defaults button
- "Apply prefix rule" batch action
- PropertyNode US-target assignment (if plan-time picks Path B)

### Deferred to yE-Closure

- Tutorial multi-language updates
- api-docs CHANGELOG bilingual entry
- README mentions

### Deferred to Phase 4 / 5.8.x

- `failure_mode={"atomic","best_effort"}` flag (yE-D is atomic-only per Q3=α)
- Custom classifier rules via `.classifier.json`
- QSettings persistence of policy choice
- Round-trip yEd-raw → SQL → yEd export verification

### Explicitly NEVER

- yE-D does NOT touch pyarchinit-projected branch (AC-2 sacred)
- yE-D does NOT modify `_run()` body
- yE-D does NOT modify `s3dgraphy` upstream
- yE-D does NOT add DB schema migrations (vocab is in-memory whitelist)
- yE-D does NOT modify existing fixtures

## 14. Plan-time investigation checklist

The plan-writing phase must complete these investigations before writing Group A code:

1. **Locate UNITA_TIPO whitelist**: grep for `UNITA_TIPO` + `unita_tipo` in `modules/`, `ext_libs/s3dgraphy/mappings/`. Determine: Python constant, JSON file, or DB CHECK constraint.
2. **Read ParadataStore API**: open `modules/s3dgraphy/sync/paradata_store.py`. List all `add_*` methods. Map ClassifiedKind → method name. Document missing methods (e.g., if no `add_combiner` exists, COMBINER classification is skipped with log).
3. **PropertyNode decision**: based on ParadataStore API, decide Path A (with US linkage, edge parsing) or Path B (standalone, skip+log).
4. **Mini fixture geometry validation**: re-verify edges in `em_demo_02_mini.graphml` are sufficient for FAN_OUT and REPRESENTATIVE L1 tests (at least one folder-to-leaf edge needed). If insufficient, add edges to the fixture in Group A.

## 15. References

- **Parent spec**: `docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md` §8 (Rapporti policy), §11 (Decomposition)
- **Predecessor specs**: yE-A foundation + yE-B classifier + yE-C parsers (all in `docs/superpowers/specs/2026-05-12-yed-import-*.md`)
- **yE-A + yE-B + yE-C memory**: `~/.claude/projects/.../memory/project_yed_import_progress.md`
- **PG-C `_DryRunRollback` pattern**: `modules/s3dgraphy/sync/graph_ingestor.py` (search for `_DryRunRollback`)
- **DbHandle**: `modules/s3dgraphy/sync/_db_handle.py` (Foundation, 5.6.2-alpha)
- **ParadataStore**: `modules/s3dgraphy/sync/paradata_store.py` (PG-D era)
- **Hook location**: `modules/s3dgraphy/sync/graph_ingestor.py:169-227` (yE-C orchestration; yE-D rewrites to dispatch)
- **Test fixture (reused)**: `tests/sync/fixtures/em_demo_02_mini.graphml`

## 16. Approval log

- Section 1 Architecture + files: approved 2026-05-12
- Section 2 Module internals: approved 2026-05-12
- Section 3 Test strategy: approved 2026-05-12
- Section 4 Decomposition + acceptance + out of scope: approved 2026-05-12
- **Spec final review**: pending user (this step)
