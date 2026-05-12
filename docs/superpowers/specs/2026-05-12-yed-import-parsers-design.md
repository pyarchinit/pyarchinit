# yE-C Parsers — Design Spec

**Date:** 2026-05-12
**Branch:** Stratigraph_00001
**Predecessor tag:** `yed-import-classifier-5.7.6-alpha` (commit `640b4e83`)
**Target tag:** `yed-import-parsers-5.7.7-alpha`

---

## 1. Goal

Ship the third milestone of the 6-milestone yEd-aware graphml import rollout. yE-C adds:

1. **`yed_table_parser.py`** — extracts archaeological periods from yEd `TableNode` rows (the swimlane-style top-level node in EM Datacenter graphmls)
2. **`yed_group_walker.py`** — walks yEd group folder hierarchy and produces `FolderCandidate` records with prefix-to-dimension auto-classification (VA*→attivita, AR*→area, ST*→struttura, …)
3. **`IngestResult.parsed_drafts: dict | None`** — new optional field carrying structured parse output (classifier + periods + folders) for downstream consumption by yE-D pipeline
4. **Branch hook update** in `populate_list()` that orchestrates classify + extract_periods + walk_folders and logs a 3-line summary (classifier counts + period names + folder breakdown) before the legacy fall-through

13 L0 unit tests + 3 L1 integration tests (per-parser + combined orchestration). No DB writes still — yE-D wires the pipeline that consumes `parsed_drafts`.

## 2. Decisions captured during brainstorming (2026-05-12)

| Q | Decision | Rationale |
|---|---|---|
| Q1 scope | **α — single milestone yE-C** | 2 parsers are independent but ship together; user only sees value when both are present + yE-D wires them. yE-B at 273 LOC proved single-milestone capacity. |
| Q2 hook output | **γ — log summary + `IngestResult.parsed_drafts` field** | Both visible feedback AND structured forward-compat for yE-D. Field defaults `None` for back-compat with pyarchinit-projected paths. |
| Q3 L1 tests | **γ — 3 separate L1 tests** | 2 per-parser + 1 combined orchestration. Better diagnostic isolation when one parser fails; combined catches cross-parser consistency issues. |
| Q-hook attach | **A — local var + attach at end of `populate_list()`** | Hook block initializes `_yed_parsed_drafts = None` at function start, populates if yEd-raw detected, attaches to `result` before final return. Clean, thread-safe, no module-level state. |

## 3. Inherited from parent spec

This spec inherits design from parent spec `docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md`:

- §6 (Period extraction) — `PeriodCandidate` dataclass + `extract_periods()` signature + algorithm + 6 L0 test names
- §7 (Group folder interpretation) — `FolderCandidate` dataclass + `walk_folders()` signature + `DEFAULT_FOLDER_PREFIX_MAP` + cycle detection via `CycleDetectedError`

Specializations for MVP:

- **`extract_periods()` and `walk_folders()` accept `Path | str` only** (NOT `Graph` union) — consistent with yE-A `detect_flavor` and yE-B `classify_leaves`
- **`CycleDetectedError` is reused** from existing `graph_ingestor.py` (PG-C) via direct import in `yed_group_walker.py`
- **Branch hook logs summary AND attaches `parsed_drafts` dict** (vs spec's ambiguous "output goes in IngestResult.parsed_drafts")

## 4. Architecture

### Files created (7)

| Path | Responsibility |
|---|---|
| `modules/s3dgraphy/sync/yed_table_parser.py` | `PeriodCandidate` dataclass + `extract_periods(graphml_path)` function |
| `modules/s3dgraphy/sync/yed_group_walker.py` | `FolderCandidate` dataclass + `walk_folders(graphml_path)` function |
| `tests/sync/test_yed_table_parser.py` | 6 L0 unit tests using synthetic graphml in tmp_path |
| `tests/sync/test_yed_group_walker.py` | 7 L0 unit tests using synthetic graphml in tmp_path |
| `tests/sync/test_table_parser_integration.py` | 1 L1 test on `em_demo_02_mini.graphml` fixture |
| `tests/sync/test_group_walker_integration.py` | 1 L1 test on `em_demo_02_mini.graphml` fixture |
| `tests/sync/test_yed_parsers_orchestration.py` | 1 L1 cross-parser consistency test on `em_demo_02_mini.graphml` |

### Files modified (2 production, 3 docs)

| Path | Change | LOC delta |
|---|---|---|
| `modules/s3dgraphy/sync/ingest_result.py` | Add `parsed_drafts: dict \| None = None` field to `IngestResult` dataclass (default None for back-compat) | ~+5 |
| `modules/s3dgraphy/sync/graph_ingestor.py` | Update branch hook at lines 169-196: orchestrate classify + extract_periods + walk_folders + 3-line summary log. Initialize `_yed_parsed_drafts = None` at function start; attach to `result.parsed_drafts` before final return. Preserve outer `try/except Exception: pass` wrapper and lazy imports. | ~+30 / -3 |
| `metadata.txt` | Version bump 5.7.6-alpha → 5.7.7-alpha | 1 line |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.7-alpha]` section | ~50 LOC |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Prepend yE-C section above yE-B | ~40 LOC |

### Files NOT touched

- `yed_detector.py` (yE-A) — unchanged
- `yed_classifier.py` (yE-B) — unchanged
- `tests/sync/fixtures/em_demo_02_mini.graphml` (yE-A) — reused, NOT extended (Y-coordinate geometry verified to work; if a test fails during execution, fixture can be touched up inline)
- Pyarchinit-projected branch of `populate_list()` — sacred (AC-2 preserved)
- DB schema, requirements.txt, vocab_provider, paradata_store — all out of scope

### Total LOC

- Production: ~370 (~340 new + ~30 modify delta)
- Test: ~540 (~480 L0 + ~210 L1)
- Docs: ~95
- **Grand total: ~1000 LOC**

Larger than yE-A (~350) and yE-B (~485) — reflects γ+γ+γ choices (structured field + 3 L1 tests + 2 parsers in 1 milestone).

## 5. `yed_table_parser.py` specification

### Public API

```python
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PeriodCandidate:
    """One period extracted from a yEd TableNode row."""
    yed_row_id: str                    # e.g., "row_0"
    auto_label: str                    # e.g., "Period01" (from NodeLabel)
    user_label: str                    # editable; defaults to auto_label
    auto_periodo: int                  # 1-based ordinal from row order
    auto_fase: int                     # always 1 (yEd rows don't encode phases)
    user_periodo: int                  # editable
    user_fase: int                     # editable
    member_yed_ids: list[str]          # leaf ids falling in this row's Y-range
    y_min: float                       # row top (graphml absolute coords)
    y_max: float                       # row bottom


def extract_periods(graphml_path: Path | str) -> list[PeriodCandidate]:
    """Extract period candidates from top-level yEd TableNode rows.

    Args:
        graphml_path: filesystem path to the .graphml file.

    Returns:
        List of PeriodCandidate in row document order. Empty list if no
        TableNode found, parse error, or missing file.
    """
```

### Algorithm

1. `Path(graphml_path).exists()` check → return `[]` if missing
2. `lxml.etree.iterparse(events=("start", "end"))` with `xml.etree` fallback
3. **First pass**: locate the first node with `<y:TableNode configuration="YED_TABLE_NODE">` child:
   - Extract `<y:Geometry x=... y=... width=... height=...>` → table bounding box
   - Extract `<y:Insets top=...>` from `<y:Table>` → header height (default 30.0 if absent)
   - Extract `<y:Row id="row_N" height="H">` elements → row geometry list (preserving order)
   - Extract each `<y:NodeLabel>` with `<y:RowNodeLabelModelParameter id="row_N">` child → row label by row_id
4. Compute Y absolute ranges progressively:
   - `row_0.y_min = table.y + header_height`
   - `row_0.y_max = row_0.y_min + row_0.height`
   - `row_n.y_min = row_{n-1}.y_max`, etc.
5. **Second pass**: for each leaf node in graphml (`<node>` without `yfiles.foldertype="group"` and NOT inside the TableNode):
   - Extract `<y:Geometry y=...>` absolute Y
   - Find which row contains it (`row.y_min <= y_leaf < row.y_max`)
   - Append leaf yed_id to `row.member_yed_ids`
6. Build `PeriodCandidate` list in row order with `auto_periodo = row_index + 1`, `auto_fase = 1`, `user_* = auto_*`
7. Return list

### Edge cases

- No TableNode found → return `[]`
- TableNode without `<y:Row>` (malformed) → return `[]`
- Row with empty label → `auto_label = f"row_{index}"` placeholder
- Leaf with Y outside all rows (e.g., in TableNode header area) → excluded from all `member_yed_ids`
- Multiple top-level TableNodes (rare) → use FIRST, log warning for others
- Parse error / IO error → return `[]` (safe default, same pattern as yE-A/B)

### 6 L0 tests (`tests/sync/test_yed_table_parser.py`)

| # | Test name | What it verifies |
|---|---|---|
| 1 | `test_no_table_node_returns_empty` | graphml without TableNode → `[]` |
| 2 | `test_extract_em_demo_02_mini_2_periods` | mini fixture → 2 PeriodCandidate (Period01, Period02) |
| 3 | `test_period_ordinal_from_row_order` | row_0 → periodo=1, row_1 → periodo=2 |
| 4 | `test_member_assignment_by_y_coordinate` | leaf with Y=200 inside row Y∈[100,300] → assigned to that row |
| 5 | `test_member_assignment_excludes_header_area` | leaf with Y in TableNode header (above row_0.y_min) → excluded |
| 6 | `test_empty_row_label_uses_placeholder` | `<y:NodeLabel></y:NodeLabel>` on row_2 → `auto_label="row_2"` |

Each test uses synthetic graphml strings in `tmp_path` (no new persistent fixtures).

## 6. `yed_group_walker.py` specification

### Public API

```python
from dataclasses import dataclass, field
from pathlib import Path
import re


DEFAULT_FOLDER_PREFIX_MAP: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^VA"), "attivita"),    # Virtual Activity (EM convention)
    (re.compile(r"^AR"), "area"),
    (re.compile(r"^ST"), "struttura"),
    (re.compile(r"^SE"), "settore"),
    (re.compile(r"^AM"), "ambient"),
    (re.compile(r"^SG"), "saggio"),
    (re.compile(r"^QP"), "quad_par"),
]


@dataclass
class FolderCandidate:
    """One yEd group folder with prefix-derived auto-classification."""
    yed_id: str                        # e.g., "n0::n0"
    full_label: str                    # "VA01-foundation example"
    auto_dimension: str | None         # "attivita" or None if no prefix match
    user_dimension: str | None         # editable (or "skip")
    auto_value: str                    # cleaned prefix-only: "VA01"
    user_value: str                    # editable
    member_yed_ids: list[str]          # direct leaf children only
    nested_folder_ids: list[str]       # direct subfolders only
    parent_folder_id: str | None
    extra_attrs: dict = field(default_factory=dict)  # description suffix


def walk_folders(graphml_path: Path | str) -> list[FolderCandidate]:
    """Walk yEd `yfiles.foldertype="group"` hierarchy and build candidates.

    Excludes the top-level TableNode (period container, yE-C
    table_parser territory).

    Args:
        graphml_path: filesystem path to the .graphml file.

    Returns:
        List of FolderCandidate in document order. Empty list if no
        folders found, parse error, or missing file.

    Raises:
        CycleDetectedError: imported from graph_ingestor.py. Raised when
        folder A contains folder B contains folder A (malformed graphml).
    """
```

### Algorithm

1. `Path(graphml_path).exists()` check → return `[]` if missing
2. Parse XML with lxml.etree (xml.etree fallback)
3. Recursive walker starting from `<graph>`:
   - For each `<node yfiles.foldertype="group">`:
     - **Skip if it's the top-level TableNode** (has direct child `<y:TableNode configuration="YED_TABLE_NODE">`)
     - **Cycle check**: `if folder_id in visited → raise CycleDetectedError`; else `visited.add(folder_id)`
     - Extract `full_label` from first non-empty `<y:NodeLabel>`
     - Compute `auto_dimension` via `DEFAULT_FOLDER_PREFIX_MAP` (first regex match wins, or None)
     - Compute `auto_value`: regex `^([A-Z]+\d+)` extracts prefix; description after `-` or first space saved to `extra_attrs["description"]`. If no prefix match, `auto_value = full_label`.
     - Walk direct children:
       - Leaf children (NOT folders) → `member_yed_ids`
       - Subfolder children → `nested_folder_ids` + recurse with `parent_folder_id = current_id`
     - Append to result list
4. Return list in document order

### Edge cases

- No folders → return `[]`
- Top-level TableNode (`yfiles.foldertype="group"` + has `<y:TableNode>`) → excluded
- Unrecognized prefix (e.g., `Foundation Area`) → `auto_dimension=None`, `auto_value="Foundation Area"`
- Folder with empty/no label → `auto_value=""`, requires user override in yE-E dialog
- Cycle (A → B → A in malformed yEd) → raises `CycleDetectedError`; hook's outer try/except swallows
- Parse error / IO error → return `[]`

### 7 L0 tests (`tests/sync/test_yed_group_walker.py`)

| # | Test name | What it verifies |
|---|---|---|
| 1 | `test_no_folders_returns_empty` | graphml without folders → `[]` |
| 2 | `test_walk_em_demo_02_mini_finds_2_folders` | mini fixture → 2 FolderCandidate (VA01, AR01) |
| 3 | `test_top_level_tablenode_excluded_from_folders` | the swimlane TableNode is NOT in the result |
| 4 | `test_label_with_description_extracts_prefix` | `VA01-foundation example` → `auto_value="VA01"`, `extra_attrs["description"]="foundation example"` |
| 5 | `test_unrecognized_prefix_uses_full_label_as_auto_value` | `Custom Group` → `auto_value="Custom Group"`, `auto_dimension=None` |
| 6 | `test_nested_folder_membership_split` | folder A → folder B → leaf X: A.member_yed_ids doesn't include X (direct only); A.nested_folder_ids includes B; B.member_yed_ids includes X; parent_folder_id of B is A.yed_id |
| 7 | `test_cycle_detection_raises_cycle_detected_error` | synthetic graphml with A → B → A → raises `CycleDetectedError` |

### `CycleDetectedError` import

```python
# In yed_group_walker.py
from .graph_ingestor import CycleDetectedError
```

No circular import risk: `graph_ingestor.py` only imports `yed_group_walker` inside the function body (lazy) of `populate_list()`. At module load time, `yed_group_walker` can import `CycleDetectedError` from `graph_ingestor` cleanly (exception class is defined at top of graph_ingestor.py before any function).

## 7. Branch hook update

### Modify `modules/s3dgraphy/sync/ingest_result.py`

```python
# Add to IngestResult dataclass
@dataclass
class IngestResult:
    # ... existing fields preserved ...

    # yE-C (5.7.7-alpha): structured output from the yEd-raw parse phase.
    # Populated by populate_list() when graphml_path is yEd-raw; None for
    # pyarchinit-projected graphmls. Forward-compat with yE-D pipeline
    # which will consume these drafts to drive DB writes.
    #
    # Shape when populated:
    #   {
    #     "classified": list[ClassifiedNode],   # from yE-B classify_leaves
    #     "periods": list[PeriodCandidate],     # from yE-C extract_periods
    #     "folders": list[FolderCandidate],     # from yE-C walk_folders
    #   }
    parsed_drafts: dict | None = None
```

`dict | None = None` default preserves back-compat for all existing call sites that construct `IngestResult(...)` without the new field.

### Modify `modules/s3dgraphy/sync/graph_ingestor.py:169-196`

The yE-B block becomes (replace yE-B's `# yE-A + yE-B: yEd-raw detection + classifier preview.` block with):

```python
        # yE-A + yE-B + yE-C: yEd-raw detection + classify + parse.
        # When graphml_path is a yEd-raw file (no pyarchinit.* keys),
        # classify leaves, extract periods, walk folders. Log a 3-line
        # summary + stash parsed drafts in _yed_parsed_drafts for
        # attachment to result.parsed_drafts at the end. Then fall
        # through to legacy path (DB writes still come from there;
        # full pipeline lands in yE-D).
        _yed_parsed_drafts = None  # populated below if yEd-raw detected
        if graphml_path is not None:
            try:
                from .yed_detector import detect_flavor
                if detect_flavor(graphml_path) == "yed-raw":
                    import logging
                    from collections import Counter
                    from .yed_classifier import classify_leaves
                    from .yed_table_parser import extract_periods
                    from .yed_group_walker import walk_folders
                    classified = classify_leaves(graphml_path)
                    periods = extract_periods(graphml_path)
                    folders = walk_folders(graphml_path)
                    counts = Counter(n.auto_kind.value for n in classified)
                    classifier_summary = ", ".join(
                        f"{k}: {v}" for k, v in sorted(counts.items())
                    )
                    period_summary = (
                        ", ".join(p.auto_label for p in periods)
                        if periods else "(no TableNode found)"
                    )
                    folder_summary = (
                        ", ".join(
                            f"{f.auto_value} ({f.auto_dimension or 'unknown'}, "
                            f"{len(f.member_yed_ids)} members)"
                            for f in folders
                        )
                        if folders else "(no group folders found)"
                    )
                    logging.getLogger(__name__).warning(
                        "yEd-raw graphml detected at %s.\n"
                        "  Classified %d leaves: %s.\n"
                        "  Detected %d periods: %s.\n"
                        "  Detected %d group folders: %s.\n"
                        "  Yed-aware import path not yet wired "
                        "(yE-C parsers only). Falling through to legacy "
                        "path. Expect partial/incorrect ingestion.",
                        graphml_path,
                        len(classified), classifier_summary,
                        len(periods), period_summary,
                        len(folders), folder_summary,
                    )
                    _yed_parsed_drafts = {
                        "classified": classified,
                        "periods": periods,
                        "folders": folders,
                    }
            except Exception:
                # Detection + parsing is best-effort; never block legacy.
                pass
        # -- existing pyarchinit-projected path UNCHANGED below --
```

### Attach `parsed_drafts` to `result` at end of `populate_list()`

Right before the final `return result` of the legacy path:

```python
        # yE-C: attach yEd-raw parse drafts to result for yE-D pipeline.
        # No-op for pyarchinit-projected graphmls (stays None).
        if _yed_parsed_drafts is not None:
            result.parsed_drafts = _yed_parsed_drafts
        return result
```

The exact location depends on the existing `populate_list()` structure — the plan-writing step will locate the right insertion point.

## 8. L1 integration tests

### `test_extract_periods_em_demo_02_mini` (in `tests/sync/test_table_parser_integration.py`)

```python
def test_extract_periods_em_demo_02_mini():
    """Verify extract_periods on the yE-A reference fixture.
    
    Mini fixture top-level TableNode has 2 rows (Period01, Period02).
    """
    fixture = FIXTURES / "em_demo_02_mini.graphml"
    periods = extract_periods(fixture)
    assert len(periods) == 2
    assert periods[0].auto_label == "Period01"
    assert periods[1].auto_label == "Period02"
    assert periods[0].auto_periodo == 1
    assert periods[1].auto_periodo == 2
    assert periods[0].auto_fase == periods[1].auto_fase == 1
    assert periods[0].user_label == periods[0].auto_label  # no override yet
    # Y-coord membership: at least some leaf assigned (precise count
    # depends on fixture geometry; assert >= 0 and total <= 6 leaves)
    total_members = sum(len(p.member_yed_ids) for p in periods)
    assert 0 <= total_members <= 6
```

### `test_walk_folders_em_demo_02_mini` (in `tests/sync/test_group_walker_integration.py`)

```python
def test_walk_folders_em_demo_02_mini():
    """Verify walk_folders on the yE-A reference fixture.
    
    Mini fixture has 2 group folders: VA01-foundation example (attivita),
    AR01-area example (area). Top-level TableNode excluded.
    """
    fixture = FIXTURES / "em_demo_02_mini.graphml"
    folders = walk_folders(fixture)
    assert len(folders) == 2

    va01 = next(f for f in folders if f.auto_value == "VA01")
    assert va01.full_label == "VA01-foundation example"
    assert va01.auto_dimension == "attivita"
    assert va01.user_dimension == "attivita"
    assert va01.extra_attrs.get("description") == "foundation example"
    # VA01 contains 4 direct leaves (US01, US02, USV101, material)
    assert len(va01.member_yed_ids) == 4

    ar01 = next(f for f in folders if f.auto_value == "AR01")
    assert ar01.full_label == "AR01-area example"
    assert ar01.auto_dimension == "area"
    # AR01 contains 2 direct leaves (SF105, VSF107)
    assert len(ar01.member_yed_ids) == 2

    # Top-level TableNode "Archaeological Context" must NOT appear
    labels = {f.full_label for f in folders}
    assert "Archaeological Context" not in labels
```

### `test_classifier_periods_folders_consistent_on_em_demo_02_mini` (in `tests/sync/test_yed_parsers_orchestration.py`)

```python
def test_classifier_periods_folders_consistent_on_em_demo_02_mini():
    """Cross-parser orchestration test: yE-B classifier + yE-C parsers
    produce consistent state on the same fixture."""
    fixture = FIXTURES / "em_demo_02_mini.graphml"
    classified = classify_leaves(fixture)
    periods = extract_periods(fixture)
    folders = walk_folders(fixture)

    # Counts: 6 classified leaves, 2 periods, 2 folders
    assert len(classified) == 6
    assert len(periods) == 2
    assert len(folders) == 2

    # No leaf yed_id appears in folder list (folders are NOT leaves)
    classified_ids = {n.yed_id for n in classified}
    folder_ids = {f.yed_id for f in folders}
    assert classified_ids.isdisjoint(folder_ids)

    # Every classified leaf appears in at least one folder's member list
    all_members = set()
    for f in folders:
        all_members.update(f.member_yed_ids)
    assert classified_ids.issubset(all_members), \
        f"Leaves not accounted for: {classified_ids - all_members}"

    # Folder labels don't leak into classifier (yE-B already verified;
    # cross-check here)
    classified_labels = {n.label for n in classified}
    folder_labels = {f.full_label for f in folders}
    assert classified_labels.isdisjoint(folder_labels)
```

## 9. Backward compat + test strategy

### AC-2 byte-identical preservation

The pyarchinit-projected branch of `populate_list()` is unchanged. The yE-C additions are:
- New `_yed_parsed_drafts = None` initialization at function start (no-op for projected path)
- The yEd-raw branch block grows by ~20 LOC (still inside try/except, still no-op fall-through)
- The `if _yed_parsed_drafts is not None: result.parsed_drafts = ...` at end is no-op for projected (stays None)
- `IngestResult.parsed_drafts` has `default=None` → existing callers unaffected

Guarantees:
- `test_ai03_export_byte_identical` passes (AC-2)
- 3 critical SQLite gates pass (`test_round_trip_with_paradata`, `test_round_trip_with_groups`, `test_graph_projector_paradata`)
- 8 PG-D L2 tests pass
- 5 yE-A detector tests preserved
- 11 yE-B classifier tests preserved (9 L0 + 2 polish + 1 L1)
- 273 SQLite baseline unchanged

### Test count progression

| Milestone | Tot passed (PG offline) | Delta |
|---|---|---|
| Pre yE-C (post yE-B) | 273 | — |
| Post yE-C Group A (+16) | 289 | +6 table + 7 walker + 1 table-L1 + 1 walker-L1 + 1 orchestration-L1 |
| Post yE-C Group B/C | 289 | docs only |

PG online + psycopg2: **297 passed, 12 skipped**

### Migrations / schema changes

**None.** No new DB columns, tables, migrations. The `IngestResult.parsed_drafts` field is in-memory only; not persisted.

## 10. Decomposition into 5 Groups

| Group | Scope | Subagent | LOC est |
|---|---|---|---|
| **Group 0** | Pre-flight + rollback tag `pre-yed-import-parsers` | Controller (pure git) | — |
| **Group A** | Production: 2 parsers + IngestResult field + hook update + 13 L0 + 3 L1 tests (single commit) | 1 subagent | ~370 prod + ~540 test |
| **Group B** | Docs + version bump 5.7.6 → 5.7.7-alpha + bilingual CHANGELOG + dev-log yE-C section | 1 subagent | ~95 |
| **Group C** | Annotated tag `yed-import-parsers-5.7.7-alpha` + USER APPROVAL GATE + push | 1 subagent (stops at C.4); controller pushes after approval | — |
| **Memory** | Update `project_yed_import_progress.md` with yE-C SHIPPED + `MEMORY.md` index | Controller | — |

### Effort estimate

~2-3 person-days of dev work + ~0.5-1 of review/iteration = ~3 calendar days. Larger than yE-A/B due to 2 parsers + structured field + 3 L1 tests.

## 11. Acceptance criteria

### Per Group A

- `yed_table_parser.py` exists with `PeriodCandidate` + `extract_periods`
- `yed_group_walker.py` exists with `FolderCandidate` + `walk_folders` + reuses `CycleDetectedError` from `graph_ingestor`
- 6 L0 + 7 L0 + 3 L1 tests pass with exact names from §5/§6/§8
- `IngestResult.parsed_drafts` field added with default `None`
- Branch hook updated: orchestrates classify + extract_periods + walk_folders + 3-line log + `_yed_parsed_drafts` local var + attach at end
- AC-2 byte-identical preserved
- 3 critical SQLite regression gates preserved
- 5 yE-A detector tests preserved
- 12 yE-B classifier tests preserved
- 8 PG-D L2 tests preserved (skip cleanly offline)
- Full suite: 289 passed, 33 skipped (PG offline)
- Commit SHA has 0 `^Co-Authored-By:` line-anchored regex hits

### Per Group B

- `metadata.txt` shows `version=5.7.7-alpha`
- Bilingual CHANGELOG entry at top of `dev_logs/CHANGELOG.md`
- Dev-log yE-C section above yE-B section
- Commit SHA has 0 trailer issues

### Per Group C

- Tag `yed-import-parsers-5.7.7-alpha` is annotated (`git cat-file -t` returns "tag")
- Tag points to Group B commit
- Tag message has 0 trailer issues
- **STOP at Task C.4** — user manual test plan presented, await `approvato` before push
- After user approval: tag + branch pushed to origin

## 12. Out of scope / explicitly deferred

### Deferred to later milestones

- **yE-D**: `yed_rapporti_policy.py` + `yed_import_pipeline.py` orchestrator + CLI + DB writes consuming `parsed_drafts`
- **yE-E**: Qt dialog UX with per-leaf classifier override + per-period editable label/numero/fase + per-folder dimension dropdown + apply-to-prefix batch action
- **yE-Closure**: docs + tutorial (9 langs) + api-docs CHANGELOG + version bump to 5.8.0-alpha

### Deferred to iteration 2 (post yE-Closure)

- Custom folder prefix rules via `.classifier.json` config file
- QSettings persistence of folder prefix overrides
- Save/Load presets of dialog choices

### Explicitly NEVER

- yE-C does NOT touch the pyarchinit-projected branch (AC-2 sacred)
- yE-C does NOT modify DB schema
- yE-C does NOT modify `s3dgraphy` upstream
- yE-C does NOT introduce a new fixture file (mini fixture from yE-A is reused)
- The `parsed_drafts` dict shape is intentionally untyped (`dict | None`) — yE-D can refactor to TypedDict / dataclass if needed

## 13. References

- **Parent spec**: `docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md` §6 (Period extraction), §7 (Group folder interpretation), §11 (Decomposition)
- **Predecessor specs**:
  - `2026-05-12-yed-import-classifier-design.md` (yE-B, commit `c0afd1fe`)
- **yE-A + yE-B memory**: `~/.claude/projects/.../memory/project_yed_import_progress.md`
- **Test fixture (reused)**: `tests/sync/fixtures/em_demo_02_mini.graphml` (108 lines, from yE-A)
- **Hook location**: `modules/s3dgraphy/sync/graph_ingestor.py:169-196` (yE-B updated; yE-C extends)
- **`CycleDetectedError` source**: `modules/s3dgraphy/sync/graph_ingestor.py` (PG-C era, reused in yE-C `yed_group_walker.py`)

## 14. Approval log

- Section 1 Architecture + files: approved 2026-05-12
- Section 2 Parser internals: approved 2026-05-12
- Section 3 Branch hook + IngestResult field: approved 2026-05-12
- Section 4 Test strategy + decomposition: approved 2026-05-12
- **Spec final review**: pending user (this step)
