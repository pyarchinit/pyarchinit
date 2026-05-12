# yEd-aware GraphML Import — Design Spec

**Date:** 2026-05-12
**Branch:** Stratigraph_00001
**Predecessor tag:** `phase3-pgcompat-consolidation-5.7.4-alpha` (commit `7064b1d1`)
**Target tags:** `yed-import-foundation-5.7.5-alpha` → `yed-import-closure-5.8.0-alpha` (6 milestones)

---

## 1. Trigger and goal

### Bug report

User reported that importing `/Users/enzo/Downloads/EM_demo_02.graphml` creates only 17 rows in `us_table` when many more were expected, and that the label `VA01-foundation of the colonnade` ends up as a US name inside the `rapporti` column. Investigation revealed this is not a small bug but a **substantive feature gap**: the current `GraphIngestor.populate_list()` was designed to ingest graphs **projected by pyarchinit's own GraphProjector**, where every node has typed s3dgraphy classes (`StratigraphicUnit`, `DocumentNode`, etc.) + the `pyarchinit.node_uuid` data key. yEd-raw graphmls authored externally have none of these markers, so the existing filter `_NON_STRAT_TYPES` is bypassed (all generic `Node` instances pass) and the existing folder-aware code (`_apply_group_folders_to_sql`) silently skips because the `pyarchinit.<kind>` data keys are absent.

### Goal

Add a **yEd-aware import path** that:

1. Detects yEd-raw graphmls automatically
2. Classifies leaf nodes by label-prefix heuristic (`US*`, `USV*`, `SF*`, `VSF*`, `D.*`, `C.*`, `VA*`, etc.)
3. Extracts periods from yEd `TableNode` rows → `periodizzazione_table`
4. Walks yEd group folder hierarchy → `us_table.<dim>` membership updates
5. Handles edges that touch group folders via a user-selectable policy (default SKIP)
6. Presents a Qt dialog where the user reviews/overrides the auto-classification before commit
7. Preserves AC-2 byte-identical regression gates for pyarchinit-projected graphmls

### Non-goals

See §10.

---

## 2. Decisions captured during brainstorming (2026-05-12)

| Dim | Question | Decision | Rationale |
|---|---|---|---|
| 1 | Classifier strategy | **B — auto + dialog override** | Safety > attrition for unfamiliar yEd-raw input |
| 2 | Period detection | **B — period section in same dialog** | UX coherence; datazione fields stay NULL (user fills later) |
| 3 | Group folder interpretation | **D — heuristic + dropdown + value-editable + apply-to-prefix** | Maximum flexibility, batch-friendly via prefix rule |
| 4 | Rapporti policy on folder-touching edges | **A+E — SKIP default + dropdown for other policies** | Safe by default; expert opt-in for FAN_OUT / REPRESENTATIVE / SYNTHETIC |
| 5 | Backward compat with pyarchinit-projected | **A — detect-and-branch transparent in `populate_list()`** | One public API, AC-2 byte-identical preserved |
| 6 | UI integration | **A — reuse existing Import GraphML menu** | One entry point, behaviour branches on graphml type |

---

## 3. Architecture overview

The feature adds a parallel codepath in `GraphIngestor.populate_list()`, activated when `yed_detector.detect_flavor()` returns `"yed-raw"`. The pyarchinit-projected branch remains **byte-identically unchanged** to preserve AC-2.

### New modules (in `modules/s3dgraphy/sync/`)

| File | Responsibility | LOC est |
|---|---|---|
| `yed_detector.py` | O(1) header scan: pyarchinit-projected vs yed-raw | ~50 |
| `yed_classifier.py` | Label-prefix → `ClassificationKind` enum | ~150 |
| `yed_table_parser.py` | `y:TableNode` rows → `PeriodCandidate` list | ~120 |
| `yed_group_walker.py` | yEd folder hierarchy → `FolderCandidate` list | ~180 |
| `yed_rapporti_policy.py` | Folder-edge classification + policy application | ~100 |
| `yed_import_pipeline.py` | Orchestrator: detect → classify → parse → dialog → write | ~200 |
| `gui/yed_import_dialog.py` | Qt dialog with 4 sections (classifier/periods/groups/rapporti) | ~400 |

### Modified existing files

| File | Modification |
|---|---|
| `modules/s3dgraphy/sync/graph_ingestor.py` | Top of `populate_list()`: detect → branch to `yed_import_pipeline.import_yed_raw()` if yEd-raw; existing path unchanged otherwise |

### Data flow (yEd-raw branch)

```
.graphml → yed_detector.detect_flavor() → "yed-raw"
  → yed_classifier.classify_leaves(graphml_path) → list[ClassifiedNode]
  → yed_table_parser.extract_periods(graphml_path) → list[PeriodCandidate]
  → yed_group_walker.walk_folders(graphml_path) → list[FolderCandidate]
  → yed_rapporti_policy.analyze_edges(graphml_path, folder_ids) → FolderEdgeReport
  → YedImportDialog.exec(drafts) → user confirms → FinalizedImport
  → existing INSERT/UPDATE machinery (us_table, periodizzazione_table,
    inventario_materiali_table, paradata.graphml) with FinalizedImport as input
```

---

## 4. Detection (yEd-raw vs pyarchinit-projected)

### File: `yed_detector.py` (~50 LOC)

```python
from pathlib import Path
from typing import Literal

GraphMLFlavor = Literal["pyarchinit-projected", "yed-raw"]

def detect_flavor(graphml_path: Path | str) -> GraphMLFlavor:
    """Inspect graphml header for the `pyarchinit.node_uuid` data key.

    pyarchinit-projected: AI03+ writes `<key attr.name="pyarchinit.node_uuid" for="node">`
    yed-raw:              No `pyarchinit.*` keys

    O(1) header scan: stops at the first `<graph>` element.
    Returns 'yed-raw' as conservative default if the file is malformed.
    """
```

### Algorithm

1. Stream-parse `.graphml` with `lxml.etree.iterparse` (or `xml.etree.iterparse` if lxml unavailable)
2. Iterate top-level `<key>` elements
3. If find `<key attr.name="pyarchinit.node_uuid" for="node">` → return `"pyarchinit-projected"`
4. As soon as `<graph>` element opens → stop, return `"yed-raw"`
5. On parse error → return `"yed-raw"` (safe default — dialog surfaces the problem)

### Integration in `graph_ingestor.py`

```python
def populate_list(self, graph, db_path=None, sito=None, *,
                  graphml_path=None, dry_run=False, ...):
    handle = _resolve_db_handle(db_path)
    # ... existing schema check ...

    # ── NEW: yEd-raw detection branch ──
    if graphml_path is not None and detect_flavor(graphml_path) == "yed-raw":
        from .yed_import_pipeline import import_yed_raw
        return import_yed_raw(graph=graph, graphml_path=graphml_path,
                              handle=handle, sito=sito, dry_run=dry_run)

    # ── existing pyarchinit-projected path UNCHANGED below ──
```

### Edge cases

- `graphml_path is None` → fall through to existing path (in-memory graph, caller responsibility)
- Mixed graphml (pyarchinit-projected with manual yEd folder edits without `pyarchinit.*` keys) → classified as `pyarchinit-projected` → folders fall back to today's behavior (`_apply_group_folders_to_sql` skip). Documented limitation.
- Empty / malformed graphml → `yed-raw` default → dialog shows "0 nodes detected, nothing to import"

---

## 5. Classifier (`yed_classifier.py`)

### ClassificationKind enum

```python
class ClassificationKind(StrEnum):
    US_REAL          = "us_real"           # → us_table, unita_tipo=US
    US_MASONRY       = "us_masonry"        # → us_table, unita_tipo=USM
    US_DOCUMENTARY   = "us_documentary"    # → us_table, unita_tipo=USD
    USV_VIRTUAL      = "usv_virtual"       # → paradata.graphml (USVs)
    USV_FORMAL       = "usv_formal"        # → paradata.graphml (USVs/USVn explicit)
    SPECIAL_FIND     = "special_find"      # → inventario_materiali_table
    VIRTUAL_FIND     = "virtual_find"      # → paradata.graphml (VirtualSpecialFindUnit)
    DOCUMENT         = "document"          # → paradata.graphml (DocumentNode)
    COMBINER         = "combiner"          # → paradata.graphml (CombinerNode)
    PROPERTY         = "property"          # → paradata.graphml (PropertyNode)
    UNKNOWN          = "unknown"           # → dialog flags for user mapping
    SKIP             = "skip"              # → user-chosen: ignore this node
```

### Default rules (order matters — first match wins)

```python
DEFAULT_CLASSIFIER_RULES: list[tuple[re.Pattern, ClassificationKind]] = [
    (re.compile(r"^USVs\b|^USVn\b"), ClassificationKind.USV_FORMAL),
    (re.compile(r"^USV\d+"),         ClassificationKind.USV_VIRTUAL),
    (re.compile(r"^USM\d+|^USR\d+|^USS\d+"), ClassificationKind.US_MASONRY),
    (re.compile(r"^USD\d+"),         ClassificationKind.US_DOCUMENTARY),
    (re.compile(r"^US\d+"),          ClassificationKind.US_REAL),
    (re.compile(r"^VSF\d+"),         ClassificationKind.VIRTUAL_FIND),
    (re.compile(r"^SF\d+"),          ClassificationKind.SPECIAL_FIND),
    (re.compile(r"^D\.\d+"),         ClassificationKind.DOCUMENT),
    (re.compile(r"^C\.\d+"),         ClassificationKind.COMBINER),
    (re.compile(r"^(material|position|width|length|height|heigth|type|color|weight|proportion|size)$", re.I),
                                     ClassificationKind.PROPERTY),
]
```

### Public API

```python
@dataclass
class ClassifiedNode:
    yed_id: str                    # e.g., "n0::n0::n10"
    label: str                     # e.g., "US02"
    auto_kind: ClassificationKind  # heuristic decision
    user_kind: ClassificationKind  # user override (defaults to auto_kind)
    extra_attrs: dict              # parsed numeric us_id, prefix, suffix


def classify_leaves(
    graph_or_graphml_path: Graph | Path | str,
    rules: list[tuple[re.Pattern, ClassificationKind]] | None = None,
) -> list[ClassifiedNode]:
    """Run prefix rules on every leaf (non-folder) node. Returns
    nodes in yEd document order (so the dialog preserves authoring order).
    `rules` defaults to DEFAULT_CLASSIFIER_RULES; callers can override
    for site-specific naming conventions (extension point — deferred to iter 2).
    """
```

### Test L0 (`tests/sync/test_yed_classifier.py`)

- `test_classify_us_prefix`
- `test_classify_usv_prefix`
- `test_classify_usm_prefix_wins_over_us` (order)
- `test_classify_special_find`
- `test_classify_document_with_subdots` (`D.01.03`)
- `test_classify_property_case_insensitive`
- `test_classify_unknown_falls_through` (`Foundation_01`)
- `test_classify_uses_yed_document_order`
- `test_classify_em_demo_02_smoke` (on real fixture)

---

## 6. Period extraction (`yed_table_parser.py`)

### yEd TableNode structure

The top-level node in `EM_demo_02.graphml` (`n0` = "Archaeological Context") has:
- `<y:TableNode configuration="YED_TABLE_NODE">`
- Multiple `<y:NodeLabel>` with `<y:RowNodeLabelModelParameter id="row_N"/>` — one per period row
- `<y:Table><y:Rows><y:Row id="row_N" height="..."/>...</y:Rows></y:Table>` — row geometry
- `<y:Geometry x=... y=... width=... height=...>` — table bounding box

Leaf US nodes are positioned with absolute Y coordinates; the row a leaf belongs to is determined by Y-coordinate intersection.

### Public API

```python
@dataclass
class PeriodCandidate:
    yed_row_id: str            # "row_0"
    auto_label: str            # "Period01"
    user_label: str            # editable
    auto_periodo: int          # 1-based ordinal from row order
    auto_fase: int             # default 1 (yEd rows don't encode phases)
    user_periodo: int
    user_fase: int
    member_yed_ids: list[str]  # leaf ids falling in this row's Y-range
    y_min: float
    y_max: float


def extract_periods(graphml_path: Path | str) -> list[PeriodCandidate]:
    """Find top-level y:TableNode + parse rows. Compute leaf membership
    by Y-coordinate. Returns [] if no TableNode found.
    """
```

### Algorithm

1. Parse graphml with `lxml.etree.iterparse`
2. Find first `<node>` containing `<y:TableNode configuration="YED_TABLE_NODE">`
3. Extract `<y:RowNodeLabelModelParameter id="row_N">` + associated `<y:NodeLabel>` text
4. Extract `<y:Row id="row_N" height=...>` for heights
5. Compute absolute Y ranges progressively
6. For each leaf, read `<y:Geometry y=...>` and find its row
7. Auto-assign `periodo = row_index + 1`, `fase = 1`

### Edge cases

- No TableNode → `[]` (dialog shows empty section)
- Leaf with Y outside all rows → excluded from all `member_yed_ids`
- Multiple top-level TableNodes → take first, warn for others
- Row with empty label → `auto_label = f"row_{index}"` placeholder

### Test L0 (`tests/sync/test_yed_table_parser.py`)

- `test_no_table_node_returns_empty`
- `test_extract_em_demo_02_periods` (assert 2 candidates)
- `test_period_ordinal_from_row_order`
- `test_member_assignment_by_y_coordinate`
- `test_member_assignment_excludes_header`
- `test_empty_row_label_gets_placeholder`

### Critical UX note

`datazione_iniziale` / `datazione_finale` cannot be auto-derived from yEd. They stay NULL after import; the user fills them via pyarchinit "Periodizzazione" tab. The dialog must show this warning explicitly in the period section.

---

## 7. Group folder interpretation (`yed_group_walker.py`)

### Default prefix → dimension map

```python
DEFAULT_FOLDER_PREFIX_MAP: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^VA"), "attivita"),   # Virtual Activity (EM convention)
    (re.compile(r"^AR"), "area"),
    (re.compile(r"^ST"), "struttura"),
    (re.compile(r"^SE"), "settore"),
    (re.compile(r"^AM"), "ambient"),
    (re.compile(r"^SG"), "saggio"),
    (re.compile(r"^QP"), "quad_par"),
]
# Folders matching no prefix → user picks dimension in dialog (or "skip")
```

### Public API

```python
@dataclass
class FolderCandidate:
    yed_id: str
    full_label: str                # "VA01-foundation of the colonnade"
    auto_dimension: str | None     # "attivita" or None
    user_dimension: str | None     # editable (or "skip")
    auto_value: str                # cleaned prefix-only: "VA01"
    user_value: str                # editable
    member_yed_ids: list[str]      # direct leaf children only
    nested_folder_ids: list[str]   # direct subfolders only
    parent_folder_id: str | None
    extra_attrs: dict              # description suffix preserved here


def walk_folders(graphml_path: Path | str) -> list[FolderCandidate]:
    """Descend yfiles.foldertype="group" hierarchy. Cycle detection via
    visited set (raises CycleDetectedError on malformed graphml).
    """
```

### Auto-value extraction logic

For folder label `"VA01-foundation of the colonnade"`:
1. Prefix regex `^([A-Z]+\d+)` → `auto_value = "VA01"`
2. Description after `-` or first space → preserved in `extra_attrs["description"]` (for future paradata use)
3. No match (e.g., `"Foundation Area"`) → `auto_value = "Foundation Area"`

### Membership application (post-dialog)

After user confirms `user_dimension` and `user_value`:

```sql
UPDATE us_table 
SET <user_dimension> = '<user_value>'
WHERE node_uuid IN (<member_uuids>)
```

For nested folders: bottom-up application. Inner folder updates direct leaf children; outer folder updates its direct leaf children only (not those already handled by inner). If dimensions differ, both columns get populated.

### Edge cases

- No folders → `[]`
- Top-level TableNode with `yfiles.foldertype="group"` → excluded (it's a period container, handled by §6)
- Leaf in multiple folder ancestors → inherits ALL their dimensions (multiple `us_table.<col>` populated)
- User selects "skip" → no us_table column update for that folder
- Cycle (A → B → A) → `CycleDetectedError`

### Test L0 (`tests/sync/test_yed_group_walker.py`)

- `test_no_folders_returns_empty`
- `test_walk_em_demo_02_finds_6_va_folders` (assert auto_dimension=attivita, auto_value=VA01..VA06)
- `test_top_level_tablenode_excluded`
- `test_label_with_description_extracts_prefix`
- `test_unrecognized_prefix_uses_full_label`
- `test_nested_folder_membership_split`
- `test_cycle_detection_raises`

---

## 8. Rapporti policy (`yed_rapporti_policy.py`)

### Policy enum

```python
class FolderEdgePolicy(StrEnum):
    SKIP           = "skip"            # DEFAULT — folder-edges scartati
    FAN_OUT        = "fan_out"         # expand to all N×M leaf pairs
    REPRESENTATIVE = "representative"  # first member as proxy
    SYNTHETIC      = "synthetic"       # create VirtualActivity us_table rows (advanced)
```

### Public API

```python
@dataclass
class FolderEdgeReport:
    total_edges: int
    leaf_to_leaf: int
    folder_touching: list[FolderEdge]


@dataclass
class FolderEdge:
    source_id: str
    target_id: str
    source_is_folder: bool
    target_is_folder: bool
    edge_type: str | None  # rapporto label e.g., "covers"


def analyze_edges(
    graphml_path: Path | str,
    folder_ids: set[str],
) -> FolderEdgeReport: ...


def apply_policy(
    report: FolderEdgeReport,
    policy: FolderEdgePolicy,
    folder_members: dict[str, list[str]],
) -> ExpandedRapporti: ...
```

### Policy semantics

| Policy | Behavior | When to use |
|---|---|---|
| `SKIP` | Folder-touching edges dropped, count logged | Default — preserves Harris matrix integrity |
| `FAN_OUT` | `(folder_A, leaf_X)` with N members → N edges | Want maximum information preserved |
| `REPRESENTATIVE` | First member of folder used as proxy | Compact, semantically arbitrary |
| `SYNTHETIC` | Create new us_table row with `us=<auto_value>`, `unita_tipo='VA'` | Requires vocab update — opt-in |

### `SYNTHETIC` requires vocab support

`vocab_provider.UNITA_TIPO_WHITELIST` does not currently include `VA`. If user selects SYNTHETIC and vocab lacks `VA`, pipeline raises `UnknownUnitaTipoError` with helpful hint: "vocab does not support 'VA' — choose SKIP or run vocab migration (deferred — see §11)".

### Test L0 (`tests/sync/test_yed_rapporti_policy.py`)

- `test_analyze_edges_em_demo_02_counts`
- `test_apply_skip_policy_returns_empty_expanded`
- `test_apply_fan_out_n_x_m`
- `test_apply_representative_uses_first_leaf`
- `test_apply_synthetic_creates_virtual_us_rows`
- `test_synthetic_without_vocab_raises_helpful_error`
- `test_self_loop_folder_skipped_in_all_policies`

---

## 9. Dialog UX (`gui/yed_import_dialog.py`)

### Layout (4 sections)

```
┌─ Import yEd GraphML — filename.graphml ──────────────── [×] ─┐
│ Detected: yEd-raw graphml, 89 nodes, 6 folders, 2 periods,   │
│           187 edges (23 folder-touching).                    │
│                                                              │
│  §1. Classify leaf nodes (82) — QTableView with override     │
│     dropdown per row + "Apply prefix rule" batch action      │
│                                                              │
│  §2. Periods (from yEd table rows) — QTableView with         │
│     editable label + periodo + fase + checkbox to include    │
│     ⚠ Datazione fields stay NULL — fill from pyarchinit      │
│                                                              │
│  §3. Group folders (6) — QTableView with dropdown dimension  │
│     + editable value + "Apply prefix rule" batch action      │
│                                                              │
│  §4. Folder-touching edges (23) — radio group with policy    │
│     SKIP / FAN_OUT / REPRESENTATIVE / SYNTHETIC              │
│                                                              │
│  Dry-run: [✓] Preview SQL changes without committing         │
│  [Cancel] [Reset to auto-defaults]              [Import →]   │
└──────────────────────────────────────────────────────────────┘
```

### Components

Each section is a `QGroupBox` with either:
- `QTableView` + custom `QAbstractTableModel` (§1, §2, §3) — supports per-row edits
- `QButtonGroup` with `QRadioButton`s (§4)

### "Apply prefix rule" UX

In §1: dropdown of unique prefixes detected (`US*`, `USV*`, `SF*`, ...) + target `ClassificationKind`. Click "Apply all" → all rows matching that prefix updated in batch.

In §3: prefix dropdown + dimension dropdown + value template (`<prefix>` or `<label>`). "Apply to all matching" applies in batch.

### Cancel vs Reset

- **Cancel** — close dialog, nothing committed
- **Reset to auto-defaults** — restore all overrides to heuristic defaults

### Dry-run mode

If checked, the pipeline uses `_DryRunRollback` sentinel (pattern from PG-C) to wrap the entire INSERT/UPDATE in a transaction that rolls back at the end. Summary dialog shown post-run: "would insert 12 rows in us_table, 2 in inventario_materiali_table, 2 in periodizzazione_table, update 6 us_table.attivita columns, skip 23 folder-edges". User can confirm with `[Confirm Import]` or `[Back to edit]`.

Default: **unchecked** (commit immediately after confirm).

### Error handling

On DB error during INSERT/UPDATE:
- Transaction rollback (existing behavior)
- Modal error dialog with detail
- User returns to import dialog to modify choices

### i18n

All visible strings wrapped in `self.tr(...)` for translation (9 languages: it/en/de/es/fr/ar/ca/ro/pt).

### Test strategy

- **L0** (`tests/gui/test_yed_import_dialog_state.py`): instantiate dialog headless, populate with fixture drafts, simulate button clicks, verify state mutations
- **Manual GUI** in QGIS: import `EM_demo_02.graphml`, screenshot each section, validate UX flow

---

## 10. Backward compat + test strategy

### AC-2 byte-identical preservation

The pyarchinit-projected branch of `populate_list()` is **literally unchanged** post-detection. New code is purely additive (an early-return `if` branch at the top).

This guarantees:
- `test_ai03_export_byte_identical` passes (AC-2 gate)
- 3 critical SQLite regression gates pass (`test_round_trip_with_paradata`, `test_round_trip_with_groups`, `test_graph_projector_paradata`)
- 8 PG-D L2 tests pass
- 256 SQLite tests baseline unchanged

### New test inventory

| Level | File | What it tests |
|---|---|---|
| L0 | `test_yed_detector.py` | Detection logic, malformed fallback |
| L0 | `test_yed_classifier.py` | Regex map, prefix order, unknown fallback |
| L0 | `test_yed_table_parser.py` | Period extraction, Y-coordinate membership |
| L0 | `test_yed_group_walker.py` | Folder hierarchy, cycles, prefix mapping |
| L0 | `test_yed_rapporti_policy.py` | 4 policies, edge classification |
| L0 | `test_yed_import_dialog_state.py` | Dialog state machine headless |
| L1 | `test_yed_import_pipeline_em_demo.py` | End-to-end on mini fixture |
| L1 | `test_yed_import_pipeline_dry_run.py` | Dry-run + rollback sentinel |
| Manual | QGIS GUI | Real dialog rendering on full `EM_demo_02.graphml` |

### Fixture strategy

`EM_demo_02.graphml` (201KB, 89 nodes) is too big for L0 fixtures. Create `tests/fixtures/em_demo_02_mini.graphml` (~5KB):
- 1 TableNode with 2 rows (Period01, Period02)
- 2 group folders (VA01 attivita, AR01 area) — covers more dimensions
- 6 leaves: 2 US, 1 USV, 1 SF, 1 VSF, 1 PropertyNode
- 5 edges: 2 leaf-to-leaf, 1 folder-to-leaf, 1 leaf-to-folder, 1 folder-to-folder

### Test count progression

| Milestone | Tot passed (PG offline) | Delta |
|---|---|---|
| Baseline post-Phase 3 | 256 | — |
| yE-A (Foundation) | 260 | +4 (detector) |
| yE-B (Classifier) | 269 | +9 (classifier) |
| yE-C (Parsers) | 281 | +12 (parsers) |
| yE-D (Pipeline) | 291 | +10 (policy + pipeline integration) |
| yE-E (Dialog) | 297 | +6 (dialog state machine) |
| yE-Closure | 297 | docs only |

### Migrations / schema changes

**None.** Uses existing columns of `us_table`, `periodizzazione_table`, `inventario_materiali_table`. The only exception is the `SYNTHETIC` rapporti policy which requires vocab `VA` (deferred).

---

## 11. Decomposition into 6 sub-milestones

| Milestone | Tag | Ships | LOC est | Deps |
|---|---|---|---|---|
| **yE-A — Foundation** | `yed-import-foundation-5.7.5-alpha` | `yed_detector.py` + branch hook (no-op for yed-raw — just logs warning) | ~120 + 30 test | None |
| **yE-B — Classifier** | `yed-import-classifier-5.7.6-alpha` | `yed_classifier.py` standalone + L0 tests | ~150 + 80 test | yE-A |
| **yE-C — Parsers** | `yed-import-parsers-5.7.7-alpha` | `yed_table_parser.py` + `yed_group_walker.py` + L0 tests. Pipeline orchestrates parsers but no UI yet. | ~300 + 120 test | yE-B |
| **yE-D — Pipeline + policy** | `yed-import-pipeline-5.7.8-alpha` | `yed_rapporti_policy.py` + `yed_import_pipeline.py` + CLI `scripts/import_yed_graphml.py --auto-defaults`. L1 integration on mini fixture. | ~250 + 150 test | yE-C |
| **yE-E — Dialog UX** | `yed-import-dialog-5.7.9-alpha` | `gui/yed_import_dialog.py` + state-machine L0 test + manual QGIS test. Pipeline now passes through dialog. | ~400 + 100 test | yE-D |
| **yE-Closure** | `yed-import-closure-5.8.0-alpha` | Docs + tutorial (9 langs) + api-docs CHANGELOG + version bump + closure summary | ~150 docs | yE-E |

### Effort estimate

~7 person-days of dev work, ~10-12 calendar days with reviews and iterations.

### Versioning

Post-Phase 3 closed at `5.7.4-alpha`. yEd-aware import is a minor feature addition: progressive minor numbering yE-A → `5.7.5-alpha` ... yE-E → `5.7.9-alpha`, with closure bumping to `5.8.0-alpha` (minor bump signals feature complete).

---

## 12. Out of scope (explicitly deferred)

### Deferred to iteration 2 (post yE-Closure)

1. **Custom classifier rules via `.classifier.json` file**
2. **QSettings `pyarchinit/yed_classifier_rules` persistence**
3. **Save/Load preset of dialog choices** (for batch import workflows)
4. **Preview Harris matrix in dialog** (graphical preview pre-commit)
5. **Diff with current DB state** (show INSERT vs UPDATE breakdown pre-commit)

### Deferred to Phase 4 / SyncEngine

6. **`SYNTHETIC` rapporti policy default activation** — requires vocab `VA` migration
7. **Auto-detection of paradata nodes** (AuthorNode, LicenseNode) from yEd properties
8. **Round-trip on yEd-raw** — import → modify in pyarchinit → re-export → verify

### Explicitly NEVER (design decisions)

9. **Never modify the pyarchinit-projected path** — AC-2 byte-identical is sacred
10. **Never modify DB schema** — no new columns / tables / migrations
11. **Never modify `s3dgraphy` upstream** — vendored stays at `>=0.1.41`
12. **No non-graphml formats** (CSV/Excel/JSON from EM Datacenter) — different feature

---

## 13. References

- **Bug investigation**: this brainstorming session (2026-05-12)
- **Parent spec** (sync architecture): `docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md` §3, §4.1, §4.2
- **Phase 3 predecessor**: `phase3-pgcompat-consolidation-5.7.4-alpha` (commit `7064b1d1`)
- **Existing partial coverage**: `_apply_group_folders_to_sql` in `graph_ingestor.py:750` — only handles `pyarchinit.*` data keys (AI07)
- **Vendored s3dgraphy importer**: `ext_libs/s3dgraphy/importer/pyarchinit_importer.py`
- **Test fixture**: `/Users/enzo/Downloads/EM_demo_02.graphml` (89 nodes, 187 edges, 6 group folders, 2 period rows)

---

## 14. Approval log

- Sezione 1 Architecture: approvata 2026-05-12
- Sezione 2 Detection: approvata 2026-05-12
- Sezione 3 Classifier: approvata 2026-05-12
- Sezione 4 Period extraction: approvata 2026-05-12
- Sezione 5 Group folder walker: approvata 2026-05-12
- Sezione 6 Rapporti policy: approvata 2026-05-12
- Sezione 7 Dialog UX: approvata 2026-05-12
- Sezione 8 Backward compat + test: approvata 2026-05-12
- Sezione 9 Decomposition: approvata 2026-05-12
- Sezione 10 Out of scope: approvata 2026-05-12
- **Spec final review**: pending user (this step)
