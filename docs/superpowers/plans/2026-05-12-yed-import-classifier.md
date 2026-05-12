# yE-B Classifier — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the second milestone of the 6-milestone yEd-aware graphml import rollout: a label-prefix classifier (`yed_classifier.py`) wired into the yE-A branch hook, so importing a yEd-raw graphml now logs a classification summary (e.g., "Classified 82 leaves: us_real: 4, usv_virtual: 8, special_find: 2, ...") before falling through to the legacy path. No user-visible behavior change beyond the richer log line.

**Architecture:** Pure additive — one new module (`yed_classifier.py`) + one new L0 test file + one new L1 test file. The yE-A branch hook in `populate_list()` is updated in-place to invoke `classify_leaves()` and emit a `Counter`-based summary. The outer `try/except Exception: pass` wrapper from yE-A is preserved, so classifier errors never block the legacy path. AC-2 byte-identical + 3 critical SQLite regression gates + 8 PG-D L2 tests + 5 yE-A detector tests all stay green untouched.

**Tech Stack:** Python 3.9+, `lxml.etree.iterparse` (with `xml.etree.iterparse` fallback), `re` (regex), `dataclasses`, `enum.Enum`, `collections.Counter`, pytest.

**Spec source of truth:** `docs/superpowers/specs/2026-05-12-yed-import-classifier-design.md` (commit `c0afd1fe`).

**Parent spec (inherited from):** `docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md` (commit `43fc5cb8`).

**Predecessor tag:** `yed-import-foundation-5.7.5-alpha` (commit `eb4fba81`).

**Target tag:** `yed-import-classifier-5.7.6-alpha`.

**Memory notes to consult before refactoring:**
- `~/.claude/projects/.../memory/feedback_no_claude_coauthor.md` — strict commit-author rule
- `~/.claude/projects/.../memory/project_yed_import_progress.md` — yE-A SHIPPED + lessons learned
- `~/.claude/projects/.../memory/MEMORY.md` — top-level index

**Strict commit-author rule:** never include trailers identifying Claude as a co-author. After each commit run `git log -1 --format=%B HEAD | grep -cE '^Co-Authored-By:'` — must return `0`. **CAUTION:** avoid the literal hyphenated phrase in commit body prose where possible (the regex-anchored check filters it correctly, but unsuspecting `grep -c Co-Authored-By` would not).

---

## File Structure

### Created

| Path | Responsibility |
|---|---|
| `modules/s3dgraphy/sync/yed_classifier.py` | `ClassificationKind` enum (12 values) + `DEFAULT_CLASSIFIER_RULES` regex map (10 order-sensitive patterns) + `ClassifiedNode` dataclass + `classify_leaves(graphml_path, rules=None)` function. Parses graphml via lxml/xml.etree iterparse. Excludes folder nodes. Safe-default `[]` on error. |
| `tests/sync/test_yed_classifier.py` | 9 L0 tests for prefix order, case insensitivity, unknown fallback, document order. Uses synthetic graphml strings in `tmp_path`. |
| `tests/sync/test_yed_classifier_integration.py` | 1 L1 test on `em_demo_02_mini.graphml` (yE-A reference fixture). Verifies count breakdown matches the fixture's 6 leaves. |

### Modified

| Path | Why | LOC delta |
|---|---|---|
| `modules/s3dgraphy/sync/graph_ingestor.py` | Replace yE-A bare warning at lines 169-189 with classifier invocation + `Counter` summary log. Preserves `try/except Exception: pass` wrapper, lazy imports, no-op fall-through to legacy path. | +15 / -3 |
| `metadata.txt` | Bump `version=5.7.5-alpha` → `version=5.7.6-alpha` | 1 |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.6-alpha]` section | ~50 |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Prepend "yE-B Classifier (5.7.6-alpha)" section | ~40 |

### Explicitly NOT touched

- `modules/s3dgraphy/sync/yed_detector.py` — yE-A scope, unchanged
- `tests/sync/fixtures/em_demo_02_mini.graphml` — yE-A fixture, reused as-is (already covers all classifier categories)
- `tests/sync/test_yed_detector.py` — yE-A tests preserved
- The pyarchinit-projected branch of `populate_list()` — stays byte-identically the same
- `vocab_provider.py`, `paradata_store.py`, `group_store.py`, `_workspace.py`, `_db_handle.py`, `graphml_writer.py`, `graph_projector.py`, `group_projector.py` — all out of yE-B scope
- DB schema — no migrations
- `requirements.txt` — no new dependencies (lxml already used)

### Total LOC

- Production: ~165 (~150 new + ~15 delta)
- Test: ~230 (150 L0 + 80 L1)
- Docs: ~90
- **Grand total: ~485 LOC**

---

## Test strategy

- **L0 unit (NEW):** `test_yed_classifier.py` — 9 tests with synthetic graphml strings in `tmp_path`. Pure pytest, no Qt, no PG. Always runs.
- **L1 integration (NEW):** `test_yed_classifier_integration.py` — 1 test on `em_demo_02_mini.graphml`. Pure pytest, no Qt, no PG.
- **L1 SQLite (existing 261):** Stay green. Pyarchinit-projected branch untouched; new yEd-raw branch is a no-op fall-through.
- **L2 PG (existing 8 from PG-D):** Stay green or skip cleanly. They never touch graphml-import code.
- **L3 regression guards (existing, MUST stay green after Group A):**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v   # AC-2
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py tests/sync/test_round_trip_with_groups.py tests/sync/test_graph_projector_paradata.py -v   # 3 critical SQLite gates
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py tests/sync/test_group_store_pg.py -v   # 8 PG-D L2
PYTHONPATH="$PWD" python -m pytest tests/sync/test_yed_detector.py -v   # 5 yE-A tests preserved
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no
```

After Group A, ALL of these must PASS (or SKIP for PG L2 when PG offline). If any breaks → STOP and report BLOCKED.

### Decision pinning

| Decision / Acceptance | Pinning test |
|---|---|
| `DEFAULT_CLASSIFIER_RULES` order: USM before US | `test_classify_usm_prefix_wins_over_us` |
| `DEFAULT_CLASSIFIER_RULES` order: VSF before SF | `test_classify_virtual_find_wins_over_special` |
| Property regex is case-insensitive | `test_classify_property_case_insensitive` |
| Unknown prefix falls through to UNKNOWN | `test_classify_unknown_falls_through` |
| Output preserves yEd document order | `test_classify_uses_yed_document_order` |
| Folder nodes excluded | `test_classify_em_demo_02_mini_smoke` (asserts VA01/AR01 NOT in labels) |
| Hook integration produces correct counts | `test_classify_em_demo_02_mini_smoke` (asserts 2 US_REAL + 1 USV_VIRTUAL + 1 SPECIAL_FIND + 1 VIRTUAL_FIND + 1 PROPERTY = 6) |
| AC-2 byte-identical preserved | Existing `test_ai03_export_byte_identical` passes after hook update |
| 5 yE-A detector tests preserved | Existing `test_yed_detector.py` tests pass after hook update |

### Test count progression

- Pre yE-B (post yE-A): `261 passed, 33 skipped` (PG offline)
- Post Group A (+9 L0 + 1 L1): `271 passed, 33 skipped`
- Post Group B (docs only): `271 passed, 33 skipped` (unchanged)
- Post Group C (tag only): unchanged
- **Final (PG offline):** `271 passed, 33 skipped`
- **Final (PG online + psycopg2):** `279 passed, 12 skipped`

---

## Group 0 — Pre-flight & rollback safety

### Task 0.1: Verify clean starting point

**Files:** none (pure git operation)

- [ ] **Step 1: Confirm current branch + HEAD**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git rev-parse --abbrev-ref HEAD
git log --oneline -3
git rev-list --left-right --count HEAD...@{u}
```

Expected:
- branch: `Stratigraph_00001`
- HEAD: `c0afd1fe spec(yE-B): classifier milestone design`
- ahead/behind origin: `1\t0` (1 commit ahead — the yE-B spec — not yet pushed)

If branch is anything else → **STOP and ask** before proceeding.

- [ ] **Step 2: Verify predecessor tag**

```bash
git tag --list | grep -E "yed-import-foundation-5.7.5-alpha"
```

Expected: `yed-import-foundation-5.7.5-alpha` listed.

- [ ] **Step 3: Capture baselines (regression gates)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py tests/sync/test_round_trip_with_groups.py tests/sync/test_graph_projector_paradata.py -v 2>&1 | tail -10
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py tests/sync/test_group_store_pg.py -v 2>&1 | tail -10
PYTHONPATH="$PWD" python -m pytest tests/sync/test_yed_detector.py -v 2>&1 | tail -10
```

Expected:
- Full suite: `261 passed, 33 skipped`
- AC-2: `1 passed`
- round_trip: `1 passed`
- 3 critical gates: `8 passed`
- 8 PG-D L2: `8 skipped` (PG offline — acceptable)
- 5 yE-A detector tests: `5 passed`

### Task 0.2: Create rollback safety tag

- [ ] **Step 1: Create + push rollback tag**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git tag -a pre-yed-import-classifier -m "Rollback point before yE-B Classifier milestone

Predecessor tag: yed-import-foundation-5.7.5-alpha (eb4fba81)
Spec commit: c0afd1fe (local-only at tag time)

If yE-B needs to be reverted, reset hard to this tag."
git push origin pre-yed-import-classifier 2>&1 | tail -3
```

Expected: `* [new tag]         pre-yed-import-classifier -> pre-yed-import-classifier`

---

## Group A — `yed_classifier.py` + 9 L0 tests + 1 L1 test + hook update

The only production-code Group. ~165 LOC production + ~230 LOC test.

**CRITICAL RULES (surface in subagent prompt):**
- `yed_classifier.py` body matches Task A.2 EXACTLY
- `DEFAULT_CLASSIFIER_RULES` list order is sacred (USV* before US*, USM* before US*, USD* before US*, VSF* before SF*) — wrong order breaks `test_classify_usm_prefix_wins_over_us` and `test_classify_virtual_find_wins_over_special`
- `classify_leaves()` signature is `Path | str` only (NOT Graph union)
- Folder nodes (`yfiles.foldertype="group"`) MUST be excluded from results
- Hook update preserves outer `try/except Exception: pass` wrapper from yE-A, lazy imports, no-op fall-through
- **AC-2 + 3 critical SQLite regression gates + 8 PG-D L2 + 5 yE-A detector tests sanity ping IMMEDIATELY after the commit** — if any breaks, STOP and report BLOCKED

### Task A.1: Create `modules/s3dgraphy/sync/yed_classifier.py`

**Files:**
- Create: `modules/s3dgraphy/sync/yed_classifier.py`

- [ ] **Step 1: Create the module**

Use the Write tool to create `modules/s3dgraphy/sync/yed_classifier.py` with EXACTLY this content:

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
classification -- yE-C `yed_group_walker` handles them separately.

Added in yE-B (yed-import-classifier-5.7.6-alpha). Inherits design
from parent spec docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md §5
specialized to Path-only input for MVP.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ClassificationKind(str, Enum):
    """12-value enum for leaf classification destinations."""
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


# Default regex map (ORDER-SENSITIVE -- first match wins).
# Specific prefixes (USV, USM, USD, VSF) MUST precede generic
# ones (US, SF) to avoid mis-classification.
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

    Empty / malformed / missing file -> [] (safe default -- caller
    falls through to legacy path).

    Folder nodes (yfiles.foldertype="group") are skipped -- yE-C
    yed_group_walker handles them.

    Args:
        graphml_path: filesystem path to the .graphml file.
        rules: optional override of DEFAULT_CLASSIFIER_RULES (for
            unit testing or future extensibility). None uses default.

    Returns:
        List of ClassifiedNode in document order. Empty list on any
        error (file missing, parse error, etc.).
    """
    path = Path(graphml_path)
    if not path.exists():
        return []

    active_rules = rules if rules is not None else DEFAULT_CLASSIFIER_RULES

    try:
        from lxml import etree as _ET
    except ImportError:
        import xml.etree.ElementTree as _ET  # type: ignore[no-redef]

    GRAPHML_NS = "{http://graphml.graphdrawing.org/xmlns}"
    Y_NS = "{http://www.yworks.com/xml/graphml}"

    result: list[ClassifiedNode] = []
    try:
        context = _ET.iterparse(str(path), events=("end",))
        for _event, elem in context:
            if elem.tag != f"{GRAPHML_NS}node":
                continue
            # Skip group folders -- yE-C territory
            if elem.get("yfiles.foldertype") == "group":
                elem.clear()
                continue

            yed_id = elem.get("id") or ""
            # Find first non-empty NodeLabel descendant text
            label = ""
            for nl in elem.iter(f"{Y_NS}NodeLabel"):
                txt = (nl.text or "").strip()
                if txt:
                    label = txt
                    break

            # Run rules in order; first match wins
            kind = ClassificationKind.UNKNOWN
            for pattern, target_kind in active_rules:
                if pattern.match(label):
                    kind = target_kind
                    break

            result.append(ClassifiedNode(
                yed_id=yed_id,
                label=label,
                auto_kind=kind,
                user_kind=kind,
            ))
            elem.clear()
    except Exception:
        # Parse errors / IO errors -> safe-default empty list
        return []

    return result
```

- [ ] **Step 2: Verify the module imports cleanly**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
PYTHONPATH="$PWD" python -c "
from modules.s3dgraphy.sync.yed_classifier import (
    classify_leaves, ClassificationKind, ClassifiedNode, DEFAULT_CLASSIFIER_RULES
)
print('imports OK')
print('Rules count:', len(DEFAULT_CLASSIFIER_RULES))
print('Enum values:', len(list(ClassificationKind)))
# Smoke test on yE-A fixture
from collections import Counter
nodes = classify_leaves('tests/sync/fixtures/em_demo_02_mini.graphml')
print(f'em_demo_02_mini: {len(nodes)} leaves')
print('Counter:', dict(Counter(n.auto_kind.value for n in nodes)))
"
```

Expected:
```
imports OK
Rules count: 10
Enum values: 12
em_demo_02_mini: 6 leaves
Counter: {'us_real': 2, 'usv_virtual': 1, 'special_find': 1, 'virtual_find': 1, 'property': 1}
```

If counts mismatch → debug the classifier before continuing.

### Task A.2: Create `tests/sync/test_yed_classifier.py` (9 L0 tests)

**Files:**
- Create: `tests/sync/test_yed_classifier.py`

- [ ] **Step 1: Create the test file**

Use the Write tool with EXACTLY this content:

```python
"""yE-B Classifier: L0 unit tests for classify_leaves().

Verifies the regex map ordering, case insensitivity, unknown fallback,
and document-order preservation. Each test builds a synthetic graphml
in tmp_path and exercises classify_leaves() against it.

Tests are independent (no shared state, no fixture files modified).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.s3dgraphy.sync.yed_classifier import (
    ClassificationKind,
    classify_leaves,
)


def _make_graphml(tmp_path: Path, labels: list[str]) -> Path:
    """Build a minimal yEd-styled graphml with one leaf per label."""
    nodes_xml = []
    for i, lbl in enumerate(labels):
        nodes_xml.append(
            f'<node id="n{i}">'
            f'<data key="d6">'
            f'<y:ShapeNode>'
            f'<y:NodeLabel>{lbl}</y:NodeLabel>'
            f'</y:ShapeNode>'
            f'</data>'
            f'</node>'
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns" '
        'xmlns:y="http://www.yworks.com/xml/graphml">\n'
        '  <key for="node" id="d6" yfiles.type="nodegraphics"/>\n'
        '  <graph edgedefault="directed" id="G">\n'
        f'    {"".join(nodes_xml)}\n'
        '  </graph>\n'
        '</graphml>\n'
    )
    path = tmp_path / "test.graphml"
    path.write_text(xml)
    return path


def test_classify_us_prefix(tmp_path):
    """US01 -> US_REAL."""
    path = _make_graphml(tmp_path, ["US01"])
    result = classify_leaves(path)
    assert len(result) == 1
    assert result[0].auto_kind == ClassificationKind.US_REAL
    assert result[0].label == "US01"
    assert result[0].user_kind == ClassificationKind.US_REAL


def test_classify_usv_prefix(tmp_path):
    """USV101 -> USV_VIRTUAL."""
    path = _make_graphml(tmp_path, ["USV101"])
    result = classify_leaves(path)
    assert len(result) == 1
    assert result[0].auto_kind == ClassificationKind.USV_VIRTUAL


def test_classify_usm_prefix_wins_over_us(tmp_path):
    """USM6 matches USM\\d+ (US_MASONRY), NOT US\\d+ (US_REAL).
    Verifies the order-sensitive regex list: USM precedes US."""
    path = _make_graphml(tmp_path, ["USM6"])
    result = classify_leaves(path)
    assert len(result) == 1
    assert result[0].auto_kind == ClassificationKind.US_MASONRY


def test_classify_special_find(tmp_path):
    """SF105 -> SPECIAL_FIND."""
    path = _make_graphml(tmp_path, ["SF105"])
    result = classify_leaves(path)
    assert len(result) == 1
    assert result[0].auto_kind == ClassificationKind.SPECIAL_FIND


def test_classify_virtual_find_wins_over_special(tmp_path):
    """VSF107 matches VSF\\d+ (VIRTUAL_FIND), NOT SF\\d+ (SPECIAL_FIND).
    Verifies the order-sensitive regex list: VSF precedes SF."""
    path = _make_graphml(tmp_path, ["VSF107"])
    result = classify_leaves(path)
    assert len(result) == 1
    assert result[0].auto_kind == ClassificationKind.VIRTUAL_FIND


def test_classify_document_with_subdots(tmp_path):
    """D.01.03 -> DOCUMENT (regex ^D\\.\\d+ matches the leading D.NN
    portion; trailing .03 is allowed)."""
    path = _make_graphml(tmp_path, ["D.01.03"])
    result = classify_leaves(path)
    assert len(result) == 1
    assert result[0].auto_kind == ClassificationKind.DOCUMENT


def test_classify_property_case_insensitive(tmp_path):
    """material / Material / MATERIAL / Heigth all -> PROPERTY."""
    path = _make_graphml(tmp_path,
                         ["material", "Material", "MATERIAL", "Heigth"])
    result = classify_leaves(path)
    assert len(result) == 4
    for node in result:
        assert node.auto_kind == ClassificationKind.PROPERTY, (
            f"Expected PROPERTY for {node.label!r}, got {node.auto_kind}"
        )


def test_classify_unknown_falls_through(tmp_path):
    """Foundation_01 has no prefix match -> UNKNOWN."""
    path = _make_graphml(tmp_path, ["Foundation_01"])
    result = classify_leaves(path)
    assert len(result) == 1
    assert result[0].auto_kind == ClassificationKind.UNKNOWN


def test_classify_uses_yed_document_order(tmp_path):
    """Returned list preserves yEd <node id=> document order."""
    path = _make_graphml(tmp_path,
                         ["US01", "USV101", "SF105", "D.01"])
    result = classify_leaves(path)
    assert len(result) == 4
    assert [n.label for n in result] == ["US01", "USV101", "SF105", "D.01"]
    assert [n.yed_id for n in result] == ["n0", "n1", "n2", "n3"]
```

- [ ] **Step 2: Run the 9 L0 tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_yed_classifier.py -v 2>&1 | tail -15
```

Expected: `9 passed`.

If any test fails, the classifier implementation has a bug. STOP and investigate before continuing.

### Task A.3: Create `tests/sync/test_yed_classifier_integration.py` (1 L1 test)

**Files:**
- Create: `tests/sync/test_yed_classifier_integration.py`

- [ ] **Step 1: Create the test file**

Use the Write tool with EXACTLY this content:

```python
"""yE-B Classifier: L1 integration test on em_demo_02_mini fixture.

Runs classify_leaves on the yE-A reference fixture and verifies
the count breakdown matches the known structure of the fixture.
This catches regex-vs-fixture mismatches that pure L0 unit tests
on synthetic input cannot.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

from modules.s3dgraphy.sync.yed_classifier import (
    ClassificationKind,
    classify_leaves,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_classify_em_demo_02_mini_smoke():
    """End-to-end: classify_leaves on em_demo_02_mini.graphml.

    Mini fixture has 6 leaves (from yE-A):
      - 2 US (US01, US02)        -> US_REAL
      - 1 USV (USV101)           -> USV_VIRTUAL
      - 1 SF (SF105)             -> SPECIAL_FIND
      - 1 VSF (VSF107)           -> VIRTUAL_FIND
      - 1 Property (material)    -> PROPERTY

    Folder nodes (VA01-foundation example, AR01-area example)
    must be EXCLUDED from the classified list -- they're handled
    by yE-C yed_group_walker.
    """
    fixture = FIXTURES / "em_demo_02_mini.graphml"
    assert fixture.exists(), f"Expected yE-A fixture at {fixture}"

    classified = classify_leaves(fixture)

    # Count breakdown
    counts = Counter(n.auto_kind for n in classified)
    assert counts[ClassificationKind.US_REAL]      == 2, f"Got {counts}"
    assert counts[ClassificationKind.USV_VIRTUAL]  == 1, f"Got {counts}"
    assert counts[ClassificationKind.SPECIAL_FIND] == 1, f"Got {counts}"
    assert counts[ClassificationKind.VIRTUAL_FIND] == 1, f"Got {counts}"
    assert counts[ClassificationKind.PROPERTY]     == 1, f"Got {counts}"

    # Total leaves count
    assert len(classified) == 6, f"Expected 6 leaves, got {len(classified)}"

    # Folder labels MUST NOT appear in the classified list
    labels = {n.label for n in classified}
    assert "VA01-foundation example" not in labels, \
        f"Folder VA01 leaked into classified leaves: {labels}"
    assert "AR01-area example" not in labels, \
        f"Folder AR01 leaked into classified leaves: {labels}"

    # All user_kind should equal auto_kind (no dialog override in yE-B)
    for n in classified:
        assert n.user_kind == n.auto_kind, (
            f"user_kind {n.user_kind} != auto_kind {n.auto_kind} "
            f"for {n.label}"
        )
```

- [ ] **Step 2: Run the L1 integration test**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_yed_classifier_integration.py -v 2>&1 | tail -10
```

Expected: `1 passed`.

If the test fails with wrong counts, check the classifier logic against the fixture structure. The fixture is unchanged from yE-A; the assertions encode the expected structure.

### Task A.4: Update branch hook in `graph_ingestor.py`

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_ingestor.py` (replace yE-A block at lines 169-189)

- [ ] **Step 1: Locate the current yE-A hook**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
sed -n '169,195p' modules/s3dgraphy/sync/graph_ingestor.py
```

The current yE-A block reads (verified at plan-writing time):

```python
        # yE-A Foundation (5.7.5-alpha): yEd-raw detection hook.
        # When graphml_path is provided AND it's a yEd-raw file (no
        # pyarchinit.* keys), log a warning and fall through to the
        # existing path. yE-B+ will replace this no-op with real
        # dispatch to yed_import_pipeline.import_yed_raw().
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
        # -- existing pyarchinit-projected path UNCHANGED below --
```

- [ ] **Step 2: Make the edit**

Use the Edit tool to replace the block above with EXACTLY this updated version (yE-B):

Find this `old_string`:

```python
        # yE-A Foundation (5.7.5-alpha): yEd-raw detection hook.
        # When graphml_path is provided AND it's a yEd-raw file (no
        # pyarchinit.* keys), log a warning and fall through to the
        # existing path. yE-B+ will replace this no-op with real
        # dispatch to yed_import_pipeline.import_yed_raw().
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
        # -- existing pyarchinit-projected path UNCHANGED below --
```

Replace with this `new_string`:

```python
        # yE-A + yE-B: yEd-raw detection + classifier preview.
        # When graphml_path is provided AND it's a yEd-raw file (no
        # pyarchinit.* keys), classify its leaves and log a summary.
        # Then fall through to the existing legacy path (full pipeline
        # wiring lands in yE-C+).
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
                # Detection + classification is best-effort;
                # never block the legacy path
                pass
        # -- existing pyarchinit-projected path UNCHANGED below --
```

- [ ] **Step 3: Syntax check**

```bash
PYTHONPATH="$PWD" python -c "
import ast
with open('modules/s3dgraphy/sync/graph_ingestor.py') as f:
    ast.parse(f.read())
print('graph_ingestor.py syntax OK')
"
```

Expected: `graph_ingestor.py syntax OK`.

- [ ] **Step 4: Verify the hook runs end-to-end on the real EM_demo_02.graphml**

```bash
PYTHONPATH="$PWD" python -c "
from modules.s3dgraphy.sync.yed_classifier import classify_leaves
from collections import Counter
path = '/Users/enzo/Downloads/EM_demo_02.graphml'
import os
if os.path.exists(path):
    classified = classify_leaves(path)
    counts = Counter(n.auto_kind.value for n in classified)
    print(f'classified={len(classified)} leaves')
    for k, v in sorted(counts.items()):
        print(f'  {k}: {v}')
else:
    print(f'NOTE: {path} not available in this env; skipping real-fixture check')
"
```

Expected output (if the file exists):
```
classified=82 leaves
  combiner: 3
  document: 38
  property: 23
  special_find: 2
  unknown: 2
  us_real: 4
  usv_virtual: 8
  virtual_find: 2
```

If the file does NOT exist, the note message is fine — the integration test on em_demo_02_mini.graphml is the real gate.

### Task A.5: Run full regression suite

- [ ] **Step 1: Run all gates**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py tests/sync/test_round_trip_with_groups.py tests/sync/test_graph_projector_paradata.py -v 2>&1 | tail -10
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py tests/sync/test_group_store_pg.py -v 2>&1 | tail -10
PYTHONPATH="$PWD" python -m pytest tests/sync/test_yed_detector.py tests/sync/test_yed_classifier.py tests/sync/test_yed_classifier_integration.py -v 2>&1 | tail -25
```

Expected:
- Full suite: `271 passed, 33 skipped` (261 baseline + 9 L0 + 1 L1)
- AC-2: `1 passed`
- round_trip: `1 passed`
- 3 critical gates: `8 passed`
- 8 PG-D L2: `8 skipped` (PG offline) or `8 passed` (PG online)
- yE detector + classifier + classifier integration: `5 + 9 + 1 = 15 passed`

**IF ANY GATE BREAKS → STOP. Report BLOCKED with full test output. Do NOT commit.**

Likely causes if a gate breaks:
- `DEFAULT_CLASSIFIER_RULES` ordering wrong (USV/USM/USD/VSF must precede their bases)
- Folder exclusion logic wrong (test_classify_em_demo_02_mini_smoke would fail)
- Hook edit accidentally broke the legacy path (AC-2 would fail) — re-check Edit didn't shift indentation

### Task A.6: Commit Group A

- [ ] **Step 1: Stage + commit**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git add modules/s3dgraphy/sync/yed_classifier.py \
        tests/sync/test_yed_classifier.py \
        tests/sync/test_yed_classifier_integration.py \
        modules/s3dgraphy/sync/graph_ingestor.py
git commit -m "$(cat <<'EOF'
feat(yE-B): yEd label-prefix classifier + hook wiring

Add modules/s3dgraphy/sync/yed_classifier.py with the label-prefix
classifier for yEd-raw graphml leaf nodes. Maps US*, USV*, USM*,
USD*, VSF*, SF*, D.*, C.*, and property keywords (material,
position, width, length, height, type, etc.) to one of 12
ClassificationKind enum values.

Implementation:
- DEFAULT_CLASSIFIER_RULES regex map is order-sensitive:
  specific prefixes (USV, USM, USD, VSF) precede generic ones
  (US, SF) to avoid mis-classification
- classify_leaves(graphml_path) parses via lxml.etree.iterparse
  with xml.etree fallback (same pattern as yed_detector.py)
- Folder nodes (yfiles.foldertype="group") are EXCLUDED from
  results -- yE-C yed_group_walker handles them
- Safe-default empty list on parse error / missing file
- Output preserves yEd document order so the yE-E dialog can
  present leaves in authoring sequence

Update modules/s3dgraphy/sync/graph_ingestor.py:169-191 to wire
the classifier into the yE-A detection hook. The yEd-raw branch
now calls classify_leaves() and emits a Counter summary in the
warning log:

  yEd-raw graphml detected at <path>. Classified N leaves:
    combiner: 3, document: 38, property: 23, special_find: 2,
    unknown: 2, us_real: 4, usv_virtual: 8, virtual_find: 2.
  Yed-aware import path not yet wired (yE-B classifier only).
  Falling through to legacy path.

Preserves the outer try/except Exception wrapper, lazy imports,
and no-op fall-through to the legacy path from yE-A. AC-2
byte-identical preserved.

Add tests/sync/test_yed_classifier.py with 9 L0 unit tests:
- test_classify_us_prefix
- test_classify_usv_prefix
- test_classify_usm_prefix_wins_over_us
- test_classify_special_find
- test_classify_virtual_find_wins_over_special
- test_classify_document_with_subdots
- test_classify_property_case_insensitive
- test_classify_unknown_falls_through
- test_classify_uses_yed_document_order

Each test builds a synthetic graphml in tmp_path; no new
persistent fixtures needed.

Add tests/sync/test_yed_classifier_integration.py with 1 L1
integration test (test_classify_em_demo_02_mini_smoke) that
runs classify_leaves on the yE-A reference fixture
em_demo_02_mini.graphml and verifies count breakdown:
2 US_REAL + 1 USV_VIRTUAL + 1 SPECIAL_FIND + 1 VIRTUAL_FIND +
1 PROPERTY = 6 leaves, with folder labels (VA01, AR01)
correctly excluded.

All regression gates preserved:
- AC-2 byte-identical (test_ai03_export_byte_identical)
- 3 critical SQLite gates (round_trip_with_paradata,
  round_trip_with_groups, graph_projector_paradata)
- 5 yE-A detector tests
- 8 PG-D L2 tests (skip cleanly when PG offline)

Test counts: 261 -> 271 passed, 33 skipped (PG offline).
EOF
)"
```

- [ ] **Step 2: Strict trailer check**

```bash
git log -1 --format=%B HEAD | grep -cE "^Co-Authored-By:"
```

MUST return `0`.

- [ ] **Step 3: Post-commit verification**

```bash
git log --oneline c0afd1fe..HEAD
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected:
- 1 commit since spec (`c0afd1fe`): Group A (the production commit)
- Full suite: `271 passed, 33 skipped`

## Self-review checklist before reporting back

- [ ] `yed_classifier.py` created with `ClassificationKind`, `DEFAULT_CLASSIFIER_RULES`, `ClassifiedNode`, `classify_leaves`
- [ ] DEFAULT_CLASSIFIER_RULES has 10 patterns in correct order (USV before US, USM before US, USD before US, VSF before SF)
- [ ] `classify_leaves()` signature is `(graphml_path: Path | str, rules=None)` — Path-only union, no Graph
- [ ] Folder nodes excluded (yfiles.foldertype="group" check)
- [ ] Safe-default empty list on parse error / missing file
- [ ] lxml import via try/except ImportError with xml.etree fallback
- [ ] `test_yed_classifier.py` created with 9 L0 tests, exact names matching plan
- [ ] `test_yed_classifier_integration.py` created with 1 L1 test, exact name matching plan
- [ ] `graph_ingestor.py` hook updated: classifier invoked, Counter summary in log, try/except preserved, lazy imports preserved, no-op fall-through preserved
- [ ] AC-2 byte-identical PASS
- [ ] 3 critical SQLite regression gates PASS
- [ ] 5 yE-A detector tests preserved (PASS)
- [ ] 8 PG-D L2 tests SKIP cleanly (or PASS if PG online)
- [ ] Full suite: 271 passed, 33 skipped (PG offline)
- [ ] Strict trailer check returns 0
- [ ] No leftover changes after commit

## Report back format

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- Commit SHA
- Test counts (full suite + AC-2 + round_trip + 3 SQLite gates + 8 PG-D L2 + detector + classifier + classifier_integration)
- Strict trailer check result (must be 0)
- Files changed (should be 4: yed_classifier.py + test_yed_classifier.py + test_yed_classifier_integration.py + graph_ingestor.py)
- Any concerns

If you find yourself wanting to refactor anything beyond the plan (e.g., add caching, configurable rules persistence, additional log levels), STOP and report DONE_WITH_CONCERNS describing what you wanted to do.

---

## Group B — Docs + version 5.7.6-alpha

### Task B.1: Bump `metadata.txt`

**Files:**
- Modify: `metadata.txt`

- [ ] **Step 1: Bump version**

Use the Edit tool to change the `version=` line:
```
version=5.7.5-alpha
```
to:
```
version=5.7.6-alpha
```

Verify:
```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
grep "^version=" metadata.txt
```
Expected: `version=5.7.6-alpha`.

### Task B.2: Insert yE-B dev-log section

**Files:**
- Modify: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

- [ ] **Step 1: Prepend yE-B section**

Use the Edit tool. Find this EXACT text (the start of the yE-A section):

```
---

## yE-A Foundation — yEd-import detection hook (5.7.5-alpha)
```

Replace with EXACTLY (preserving the yE-A heading at the end):

```
---

## yE-B Classifier — yEd label-prefix classifier (5.7.6-alpha)

**Tag:** `yed-import-classifier-5.7.6-alpha`
**Date:** 2026-05-12
**Spec:** `docs/superpowers/specs/2026-05-12-yed-import-classifier-design.md`
**Plan:** `docs/superpowers/plans/2026-05-12-yed-import-classifier.md`
**Predecessor:** `yed-import-foundation-5.7.5-alpha` (`eb4fba81`)

### What shipped

- NEW `modules/s3dgraphy/sync/yed_classifier.py` with
  `classify_leaves()` function + `ClassificationKind` enum
  (12 values) + `DEFAULT_CLASSIFIER_RULES` regex map
  (10 order-sensitive patterns) + `ClassifiedNode` dataclass
- NEW `tests/sync/test_yed_classifier.py` with 9 L0 unit tests
  (synthetic graphml strings in tmp_path)
- NEW `tests/sync/test_yed_classifier_integration.py` with 1 L1
  integration test on the yE-A reference fixture
  `em_demo_02_mini.graphml`
- MODIFY `modules/s3dgraphy/sync/graph_ingestor.py:169-191`:
  the yE-A bare warning is replaced with a classifier
  invocation + Counter summary log. The yEd-raw branch now
  emits a richer log line:
  `yEd-raw graphml detected at <path>. Classified N leaves:
  combiner: 3, document: 38, property: 23, ... Falling through
  to legacy path.`
  Preserves outer try/except, lazy imports, no-op fall-through.

### Inheritance from parent spec

This milestone inherits the classifier design from parent spec
§5 (`docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md`)
and specializes it for the MVP:
- input is Path-only (NOT `Graph | Path | str` union as parent
  spec said) — consistent with yE-A `detect_flavor` pattern
- folder nodes (yfiles.foldertype="group") are EXCLUDED from
  classification — yE-C `yed_group_walker` handles folders
- DEFAULT_CLASSIFIER_RULES is the only ruleset shipped; user
  override via dialog deferred to yE-E

### Tests

- 9 new L0 classifier tests (always run, no Qt, no PG dep)
- 1 new L1 integration test (on em_demo_02_mini.graphml)
- 5 yE-A detector tests preserved
- 256 SQLite baseline + AC-2 + 3 critical SQLite regression
  gates + 8 PG-D L2 tests all preserved
- Total: 261 -> 271 passed, 33 skipped (PG offline) or
  269 -> 279 passed, 12 skipped (PG online + psycopg2)

### Next: yE-C (Parsers — `yed-import-parsers-5.7.7-alpha`)

Will ship `yed_table_parser.py` (yEd TableNode rows ->
PeriodCandidate) + `yed_group_walker.py` (folder hierarchy ->
FolderCandidate). The branch hook will start orchestrating
detection + classification + period parsing + group walking,
but still no DB writes (those land in yE-D).

---

## yE-A Foundation — yEd-import detection hook (5.7.5-alpha)
```

### Task B.3: Prepend bilingual CHANGELOG entry

**Files:**
- Modify: `dev_logs/CHANGELOG.md`

- [ ] **Step 1: Prepend entry**

Use the Edit tool. Find this EXACT text (current top of changelog):

```
## [5.7.5-alpha] - 2026-05-12
```

Replace with EXACTLY (preserving the original heading at the end):

```
## [5.7.6-alpha] - 2026-05-12

### Italiano

**yE-B Classifier — secondo milestone del feature yEd-aware graphml import.**

Aggiunge il classifier label-prefix per i leaf node dei graphml yEd-raw + wiring nel branch hook esistente (introdotto in yE-A). All'import di un file yEd-raw, il log ora mostra una sintesi della classificazione:

```
yEd-raw graphml detected at <path>. Classified N leaves:
  combiner: 3, document: 38, property: 23, special_find: 2,
  unknown: 2, us_real: 4, usv_virtual: 8, virtual_find: 2.
Falling through to legacy path.
```

- **NEW `modules/s3dgraphy/sync/yed_classifier.py`**: helper `classify_leaves(graphml_path)` con enum `ClassificationKind` (12 valori: US_REAL, US_MASONRY, US_DOCUMENTARY, USV_VIRTUAL, USV_FORMAL, SPECIAL_FIND, VIRTUAL_FIND, DOCUMENT, COMBINER, PROPERTY, UNKNOWN, SKIP), regex map `DEFAULT_CLASSIFIER_RULES` (10 pattern order-sensitive — USV* prima di US*, USM* prima di US*, USD* prima di US*, VSF* prima di SF*), e dataclass `ClassifiedNode` con `auto_kind` + `user_kind` (l'utente potrà override per-nodo nel dialog yE-E).
- **Esclusione folder**: i nodi con `yfiles.foldertype="group"` NON vengono classificati — quelli sono territorio di yE-C `yed_group_walker`.
- **Sicurezza**: parse error / file mancante → lista vuota (safe default, fall-through al path legacy preservato).
- **MODIFY `modules/s3dgraphy/sync/graph_ingestor.py:169-191`**: il bare warning di yE-A viene sostituito con invocazione di `classify_leaves()` + summary `Counter` nel log. Outer `try/except Exception: pass` di yE-A preservato (classifier errors non possono rompere il path legacy). Import lazy preservati.
- **NEW 9 test L0** in `tests/sync/test_yed_classifier.py`: ordering prefix, case insensitivity, unknown fallback, document order. Usano graphml sintetici in tmp_path — nessuna nuova fixture persistente.
- **NEW 1 test L1** in `tests/sync/test_yed_classifier_integration.py`: integration su `em_demo_02_mini.graphml` (fixture yE-A) — verifica count breakdown e esclusione folder.

**Eredita dal parent spec** (`docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md` §5) ma specializza:
- Input è Path-only (NON union `Graph | Path | str`) — consistenza con `yed_detector.detect_flavor`
- DEFAULT_CLASSIFIER_RULES è l'unico ruleset shippato; override utente via dialog deferito a yE-E

**Garanzie regressione (tutte verdi post-yE-B):**
- AC-2 byte-identical (`test_ai03_export_byte_identical`)
- 3 critical SQLite gates
- 5 yE-A detector tests
- 8 PG-D L2 (skip puliti offline)

Test count: 261 → 271 passed, 33 skipped (PG offline) o 269 → 279 passed, 12 skipped (PG online + psycopg2).

### English

**yE-B Classifier — second milestone of the yEd-aware graphml import feature.**

Adds the label-prefix classifier for yEd-raw graphml leaf nodes + wiring into the existing branch hook (introduced in yE-A). On import of a yEd-raw file, the log now shows a classification summary:

```
yEd-raw graphml detected at <path>. Classified N leaves:
  combiner: 3, document: 38, property: 23, special_find: 2,
  unknown: 2, us_real: 4, usv_virtual: 8, virtual_find: 2.
Falling through to legacy path.
```

- **NEW `modules/s3dgraphy/sync/yed_classifier.py`**: helper `classify_leaves(graphml_path)` with `ClassificationKind` enum (12 values: US_REAL, US_MASONRY, US_DOCUMENTARY, USV_VIRTUAL, USV_FORMAL, SPECIAL_FIND, VIRTUAL_FIND, DOCUMENT, COMBINER, PROPERTY, UNKNOWN, SKIP), `DEFAULT_CLASSIFIER_RULES` regex map (10 order-sensitive patterns — USV* before US*, USM* before US*, USD* before US*, VSF* before SF*), and `ClassifiedNode` dataclass with `auto_kind` + `user_kind` (user can override per-node in the yE-E dialog).
- **Folder exclusion**: nodes with `yfiles.foldertype="group"` are NOT classified — those are yE-C `yed_group_walker` territory.
- **Safety**: parse error / missing file → empty list (safe default, legacy path fall-through preserved).
- **MODIFY `modules/s3dgraphy/sync/graph_ingestor.py:169-191`**: the yE-A bare warning is replaced with `classify_leaves()` invocation + `Counter` summary log. The yE-A outer `try/except Exception: pass` is preserved (classifier errors cannot break the legacy path). Lazy imports preserved.
- **NEW 9 L0 tests** in `tests/sync/test_yed_classifier.py`: prefix ordering, case insensitivity, unknown fallback, document order. Uses synthetic graphml strings in tmp_path — no new persistent fixtures.
- **NEW 1 L1 test** in `tests/sync/test_yed_classifier_integration.py`: integration on `em_demo_02_mini.graphml` (yE-A fixture) — verifies count breakdown and folder exclusion.

**Inherits parent spec** (`docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md` §5) but specializes:
- Input is Path-only (NOT `Graph | Path | str` union) — consistency with `yed_detector.detect_flavor`
- DEFAULT_CLASSIFIER_RULES is the only ruleset shipped; user override via dialog deferred to yE-E

**Regression guarantees (all green post-yE-B):**
- AC-2 byte-identical (`test_ai03_export_byte_identical`)
- 3 critical SQLite gates
- 5 yE-A detector tests
- 8 PG-D L2 (skip cleanly offline)

Test count: 261 → 271 passed, 33 skipped (PG offline) or 269 → 279 passed, 12 skipped (PG online + psycopg2).

---

## [5.7.5-alpha] - 2026-05-12
```

### Task B.4: Commit + final verification

- [ ] **Step 1: Pre-commit verification**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git log --oneline c0afd1fe..HEAD
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
grep "^version=" metadata.txt
```

Expected:
- 1 commit since spec (`c0afd1fe`): Group A (the production commit)
- Test suite: `271 passed, 33 skipped`
- Version: `5.7.6-alpha`

- [ ] **Step 2: Commit docs + version**

```bash
git add metadata.txt \
        docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md \
        dev_logs/CHANGELOG.md
git commit -m "$(cat <<'EOF'
release(yE-B): docs + version 5.7.6-alpha

yE-B Classifier milestone documentation: bilingual CHANGELOG entry,
dev-log yE-B section, version bump 5.7.5-alpha -> 5.7.6-alpha.

This is the second milestone of the 6-milestone yEd-aware graphml
import rollout. Ships the label-prefix classifier + hook wiring
that emits a Counter summary on yEd-raw imports.

The classifier inherits design from parent spec §5 and specializes
for MVP: Path-only input, folder nodes excluded (yE-C territory),
DEFAULT_CLASSIFIER_RULES is the only ruleset (user override
deferred to yE-E dialog).

Test count: 261 -> 271 passed, 33 skipped (PG offline) or
269 -> 279 passed, 12 skipped (PG online + psycopg2).
AC-2 byte-identical baseline preserved.
3 critical SQLite gates preserved.
5 yE-A detector tests preserved.
8 PG-D L2 tests preserved.

Spec: docs/superpowers/specs/2026-05-12-yed-import-classifier-design.md (c0afd1fe)
Plan: docs/superpowers/plans/2026-05-12-yed-import-classifier.md
Predecessor: yed-import-foundation-5.7.5-alpha (eb4fba81)
EOF
)"
```

- [ ] **Step 3: Strict trailer check**

```bash
git log -1 --format=%B HEAD | grep -cE "^Co-Authored-By:"
```

MUST return `0`.

- [ ] **Step 4: Post-commit verification**

```bash
git log --oneline c0afd1fe..HEAD
git log c0afd1fe..HEAD --format=%B | grep -cE "^Co-Authored-By:"
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
grep "^version=" metadata.txt
```

Expected:
- 2 commits since spec (`c0afd1fe`): A, B
- Trailer count: `0`
- `271 passed, 33 skipped`
- Version: `5.7.6-alpha`

---

## Group C — Annotated tag + USER APPROVAL GATE for push

### Task C.1: Pre-flight branch check

- [ ] **Step 1: Confirm branch**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git rev-parse --abbrev-ref HEAD
```

Expected: `Stratigraph_00001`. **STOP and BLOCK** if anything else.

### Task C.2: Create annotated tag (LOCAL ONLY — do not push yet)

- [ ] **Step 1: Create tag**

```bash
git tag -a yed-import-classifier-5.7.6-alpha -m "$(cat <<'EOF'
yE-B Classifier - yEd label-prefix classifier + hook wiring

Second milestone of the 6-milestone yEd-aware graphml import
rollout. Ships the label-prefix classifier and wires it into
the yE-A detection hook. No user-visible behavior change beyond
a richer log line on yEd-raw imports.

Cumulative deliverables (Groups A-B, 2 commits):

- NEW modules/s3dgraphy/sync/yed_classifier.py with
  classify_leaves(graphml_path) function + ClassificationKind
  enum (12 values) + DEFAULT_CLASSIFIER_RULES regex map
  (10 order-sensitive patterns: USV/USM/USD/VSF precede their
  bases) + ClassifiedNode dataclass.
- NEW tests/sync/test_yed_classifier.py with 9 L0 unit tests
  using synthetic graphml strings in tmp_path.
- NEW tests/sync/test_yed_classifier_integration.py with 1 L1
  test on the yE-A reference fixture em_demo_02_mini.graphml.
- MODIFY modules/s3dgraphy/sync/graph_ingestor.py:169-191
  to invoke classify_leaves() in the yEd-raw branch + emit a
  Counter summary in the warning log. Outer try/except wrapper
  and lazy imports preserved from yE-A; no-op fall-through to
  legacy path preserved (full pipeline wiring lands in yE-C+).
- Version bump 5.7.5-alpha -> 5.7.6-alpha + bilingual CHANGELOG
  entry + dev-log yE-B section.

Inherits classifier design from parent spec §5
(2026-05-12-yed-aware-graphml-import-design.md) and specializes
for MVP: Path-only input (no Graph union), folder nodes excluded
(yE-C territory), DEFAULT_CLASSIFIER_RULES is the only ruleset
shipped (user override via dialog deferred to yE-E).

Test counts: 261 -> 271 passed, 33 skipped (PG offline) or
269 -> 279 passed, 12 skipped (PG online + psycopg2).
AC-2 byte-identical preserved.
All 3 critical SQLite regression gates preserved.
All 5 yE-A detector tests preserved.
All 8 PG-D L2 tests preserved.

Next milestone: yE-C Parsers (yed-import-parsers-5.7.7-alpha)
- ships yed_table_parser.py (TableNode rows -> PeriodCandidate)
  and yed_group_walker.py (folder hierarchy -> FolderCandidate).
  Branch hook orchestrates detection + classification + parsing.

Spec: docs/superpowers/specs/2026-05-12-yed-import-classifier-design.md
Plan: docs/superpowers/plans/2026-05-12-yed-import-classifier.md
Predecessor: yed-import-foundation-5.7.5-alpha (eb4fba81)
EOF
)"
```

### Task C.3: Verify the tag (LOCAL)

- [ ] **Step 1: Verify**

```bash
echo "=== Tag created locally ==="
git tag -n5 yed-import-classifier-5.7.6-alpha | head -10
echo "=== Tag points to HEAD ==="
git rev-parse yed-import-classifier-5.7.6-alpha^{commit}
git rev-parse HEAD
echo "=== Tag is annotated ==="
git cat-file -t yed-import-classifier-5.7.6-alpha
echo "=== Strict trailer check on tag message ==="
git tag -l --format='%(contents)' yed-import-classifier-5.7.6-alpha | grep -cE "^Co-Authored-By:"
```

The final grep MUST return `0`. The tag must be type `tag` (annotated), not `commit`. The tag commit SHA MUST match HEAD.

### Task C.4: USER APPROVAL GATE — present manual test plan

- [ ] **Step 1: STOP and present test plan to user**

This is a controller gate, NOT a subagent decision. Before pushing the tag + branch + spec commit to origin, present the following manual test plan and wait for `approvato`:

```
yE-B Classifier is wired into the detection hook but is still no-op
fall-through. The manual test surface is small but worth running:

1. Reload pyarchinit / restart QGIS to pick up the new
   yed_classifier.py and modified graph_ingestor.py.

2. From QGIS Python Console (Ctrl+Alt+P):
     from modules.s3dgraphy.sync.yed_classifier import (
         classify_leaves, ClassificationKind
     )
     classified = classify_leaves("/Users/enzo/Downloads/EM_demo_02.graphml")
     from collections import Counter
     dict(Counter(n.auto_kind.value for n in classified))
     
     # Expected output (matches the bug investigation from earlier):
     # {'document': 38, 'property': 23, 'usv_virtual': 8,
     #  'us_real': 4, 'combiner': 3, 'special_find': 2,
     #  'virtual_find': 2, 'unknown': 2}
     # Total leaves: 82

3. (Optional) Try the existing "Import GraphML" menu with
   /Users/enzo/Downloads/EM_demo_02.graphml -- expect to see
   the new enriched WARNING in the QGIS Log Messages panel:
     "yEd-raw graphml detected at <path>. Classified 82 leaves:
      combiner: 3, document: 38, property: 23, special_find: 2,
      unknown: 2, us_real: 4, usv_virtual: 8, virtual_find: 2.
      Yed-aware import path not yet wired (yE-B classifier only).
      Falling through to legacy path."
   The actual ingest will still be the broken behavior from before
   (17 us_table rows etc.) -- yE-C/D will fix that.

4. (Optional) Try the same menu with a pyarchinit-projected
   graphml -- should behave IDENTICALLY to before (no warning,
   no classifier invocation, no count log).

If all 4 steps look right, reply 'approvato' to push.
If anything is wrong, describe what you saw and I'll fix.
```

Wait for the user's response. **DO NOT push** until the user replies `approvato` / `go` / `procedi`.

### Task C.5: Push tag + branch (after user approval)

- [ ] **Step 1: Push spec commit + Group A + Group B + tag**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git push origin Stratigraph_00001 2>&1 | tail -3
git push origin yed-import-classifier-5.7.6-alpha 2>&1 | tail -3
```

### Task C.6: Verify on origin

- [ ] **Step 1: Confirm push**

```bash
git ls-remote --tags origin | grep "yed-import-classifier-5.7.6-alpha"
git ls-remote --heads origin Stratigraph_00001
```

Expected: tag listed (with `^{}` dereferenced commit line), branch tip equals local HEAD.

---

## Group D — Memory snapshot (controller, no subagent)

After Group C ships, the controller (NOT a subagent) updates memory.

- [ ] **Step 1: Update `~/.claude/projects/-Users-enzo-Library-Application-Support-QGIS-QGIS3-profiles-default-python-plugins-pyarchinit/memory/project_yed_import_progress.md`**

- Mark yE-A SHIPPED (already done) — keep
- Mark **yE-B SHIPPED 2026-05-12** with tag/commit/SHAs filled in from `git rev-parse` after push
- yE-C, yE-D, yE-E, yE-Closure remain PENDING with their target tags
- Append "Lessons from yE-B execution" section if any new lessons emerged

- [ ] **Step 2: Update `~/.claude/projects/-Users-enzo-Library-Application-Support-QGIS-QGIS3-profiles-default-python-plugins-pyarchinit/memory/MEMORY.md`**

Replace the yE-A SHIPPED index line with an updated entry reflecting yE-B SHIPPED. Something like:

```
- [yEd-import yE-B Classifier SHIPPED 2026-05-12](project_yed_import_progress.md) — Tags `yed-import-foundation-5.7.5-alpha` (yE-A, eb4fba81) + `yed-import-classifier-5.7.6-alpha` (yE-B). 4/6 milestones pending (yE-C Parsers next). 261 → 271 passed, 33 skipped. AC-2 preserved. yE-B adds label-prefix classifier (yed_classifier.py with 12-value enum + 10 order-sensitive regex rules) + hook wiring with Counter summary log on yEd-raw imports. Reference fixture em_demo_02_mini.graphml reused for L1 integration test.
```

---

## Self-Review

This plan covers every yE-B spec requirement:

| Spec section | Plan task |
|---|---|
| §3 Architecture overview | File structure section + Group A creates the listed new files; Group B modifies metadata + docs |
| §4 Classifier module specification | Task A.1 (full code provided) |
| §5 Branch hook update | Task A.4 (exact old/new strings provided) |
| §6 Test strategy (9 L0 + 1 L1) | Task A.2 (9 L0 tests) + Task A.3 (1 L1 test) |
| §7 Decomposition (5 Groups) | Groups 0/A/B/C/D structure |
| §8 Acceptance criteria | Self-review checklist + Task A.5 regression gates |
| §9 Out of scope | "Explicitly NOT touched" + Group A scope discipline |

**Placeholder scan:** zero `TBD/TODO/FIXME` in the plan body. The "fill in commit SHA after push" in Group D is intentional — those values are post-execution.

**Type consistency:**
- `ClassificationKind` enum — used consistently in module, 9 L0 tests, 1 L1 test, hook update
- `classify_leaves(graphml_path, rules=None)` — same signature in module + tests + hook
- `DEFAULT_CLASSIFIER_RULES` — referenced consistently
- `ClassifiedNode` dataclass — used consistently
- Fixture path `tests/sync/fixtures/em_demo_02_mini.graphml` — consistent
- Hook line range "169-191" — consistent across plan + spec

**No placeholders:** every step has runnable code, exact commands, or specific file edits.

**Scope discipline:** Plan focused on yE-B only. No premature parsers (yE-C), no dialog (yE-E), no pipeline orchestrator (yE-D).

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-12-yed-import-classifier.md`. Two execution options:

**1. Subagent-Driven (recommended)** — controller dispatches fresh subagent per task with two-stage review (spec compliance → code quality); recommended batching:
- Group 0 (controller-only, pure git)
- Group A (1 subagent — production code + tests + hook)
- Group B (1 subagent — docs + version)
- Group C (1 subagent for tag creation; STOP at Task C.4 for user approval; then 1 more action for push)
- Group D (controller writes memory snapshot)

**2. Inline Execution** — execute tasks in this session via `executing-plans` with checkpoints after each Group.

Which approach?
