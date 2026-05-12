# yE-B Classifier — Design Spec

**Date:** 2026-05-12
**Branch:** Stratigraph_00001
**Predecessor tag:** `yed-import-foundation-5.7.5-alpha` (commit `eb4fba81`)
**Target tag:** `yed-import-classifier-5.7.6-alpha`

---

## 1. Goal

Ship the second milestone of the 6-milestone yEd-aware graphml import rollout. yE-B adds:

1. `modules/s3dgraphy/sync/yed_classifier.py` — label-prefix → `ClassificationKind` heuristic for leaf nodes in yEd-raw graphmls
2. Wires the new classifier into the existing yE-A branch hook in `populate_list()`, replacing the bare warning with a classification summary log
3. 9 L0 unit tests + 1 L1 integration test on the `em_demo_02_mini.graphml` fixture

No user-visible behavior change beyond a richer log line. The legacy ingestion path remains unchanged (AC-2 byte-identical preserved).

This is the **β (integrated) interpretation** of yE-B per spec §11 of the parent design (`docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md`). The α (minimal) alternative was rejected during brainstorming 2026-05-12 because:
- β gives the user immediate visible feedback that the classifier works
- β has minimal AC-2 risk (the hook is already wrapped in `try/except Exception: pass`)
- β makes yE-C/D simpler to start (classifier already wired, parsers attach next)
- The L1 integration test in β catches classifier-regex-vs-fixture regressions that pure L0 unit tests on synthetic input cannot

---

## 2. Inherited from parent spec

This spec **inherits** the classifier design from parent spec §5:

- `ClassificationKind` enum (12 values: `US_REAL`, `US_MASONRY`, `US_DOCUMENTARY`, `USV_VIRTUAL`, `USV_FORMAL`, `SPECIAL_FIND`, `VIRTUAL_FIND`, `DOCUMENT`, `COMBINER`, `PROPERTY`, `UNKNOWN`, `SKIP`)
- `DEFAULT_CLASSIFIER_RULES` — 10 regex patterns, order-sensitive (USV*  before US*, VSF* before SF*, USM* before US*, USD* before US*)
- `ClassifiedNode` dataclass (yed_id, label, auto_kind, user_kind, extra_attrs)
- Function signature pattern

This spec **specializes** the parent design for the MVP:

- **Input is `Path | str` only** (NOT `Graph | Path | str` as parent spec said). Rationale: yE-A passes path-only to `detect_flavor`, consistent pattern. The classifier parses graphml directly via `lxml.etree.iterparse` (xml.etree fallback) — same pattern as `yed_detector.py` and `_apply_group_folders_to_sql`. Loading a full `s3dgraphy.Graph` instance just to classify would be wasteful for the "preview" use case yE-E will need.
- **No `rules=...` user override mechanism beyond function parameter** for MVP. `DEFAULT_CLASSIFIER_RULES` is the only ruleset shipped. QSettings persistence + `.classifier.json` config file are explicitly deferred to iteration 2 (per parent spec §12).
- **Folder nodes excluded from classification.** yE-C `yed_group_walker` handles folders. Classifier only processes `yfiles.foldertype != "group"` leaves.

---

## 3. Architecture

### Files created

| Path | Responsibility | LOC est |
|---|---|---|
| `modules/s3dgraphy/sync/yed_classifier.py` | `ClassificationKind` enum + `ClassifiedNode` dataclass + `DEFAULT_CLASSIFIER_RULES` regex map + `classify_leaves(graphml_path, rules=None)` function | ~150 |
| `tests/sync/test_yed_classifier.py` | 9 L0 unit tests for regex map + prefix order + unknown fallback + document order + case insensitivity | ~150 |
| `tests/sync/test_yed_classifier_integration.py` | 1 L1 integration test on `em_demo_02_mini.graphml` verifying count breakdown | ~80 |

### Files modified

| Path | Change | Delta |
|---|---|---|
| `modules/s3dgraphy/sync/graph_ingestor.py` | Branch hook at lines ~169-189 of `populate_list()`: replace bare warning with `classify_leaves()` call + `Counter` summary in log. Still no-op fall-through to legacy path. Same `try/except Exception: pass` wrapper from yE-A. | ~+20 / -5 |
| `metadata.txt` | Version bump 5.7.5-alpha → 5.7.6-alpha | 1 line |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.6-alpha]` section | ~50 |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Add yE-B section | ~40 |

### Files NOT touched

- `modules/s3dgraphy/sync/yed_detector.py` — yE-A scope, unchanged
- `tests/sync/fixtures/em_demo_02_mini.graphml` — yE-A fixture, reused as-is (already covers all classifier categories)
- Any other module in `modules/s3dgraphy/sync/` — yE-C/D/E territory
- DB schema, migrations, requirements.txt — no changes

### Total LOC

- Production: ~170 (~150 new + ~20 delta)
- Test: ~230 (150 L0 + 80 L1)
- Docs: ~90
- **Grand total: ~490 LOC**

---

## 4. Classifier module specification

### `modules/s3dgraphy/sync/yed_classifier.py`

```python
"""Label-prefix classifier for yEd-raw graphml leaf nodes.

Maps leaf node label patterns (US*, USV*, SF*, VSF*, D.*, C.*,
material/position/height/...) to ClassificationKind enum values
that drive the downstream import pipeline (yE-C onward).

The detection pattern is regex-based and order-sensitive: more
specific patterns (USV*, USM*, VSF*) must precede generic ones
(US*, SF*) to avoid mis-classification. The DEFAULT_CLASSIFIER_RULES
list is the single source of truth for MVP (yE-B); the dialog in
yE-E will let the user override per-node.

Folder nodes (yfiles.foldertype="group") are EXCLUDED from
classification — yE-C `yed_group_walker` handles them separately.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# 12-value enum mirroring parent spec §5
class ClassificationKind(str, Enum):
    US_REAL          = "us_real"
    US_MASONRY       = "us_masonry"
    US_DOCUMENTARY   = "us_documentary"
    USV_VIRTUAL      = "usv_virtual"
    USV_FORMAL       = "usv_formal"
    SPECIAL_FIND     = "special_find"
    VIRTUAL_FIND     = "virtual_find"
    DOCUMENT         = "document"
    COMBINER         = "combiner"
    PROPERTY         = "property"
    UNKNOWN          = "unknown"
    SKIP             = "skip"

# Default regex map (order-sensitive — first match wins)
DEFAULT_CLASSIFIER_RULES: list[tuple[re.Pattern, ClassificationKind]] = [
    (re.compile(r"^USVs\b|^USVn\b"),                ClassificationKind.USV_FORMAL),
    (re.compile(r"^USV\d+"),                        ClassificationKind.USV_VIRTUAL),
    (re.compile(r"^USM\d+|^USR\d+|^USS\d+"),        ClassificationKind.US_MASONRY),
    (re.compile(r"^USD\d+"),                        ClassificationKind.US_DOCUMENTARY),
    (re.compile(r"^US\d+"),                         ClassificationKind.US_REAL),
    (re.compile(r"^VSF\d+"),                        ClassificationKind.VIRTUAL_FIND),
    (re.compile(r"^SF\d+"),                         ClassificationKind.SPECIAL_FIND),
    (re.compile(r"^D\.\d+"),                        ClassificationKind.DOCUMENT),
    (re.compile(r"^C\.\d+"),                        ClassificationKind.COMBINER),
    (re.compile(
        r"^(material|position|width|length|height|heigth|type|color|weight|proportion|size)$",
        re.I,
    ),                                              ClassificationKind.PROPERTY),
]

@dataclass
class ClassifiedNode:
    """One leaf node classified by the heuristic.

    `auto_kind` is what the classifier produced.
    `user_kind` is initially equal to `auto_kind`; the yE-E dialog
    lets the user override per-node before commit. yE-B always
    leaves them equal (no dialog yet).
    """
    yed_id: str
    label: str
    auto_kind: ClassificationKind
    user_kind: ClassificationKind
    extra_attrs: dict = field(default_factory=dict)


def classify_leaves(
    graphml_path: Path | str,
    rules: list[tuple[re.Pattern, ClassificationKind]] | None = None,
) -> list[ClassifiedNode]:
    """Classify every leaf node in the graphml by label-prefix.

    Returns nodes in yEd document order (preserving authoring sequence,
    so the dialog in yE-E can present them in the order the user
    expects).

    Empty / malformed / missing file -> [] (safe default — caller
    falls through to legacy path).

    Folder nodes (yfiles.foldertype="group") are skipped — yE-C
    yed_group_walker handles them.
    """
```

### Algorithm

1. `lxml.etree.iterparse` (xml.etree fallback) on graphml path with `events=("start", "end")`
2. For each `<node>` end event:
   - Skip if `yfiles.foldertype == "group"`
   - Extract first non-empty `<y:NodeLabel>` text
   - Run rules in order; first match wins → `auto_kind`
   - No match → `ClassificationKind.UNKNOWN`
3. Build `ClassifiedNode(yed_id, label, auto_kind, user_kind=auto_kind)`
4. Append to result list
5. On parse error or missing file → `return []`

### Edge cases

- **No `<y:NodeLabel>` text or empty label** → `auto_kind=UNKNOWN`, `label=""`. yE-E dialog will surface these for manual mapping.
- **Multiple `<y:NodeLabel>` per node** → use the FIRST one with non-empty text (matches yE-A `_apply_group_folders_to_sql` behaviour)
- **Leaf inside a folder ancestor** → STILL classified. Folder membership is yE-C's responsibility, not the classifier's.
- **File missing / parse error** → return `[]`. Same safe-default discipline as `yed_detector.py`.
- **Unicode in labels** → handled naturally by regex (re module is Unicode-aware on str)

---

## 5. Branch hook update

### Current state (yE-A in `graph_ingestor.py` ~lines 169-189)

```python
if graphml_path is not None:
    try:
        from .yed_detector import detect_flavor
        if detect_flavor(graphml_path) == "yed-raw":
            import logging
            logging.getLogger(__name__).warning(
                "yEd-raw graphml detected at %s -- yed-aware "
                "import path not yet implemented (yE-A "
                "foundation only). Falling through to legacy "
                "path. Expect partial/incorrect ingestion.",
                graphml_path,
            )
    except Exception:
        # Detection is best-effort; never block the legacy path
        pass
```

### Updated state (yE-B)

```python
if graphml_path is not None:
    try:
        from .yed_detector import detect_flavor
        if detect_flavor(graphml_path) == "yed-raw":
            import logging
            from collections import Counter
            from .yed_classifier import classify_leaves
            classified = classify_leaves(graphml_path)
            counts = Counter(n.auto_kind.value for n in classified)
            summary = ", ".join(
                f"{k}: {v}" for k, v in sorted(counts.items())
            )
            logging.getLogger(__name__).warning(
                "yEd-raw graphml detected at %s. Classified %d "
                "leaves: %s. Yed-aware import path not yet wired "
                "(yE-B classifier only). Falling through to legacy "
                "path. Expect partial/incorrect ingestion.",
                graphml_path, len(classified), summary,
            )
    except Exception:
        # Detection + classification is best-effort; never block legacy
        pass
```

### Properties preserved

- Single if-branch, no other code changes in `populate_list()`
- Lazy imports of `detect_flavor` and `classify_leaves` (inside the function, not at module top)
- Outer `try/except Exception: pass` ensures classifier errors never block legacy path → AC-2 byte-identical preserved
- Fall-through semantics unchanged (legacy code below this block runs as before)

---

## 6. Test strategy

### L0 unit tests (`tests/sync/test_yed_classifier.py`) — 9 tests

| # | Test name | What it verifies |
|---|---|---|
| 1 | `test_classify_us_prefix` | `US01` → `US_REAL` |
| 2 | `test_classify_usv_prefix` | `USV101` → `USV_VIRTUAL` |
| 3 | `test_classify_usm_prefix_wins_over_us` | `USM6` matches `USM\d+` NOT `US\d+` (order-sensitive) |
| 4 | `test_classify_special_find` | `SF105` → `SPECIAL_FIND` |
| 5 | `test_classify_virtual_find_wins_over_special` | `VSF107` matches `VSF\d+` NOT `SF\d+` (order) |
| 6 | `test_classify_document_with_subdots` | `D.01.03` → `DOCUMENT` (regex `^D\.\d+` accepts subdots) |
| 7 | `test_classify_property_case_insensitive` | `Material`, `material`, `MATERIAL`, `Heigth` → `PROPERTY` |
| 8 | `test_classify_unknown_falls_through` | `Foundation_01` (no prefix match) → `UNKNOWN` |
| 9 | `test_classify_uses_yed_document_order` | Returned order matches `<node id=>` document order in XML |

Each test uses a synthetic graphml string in `tmp_path` — no need for new persistent fixtures.

### L1 integration test (`tests/sync/test_yed_classifier_integration.py`) — 1 test

```python
def test_classify_em_demo_02_mini_smoke():
    """End-to-end: run classify_leaves on the yE-A reference fixture
    and verify the count breakdown matches the known structure.
    
    Mini fixture has 6 leaves:
      - 2 US (US01, US02)        → US_REAL
      - 1 USV (USV101)           → USV_VIRTUAL
      - 1 SF (SF105)             → SPECIAL_FIND
      - 1 VSF (VSF107)           → VIRTUAL_FIND
      - 1 Property (material)    → PROPERTY
    """
```

### Regression gates (must stay green after Group A)

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v  # AC-2
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py tests/sync/test_round_trip_with_groups.py tests/sync/test_graph_projector_paradata.py -v  # 3 critical SQLite gates
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py tests/sync/test_group_store_pg.py -v  # 8 PG-D L2
PYTHONPATH="$PWD" python -m pytest tests/sync/test_yed_detector.py -v  # 5 yE-A tests preserved
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no  # full suite
```

### Test count progression

- Pre yE-B (post yE-A): `261 passed, 33 skipped` (PG offline)
- Post yE-B Group A: `271 passed, 33 skipped` (+9 L0 + 1 L1)
- Post yE-B Group B/C: unchanged
- **Final (PG offline):** `271 passed, 33 skipped`
- **Final (PG online + psycopg2):** `279 passed, 12 skipped`

---

## 7. Decomposition (5 Groups, same pattern as yE-A)

| Group | Scope | Subagent | LOC est |
|---|---|---|---|
| Group 0 | Pre-flight: clean state check, baseline test counts, rollback tag `pre-yed-import-classifier` | Controller-only (pure git) | — |
| Group A | Production: `yed_classifier.py` + 9 L0 + 1 L1 + hook update in `graph_ingestor.py` | 1 subagent | ~170 prod + ~230 test |
| Group B | Docs: bump 5.7.5 → 5.7.6-alpha + bilingual CHANGELOG + dev-log yE-B section | 1 subagent | ~90 docs |
| Group C | Annotated tag `yed-import-classifier-5.7.6-alpha` + USER APPROVAL GATE + push | 1 subagent (stop at gate); controller pushes after approval | — |
| Memory | Update `project_yed_import_progress.md` with yE-B SHIPPED + MEMORY.md index line | Controller-only | — |

### Effort estimate

~1 person-day of dev work + ~0.5 of review/iteration = 1.5 calendar days.

---

## 8. Acceptance criteria

### Per Group A

- `yed_classifier.py` exists with `ClassificationKind`, `DEFAULT_CLASSIFIER_RULES`, `ClassifiedNode`, `classify_leaves` matching this spec
- 9 L0 tests pass with exact names from §6
- 1 L1 test passes on `em_demo_02_mini.graphml`
- `graph_ingestor.py` branch hook updated per §5; remains no-op fall-through; outer `try/except` preserved
- AC-2 byte-identical preserved (`test_ai03_export_byte_identical` passes unchanged)
- 3 critical SQLite regression gates preserved
- 5 yE-A detector tests preserved
- 8 PG-D L2 tests preserved (skip cleanly when PG offline)
- Full suite: 271 passed, 33 skipped (PG offline)
- Commit SHA has 0 `^Co-Authored-By:` line-anchored regex hits

### Per Group B

- `metadata.txt` shows `version=5.7.6-alpha`
- Bilingual CHANGELOG entry added at top of `dev_logs/CHANGELOG.md`
- Dev-log yE-B section added to `T5.4_PyArchInit_Dev_Log.md`
- Commit SHA has 0 trailer issues

### Per Group C

- Tag `yed-import-classifier-5.7.6-alpha` is annotated (`git cat-file -t` returns "tag")
- Tag points to Group B commit
- Tag message has 0 trailer issues
- **STOP at Task C.4** — user manual test plan presented, await `approvato` before push
- After user approval: tag + branch pushed to origin

---

## 9. Out of scope / explicitly deferred

### Deferred to iteration 2 (post yE-Closure)

- Custom classifier rules via `.classifier.json` file (parent spec §12)
- QSettings `pyarchinit/yed_classifier_rules` persistence (parent spec §12)
- Save/Load preset of classifier overrides

### Deferred to later milestones

- **yE-C**: Parser for yEd TableNode rows → periodizzazione (`yed_table_parser.py`) + folder walker (`yed_group_walker.py`)
- **yE-D**: Rapporti policy + `yed_import_pipeline.py` orchestrator + CLI script + real SQL writes
- **yE-E**: Qt dialog UX (4 sections including classifier override per node)
- **yE-Closure**: Docs + tutorial + api-docs CHANGELOG + version bump to 5.8.0-alpha

### Explicitly NEVER (design decisions)

- yE-B does NOT touch the pyarchinit-projected branch (AC-2 sacred)
- yE-B does NOT modify DB schema
- yE-B does NOT modify `s3dgraphy` upstream
- yE-B's classifier does NOT run on folders (delegated to yE-C `yed_group_walker`)

---

## 10. References

- **Parent spec**: `docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md` §5 (Classifier), §11 (Decomposition), §12 (Out of scope)
- **Predecessor (yE-A)**: `docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md` (Foundation already shipped)
- **yE-A memory**: `~/.claude/projects/.../memory/project_yed_import_progress.md`
- **Test fixture (reused)**: `tests/sync/fixtures/em_demo_02_mini.graphml`
- **Hook location**: `modules/s3dgraphy/sync/graph_ingestor.py:169-189` (yE-A added the block; yE-B updates lines inside it)

---

## 11. Approval log

- Section 1 Architecture + files: approved 2026-05-12
- Section 2 Classifier internals + branch hook: approved 2026-05-12
- Section 3 Test strategy + decomposition: approved 2026-05-12
- **Spec final review**: pending user (this step)
