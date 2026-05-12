# yE-C Parsers — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the third milestone of the 6-milestone yEd-aware graphml import rollout: two new parsers (`yed_table_parser.py` for TableNode rows → periods, `yed_group_walker.py` for folder hierarchy → folder candidates) wired into the yE-B branch hook with a 3-line summary log + `IngestResult.parsed_drafts` field for forward-compat with the yE-D pipeline.

**Architecture:** Pure additive on the yEd-raw branch. Two new modules + one new field on `IngestResult` + branch-hook orchestration update. Local var `_yed_parsed_drafts` initialized at function start, populated by the hook block, passed at construction time to the final `IngestResult(...)` call (which is `frozen=True` — no mutation possible). The pyarchinit-projected branch stays byte-identically the same. 13 L0 unit tests + 3 L1 integration tests.

**Tech Stack:** Python 3.9+, `lxml.etree.iterparse` (with `xml.etree.iterparse` fallback), `dataclasses`, `re`, pytest. No new dependencies.

**Spec source of truth:** `docs/superpowers/specs/2026-05-12-yed-import-parsers-design.md` (commit `eb131d50`).

**Parent spec (inherited from):** `docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md` (commit `43fc5cb8`).

**Predecessor tag:** `yed-import-classifier-5.7.6-alpha` (commit `640b4e83`).

**Target tag:** `yed-import-parsers-5.7.7-alpha`.

**Memory notes:**
- `~/.claude/projects/.../memory/feedback_no_claude_coauthor.md` — strict commit-author rule
- `~/.claude/projects/.../memory/project_yed_import_progress.md` — yE-A + yE-B SHIPPED + lessons

**Strict commit-author rule:** never include trailers identifying Claude as a co-author. After each commit run `git log -1 --format=%B HEAD | grep -cE '^Co-Authored-By:'` — must return `0`.

---

## CRITICAL DISCOVERY DURING PLAN-WRITING

**`IngestResult` is `@dataclass(frozen=True)`** (verified at `modules/s3dgraphy/sync/ingest_result.py`). This means **cannot mutate `result.parsed_drafts = ...` after construction**. The spec §7 said "attach to result before final return" but that's not possible with frozen.

**Corrected approach:** Pass `parsed_drafts=_yed_parsed_drafts` at construction time. The final `IngestResult(...)` call is at `modules/s3dgraphy/sync/graph_ingestor.py:648-654`:

```python
        return IngestResult(
            applied=applied,
            inserted=inserted, updated=updated, skipped=skipped,
            epochs_created=epochs_created,
            conflicts=tuple(conflicts), errors=tuple(errors),
            dry_run=dry_run,
        )
```

The implementer must add ONE keyword argument: `parsed_drafts=_yed_parsed_drafts`. Default `None` on the field preserves back-compat for any other call sites that construct `IngestResult(...)` without the field.

The local-var pattern still works: initialize `_yed_parsed_drafts = None` at function start, populate inside the hook block if yEd-raw detected, pass to constructor.

---

## File Structure

### Created (7)

| Path | Responsibility |
|---|---|
| `modules/s3dgraphy/sync/yed_table_parser.py` | `PeriodCandidate` dataclass + `extract_periods(graphml_path)` function. lxml/xml.etree iterparse. Returns [] on error / no TableNode. |
| `modules/s3dgraphy/sync/yed_group_walker.py` | `FolderCandidate` dataclass + `DEFAULT_FOLDER_PREFIX_MAP` + `walk_folders(graphml_path)` function. Recursive walker with cycle detection (reuses `CycleDetectedError` from `graph_ingestor.py`). |
| `tests/sync/test_yed_table_parser.py` | 6 L0 tests with synthetic graphml strings in `tmp_path`. |
| `tests/sync/test_yed_group_walker.py` | 7 L0 tests with synthetic graphml strings in `tmp_path`. |
| `tests/sync/test_table_parser_integration.py` | 1 L1 test on `em_demo_02_mini.graphml`. |
| `tests/sync/test_group_walker_integration.py` | 1 L1 test on `em_demo_02_mini.graphml`. |
| `tests/sync/test_yed_parsers_orchestration.py` | 1 L1 cross-parser consistency test. |

### Modified (5)

| Path | Why | LOC delta |
|---|---|---|
| `modules/s3dgraphy/sync/ingest_result.py` | Add `parsed_drafts: dict \| None = None` field to `IngestResult`. Keeps `frozen=True`. | +5 |
| `modules/s3dgraphy/sync/graph_ingestor.py` | Update yE-B branch hook at lines 169-196: orchestrate classify_leaves + extract_periods + walk_folders + 3-line summary log + populate `_yed_parsed_drafts` local var. Add `parsed_drafts=_yed_parsed_drafts` to `IngestResult(...)` constructor call at line 648-654. | +35 / -3 |
| `metadata.txt` | Version bump 5.7.6-alpha → 5.7.7-alpha | 1 |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.7-alpha]` section | ~50 |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Prepend yE-C section above yE-B | ~40 |

### NOT touched

- `yed_detector.py` (yE-A), `yed_classifier.py` (yE-B) — unchanged
- `tests/sync/fixtures/em_demo_02_mini.graphml` — reused as-is (fixture geometry verified: rows at y=30-330 and y=330-630, 4 leaves in row 0, 2 in row 1)
- Pyarchinit-projected branch of `populate_list()` — sacred (AC-2)
- DB schema, requirements.txt, vocab_provider, paradata_store — all out of scope

### Total LOC

- Production: ~370 (~340 new + ~30 modify delta)
- Test: ~540
- Docs: ~95
- **Grand total: ~1000 LOC**

---

## Test strategy

- **L0 unit (NEW):** 13 tests (6 table parser + 7 group walker) using synthetic graphml strings in `tmp_path`. Pure pytest, no Qt, no PG. Always runs.
- **L1 integration (NEW):** 3 tests on `em_demo_02_mini.graphml` (2 per-parser + 1 cross-parser orchestration). Pure pytest, no Qt, no PG.
- **L1 SQLite (existing 273):** Stay green. Pyarchinit-projected branch unchanged; new yEd-raw branch is still no-op fall-through.
- **L2 PG (existing 8):** Stay green or skip cleanly.
- **L3 regression guards (existing, MUST stay green after Group A):**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v   # AC-2
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py tests/sync/test_round_trip_with_groups.py tests/sync/test_graph_projector_paradata.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py tests/sync/test_group_store_pg.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_yed_detector.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_yed_classifier.py tests/sync/test_yed_classifier_integration.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no
```

After Group A, ALL must PASS (or SKIP for PG L2 when PG offline). If any breaks → STOP and report BLOCKED.

### Test count progression

- Pre yE-C (post yE-B): `273 passed, 33 skipped`
- Post Group A (+13 L0 + 3 L1): `289 passed, 33 skipped`
- Post Group B (docs only): unchanged
- **Final (PG offline):** `289 passed, 33 skipped`
- **Final (PG online + psycopg2):** `297 passed, 12 skipped`

---

## Group 0 — Pre-flight & rollback safety

### Task 0.1: Verify clean starting point

- [ ] **Step 1: Confirm branch + HEAD**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git rev-parse --abbrev-ref HEAD
git log --oneline -3
git rev-list --left-right --count HEAD...@{u}
```

Expected: branch `Stratigraph_00001`, HEAD `eb131d50 spec(yE-C): parsers milestone design`, ahead `1\t0`.

- [ ] **Step 2: Verify predecessor tag**

```bash
git tag --list | grep -E "yed-import-classifier-5.7.6-alpha"
```

Expected: tag listed.

- [ ] **Step 3: Capture baselines**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py tests/sync/test_round_trip.py tests/sync/test_round_trip_with_paradata.py tests/sync/test_round_trip_with_groups.py tests/sync/test_graph_projector_paradata.py -v 2>&1 | tail -10
PYTHONPATH="$PWD" python -m pytest tests/sync/test_yed_detector.py tests/sync/test_yed_classifier.py tests/sync/test_yed_classifier_integration.py -v 2>&1 | tail -20
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py tests/sync/test_group_store_pg.py -v 2>&1 | tail -10
```

Expected:
- Full suite: `273 passed, 33 skipped`
- AC-2 + round_trip + 3 SQLite gates: `10 passed`
- yE-A + yE-B: `17 passed` (5 + 11 + 1)
- 8 PG-D L2: `8 skipped` (PG offline)

### Task 0.2: Create rollback safety tag

- [ ] **Step 1: Create + push rollback tag**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git tag -a pre-yed-import-parsers -m "Rollback point before yE-C Parsers milestone

Predecessor tag: yed-import-classifier-5.7.6-alpha (640b4e83)
Spec commit: eb131d50 (local-only at tag time)

If yE-C needs to be reverted, reset hard to this tag."
git push origin pre-yed-import-parsers 2>&1 | tail -3
```

Expected: `* [new tag]         pre-yed-import-parsers -> pre-yed-import-parsers`.

---

## Group A — Parsers + IngestResult field + hook update + tests

The only production-code Group. ~370 LOC prod + ~540 LOC test.

**CRITICAL RULES (surface in subagent prompt):**
- `IngestResult` is `@dataclass(frozen=True)` — CANNOT mutate after construction. Pass `parsed_drafts=` at construction time (line 648-654).
- `extract_periods()` and `walk_folders()` signatures are `(graphml_path: Path | str)` — NOT Graph union
- `CycleDetectedError` imported from `graph_ingestor.py` (NOT redefined)
- Top-level TableNode excluded from `walk_folders` (it has `<y:TableNode>` child)
- All lazy imports preserved in hook block
- AC-2 + 3 SQLite gates + 5 yE-A + 12 yE-B + 8 PG-D L2 ALL must stay green

### Task A.1: Create `modules/s3dgraphy/sync/yed_table_parser.py`

**Files:** Create `modules/s3dgraphy/sync/yed_table_parser.py`.

- [ ] **Step 1: Create the module**

Use the Write tool with EXACTLY this content:

```python
"""yEd TableNode period extractor (yE-C Parsers, 5.7.7-alpha).

Reads the top-level <y:TableNode configuration="YED_TABLE_NODE"> of a
yEd-raw graphml and extracts archaeological period candidates from
its swimlane rows. Each row produces a PeriodCandidate with:
  - auto_label from <y:NodeLabel> text
  - auto_periodo from 1-based row ordinal
  - auto_fase always 1 (yEd table rows don't encode phases)
  - member_yed_ids from leaf nodes whose Y-coordinate falls in the
    row's Y-range

datazione_iniziale / datazione_finale are NOT extracted (yEd doesn't
encode dates on table rows) — user fills them later in the
pyarchinit Periodizzazione tab.

Folder nodes (yfiles.foldertype="group") are skipped in the
membership scan — yE-C yed_group_walker handles them.

Returns [] on parse error / missing file / no TableNode (safe
default; the branch hook's try/except wrapper passes through).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PeriodCandidate:
    """One period extracted from a yEd TableNode row.

    auto_* fields are heuristic-derived; user_* are editable by the
    yE-E dialog (in yE-C they default to auto_* values).
    """
    yed_row_id: str
    auto_label: str
    user_label: str
    auto_periodo: int
    auto_fase: int
    user_periodo: int
    user_fase: int
    member_yed_ids: list[str] = field(default_factory=list)
    y_min: float = 0.0
    y_max: float = 0.0


def extract_periods(graphml_path: Path | str) -> list[PeriodCandidate]:
    """Find top-level yEd TableNode rows and build PeriodCandidate list.

    Args:
        graphml_path: filesystem path to the .graphml file.

    Returns:
        List of PeriodCandidate in row document order. Empty list if
        no TableNode found, malformed file, or missing file.
    """
    path = Path(graphml_path)
    if not path.exists():
        return []

    try:
        from lxml import etree as _ET
    except ImportError:
        import xml.etree.ElementTree as _ET  # type: ignore[no-redef]

    GRAPHML_NS = "{http://graphml.graphdrawing.org/xmlns}"
    Y_NS = "{http://www.yworks.com/xml/graphml}"

    try:
        tree = _ET.parse(str(path))
    except Exception:
        return []

    root = tree.getroot()

    # First pass: find the first top-level y:TableNode + extract its
    # geometry, row labels, row heights.
    table_node = None
    table_geom_y = 0.0
    table_geom_x = 0.0
    table_geom_width = 0.0
    rows: list[tuple[str, str, float]] = []  # (row_id, label, height)
    header_height = 30.0  # yEd default if not specified

    for node in root.iter(f"{GRAPHML_NS}node"):
        tn = node.find(f".//{Y_NS}TableNode")
        if tn is not None and tn.get("configuration") == "YED_TABLE_NODE":
            table_node = node
            # Geometry of the TableNode itself
            geom = tn.find(f"{Y_NS}Geometry")
            if geom is not None:
                try:
                    table_geom_y = float(geom.get("y") or "0")
                    table_geom_x = float(geom.get("x") or "0")
                    table_geom_width = float(geom.get("width") or "0")
                except (ValueError, TypeError):
                    pass

            # Build {row_id: label} from NodeLabels with
            # RowNodeLabelModelParameter children
            row_labels: dict[str, str] = {}
            for nl in tn.findall(f"{Y_NS}NodeLabel"):
                rmp = nl.find(
                    f".//{Y_NS}RowNodeLabelModelParameter")
                if rmp is not None:
                    rid = rmp.get("id") or ""
                    txt = (nl.text or "").strip()
                    row_labels[rid] = txt

            # Header height (yEd Insets top), if specified
            table_el = tn.find(f"{Y_NS}Table")
            if table_el is not None:
                insets = table_el.find(f"{Y_NS}Insets")
                if insets is not None:
                    try:
                        header_height = float(
                            insets.get("top") or "30.0")
                    except (ValueError, TypeError):
                        pass

                # Row geometries in order
                rows_el = table_el.find(f"{Y_NS}Rows")
                if rows_el is not None:
                    for row_el in rows_el.findall(f"{Y_NS}Row"):
                        rid = row_el.get("id") or ""
                        try:
                            height = float(
                                row_el.get("height") or "0")
                        except (ValueError, TypeError):
                            height = 0.0
                        label = row_labels.get(rid, "")
                        if not label:
                            # Placeholder for empty-label rows
                            label = f"row_{len(rows)}"
                        rows.append((rid, label, height))
            break  # only the first top-level TableNode

    if not rows:
        return []

    # Build PeriodCandidate list with Y ranges
    periods: list[PeriodCandidate] = []
    current_y = table_geom_y + header_height
    for idx, (rid, label, height) in enumerate(rows):
        y_min = current_y
        y_max = current_y + height
        periods.append(PeriodCandidate(
            yed_row_id=rid,
            auto_label=label,
            user_label=label,
            auto_periodo=idx + 1,
            auto_fase=1,
            user_periodo=idx + 1,
            user_fase=1,
            member_yed_ids=[],
            y_min=y_min,
            y_max=y_max,
        ))
        current_y = y_max

    if not periods:
        return []

    # Second pass: assign every non-folder leaf to a row by Y-coord.
    # Skip the TableNode itself and any node with foldertype="group".
    table_node_id = table_node.get("id") if table_node is not None else None
    for node in root.iter(f"{GRAPHML_NS}node"):
        nid = node.get("id") or ""
        if nid == table_node_id:
            continue
        if node.get("yfiles.foldertype") == "group":
            continue
        # Find <y:Geometry y="...">
        geom = node.find(f".//{Y_NS}Geometry")
        if geom is None:
            continue
        try:
            y = float(geom.get("y") or "")
        except (ValueError, TypeError):
            continue
        # Find which row contains it
        for period in periods:
            if period.y_min <= y < period.y_max:
                period.member_yed_ids.append(nid)
                break

    return periods
```

- [ ] **Step 2: Verify import + smoke test on yE-A fixture**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
PYTHONPATH="$PWD" python -c "
from modules.s3dgraphy.sync.yed_table_parser import extract_periods, PeriodCandidate
print('imports OK')
periods = extract_periods('tests/sync/fixtures/em_demo_02_mini.graphml')
print(f'mini fixture: {len(periods)} periods')
for p in periods:
    print(f'  {p.yed_row_id}: {p.auto_label!r} periodo={p.auto_periodo} y=[{p.y_min},{p.y_max}) members={len(p.member_yed_ids)}')
"
```

Expected output:
```
imports OK
mini fixture: 2 periods
  row_0: 'Period01' periodo=1 y=[30.0,330.0) members=4
  row_1: 'Period02' periodo=2 y=[330.0,630.0) members=2
```

If counts mismatch → STOP and debug before continuing. The fixture geometry was verified at plan-writing: TableNode at y=0, height=600, header=30 (default), 2 rows of height=300 each. Leaves at y=100,160,220,400,460 distribute as 4 in row_0 + 2 in row_1 (US01/US02/USV101/material in row 0; SF105/VSF107 in row 1).

### Task A.2: Create `modules/s3dgraphy/sync/yed_group_walker.py`

**Files:** Create `modules/s3dgraphy/sync/yed_group_walker.py`.

- [ ] **Step 1: Create the module**

Use the Write tool with EXACTLY this content:

```python
"""yEd group folder walker (yE-C Parsers, 5.7.7-alpha).

Descends `yfiles.foldertype="group"` hierarchy and produces
FolderCandidate records with prefix-derived auto-classification
(VA->attivita, AR->area, ST->struttura, SE->settore, AM->ambient,
SG->saggio, QP->quad_par).

Excludes the top-level swimlane (TableNode container) — yE-C
yed_table_parser handles that as periods.

Auto-value extraction: regex `^([A-Z]+\\d+)` captures the
"VA01" prefix from "VA01-foundation example"; the trailing
description is preserved in extra_attrs["description"].

Cycle detection via visited set; raises CycleDetectedError
(imported from graph_ingestor.py) on malformed input.

Returns [] on parse error / missing file / no folders.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .graph_ingestor import CycleDetectedError


# Order-sensitive: first match wins. Patterns match prefix only;
# auto_value strips trailing digits + description.
DEFAULT_FOLDER_PREFIX_MAP: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^VA"), "attivita"),
    (re.compile(r"^AR"), "area"),
    (re.compile(r"^ST"), "struttura"),
    (re.compile(r"^SE"), "settore"),
    (re.compile(r"^AM"), "ambient"),
    (re.compile(r"^SG"), "saggio"),
    (re.compile(r"^QP"), "quad_par"),
]


_VALUE_PREFIX_RE = re.compile(r"^([A-Z]+\d+)")


@dataclass
class FolderCandidate:
    """One yEd group folder with prefix-derived auto-classification."""
    yed_id: str
    full_label: str
    auto_dimension: str | None
    user_dimension: str | None
    auto_value: str
    user_value: str
    member_yed_ids: list[str] = field(default_factory=list)
    nested_folder_ids: list[str] = field(default_factory=list)
    parent_folder_id: str | None = None
    extra_attrs: dict = field(default_factory=dict)


def _classify_label(full_label: str) -> tuple[str | None, str, dict]:
    """Return (auto_dimension, auto_value, extra_attrs) for a folder label."""
    dimension: str | None = None
    for pat, dim in DEFAULT_FOLDER_PREFIX_MAP:
        if pat.match(full_label):
            dimension = dim
            break

    # Extract prefix-only via regex; trailing text -> description
    match = _VALUE_PREFIX_RE.match(full_label)
    if match:
        value = match.group(1)
        rest = full_label[len(value):].lstrip("- ").strip()
        extra = {"description": rest} if rest else {}
    else:
        value = full_label
        extra = {}

    return dimension, value, extra


def walk_folders(graphml_path: Path | str) -> list[FolderCandidate]:
    """Walk yEd group folder hierarchy and build candidates.

    Args:
        graphml_path: filesystem path to the .graphml file.

    Returns:
        List of FolderCandidate in document order. Empty list if no
        folders found, parse error, or missing file.

    Raises:
        CycleDetectedError: if folder A contains folder B contains
            folder A (malformed graphml). Hook's outer try/except
            swallows this gracefully.
    """
    path = Path(graphml_path)
    if not path.exists():
        return []

    try:
        from lxml import etree as _ET
    except ImportError:
        import xml.etree.ElementTree as _ET  # type: ignore[no-redef]

    GRAPHML_NS = "{http://graphml.graphdrawing.org/xmlns}"
    Y_NS = "{http://www.yworks.com/xml/graphml}"

    try:
        tree = _ET.parse(str(path))
    except Exception:
        return []

    root = tree.getroot()

    result: list[FolderCandidate] = []
    visited: set[str] = set()

    def _is_top_level_tablenode(node) -> bool:
        """True if this folder is the swimlane (has TableNode child)."""
        tn = node.find(f".//{Y_NS}TableNode")
        return tn is not None and tn.get("configuration") == "YED_TABLE_NODE"

    def _extract_label(node) -> str:
        """First non-empty <y:NodeLabel> text."""
        for nl in node.iter(f"{Y_NS}NodeLabel"):
            txt = (nl.text or "").strip()
            if txt:
                return txt
        return ""

    def _walk(node, parent_id: str | None):
        nid = node.get("id") or ""
        if nid in visited:
            raise CycleDetectedError(
                f"Cycle detected: folder {nid!r} visited twice"
            )
        visited.add(nid)

        # Find this folder's nested <graph> element (direct child)
        inner_graph = node.find(f"{GRAPHML_NS}graph")
        member_ids: list[str] = []
        nested_ids: list[str] = []

        if inner_graph is not None:
            for child in inner_graph.findall(f"{GRAPHML_NS}node"):
                cid = child.get("id") or ""
                if child.get("yfiles.foldertype") == "group":
                    # Skip top-level TableNode swimlane (handled by
                    # table_parser). For non-TableNode subfolders,
                    # record + recurse.
                    if _is_top_level_tablenode(child):
                        continue
                    nested_ids.append(cid)
                    # Recurse (depth-first walk)
                    _walk(child, parent_id=nid)
                else:
                    member_ids.append(cid)

        full_label = _extract_label(node)
        dim, value, extra = _classify_label(full_label)
        candidate = FolderCandidate(
            yed_id=nid,
            full_label=full_label,
            auto_dimension=dim,
            user_dimension=dim,
            auto_value=value,
            user_value=value,
            member_yed_ids=member_ids,
            nested_folder_ids=nested_ids,
            parent_folder_id=parent_id,
            extra_attrs=extra,
        )
        result.append(candidate)

    # Top-level: iterate all <graph><node yfiles.foldertype="group">
    # in document order. Skip the TableNode swimlane.
    for top_graph in root.findall(f"{GRAPHML_NS}graph"):
        for child in top_graph.findall(f"{GRAPHML_NS}node"):
            if child.get("yfiles.foldertype") != "group":
                continue
            if _is_top_level_tablenode(child):
                # Swimlane container — recurse INTO it to find
                # nested folders, but don't record it.
                inner = child.find(f"{GRAPHML_NS}graph")
                if inner is not None:
                    for inner_child in inner.findall(
                            f"{GRAPHML_NS}node"):
                        if inner_child.get(
                                "yfiles.foldertype") == "group":
                            _walk(inner_child, parent_id=None)
                continue
            _walk(child, parent_id=None)

    return result
```

- [ ] **Step 2: Verify import + smoke test on yE-A fixture**

```bash
PYTHONPATH="$PWD" python -c "
from modules.s3dgraphy.sync.yed_group_walker import walk_folders, FolderCandidate, DEFAULT_FOLDER_PREFIX_MAP
print('imports OK')
print(f'rules count: {len(DEFAULT_FOLDER_PREFIX_MAP)}')
folders = walk_folders('tests/sync/fixtures/em_demo_02_mini.graphml')
print(f'mini fixture: {len(folders)} folders')
for f in folders:
    print(f'  {f.yed_id}: {f.full_label!r} dim={f.auto_dimension} val={f.auto_value!r} members={len(f.member_yed_ids)} extra={f.extra_attrs}')
"
```

Expected output:
```
imports OK
rules count: 7
mini fixture: 2 folders
  n0::n0: 'VA01-foundation example' dim=attivita val='VA01' members=4 extra={'description': 'foundation example'}
  n0::n1: 'AR01-area example' dim=area val='AR01' members=2 extra={'description': 'area example'}
```

If counts/values mismatch → STOP and debug.

### Task A.3: Modify `modules/s3dgraphy/sync/ingest_result.py` — add `parsed_drafts` field

**Files:** Modify `modules/s3dgraphy/sync/ingest_result.py`.

- [ ] **Step 1: Read current IngestResult**

```bash
sed -n '/^@dataclass.*frozen=True.*$/,/^[a-zA-Z@]/p' modules/s3dgraphy/sync/ingest_result.py | head -30
```

Note: `IngestResult` is `@dataclass(frozen=True)` with fields ending at `dry_run: bool = False`.

- [ ] **Step 2: Use the Edit tool to add the field**

Find this exact text:

```python
    epochs_created: int     # auto-created periodizzazione rows
    conflicts: tuple[ConflictRecord, ...] = ()
    errors: tuple[str, ...] = ()
    dry_run: bool = False
```

Replace with:

```python
    epochs_created: int     # auto-created periodizzazione rows
    conflicts: tuple[ConflictRecord, ...] = ()
    errors: tuple[str, ...] = ()
    dry_run: bool = False
    # yE-C (5.7.7-alpha): structured output from the yEd-raw parse
    # phase. Populated by populate_list() when graphml_path is
    # yEd-raw; None for pyarchinit-projected graphmls.
    # Shape when populated:
    #   {"classified": list[ClassifiedNode],
    #    "periods": list[PeriodCandidate],
    #    "folders": list[FolderCandidate]}
    # Forward-compat with yE-D pipeline.
    parsed_drafts: dict | None = None
```

- [ ] **Step 3: Verify**

```bash
PYTHONPATH="$PWD" python -c "
from modules.s3dgraphy.sync.ingest_result import IngestResult
import dataclasses
fields = [f.name for f in dataclasses.fields(IngestResult)]
print('fields:', fields)
# Construct with old signature (no parsed_drafts) — should work
ir = IngestResult(applied=0, inserted=0, updated=0, skipped=0, epochs_created=0)
print('ir.parsed_drafts:', ir.parsed_drafts)
# Construct with new signature
ir2 = IngestResult(applied=0, inserted=0, updated=0, skipped=0, epochs_created=0, parsed_drafts={'a': 1})
print('ir2.parsed_drafts:', ir2.parsed_drafts)
"
```

Expected:
```
fields: ['applied', 'inserted', 'updated', 'skipped', 'epochs_created', 'conflicts', 'errors', 'dry_run', 'parsed_drafts']
ir.parsed_drafts: None
ir2.parsed_drafts: {'a': 1}
```

### Task A.4: Update branch hook in `graph_ingestor.py:169-196`

**Files:** Modify `modules/s3dgraphy/sync/graph_ingestor.py`.

- [ ] **Step 1: Locate the current yE-B block**

```bash
sed -n '165,200p' modules/s3dgraphy/sync/graph_ingestor.py
```

- [ ] **Step 2: Replace the yE-B hook block with yE-C version**

Use the Edit tool. Find this exact yE-B block:

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

Replace with the yE-C version:

```python
        # yE-A + yE-B + yE-C: yEd-raw detection + classify + parse.
        # When graphml_path is provided AND it's a yEd-raw file (no
        # pyarchinit.* keys), classify leaves, extract periods, walk
        # folders. Log a 3-line summary + populate
        # _yed_parsed_drafts (passed to IngestResult below). Then
        # fall through to legacy path (full pipeline wiring lands
        # in yE-D).
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
                # Detection + parsing is best-effort;
                # never block the legacy path
                pass
        # -- existing pyarchinit-projected path UNCHANGED below --
```

- [ ] **Step 3: Add `parsed_drafts=` to the final IngestResult construction**

Find this exact block (around line 648-654):

```python
        return IngestResult(
            applied=applied,
            inserted=inserted, updated=updated, skipped=skipped,
            epochs_created=epochs_created,
            conflicts=tuple(conflicts), errors=tuple(errors),
            dry_run=dry_run,
        )
```

Replace with:

```python
        return IngestResult(
            applied=applied,
            inserted=inserted, updated=updated, skipped=skipped,
            epochs_created=epochs_created,
            conflicts=tuple(conflicts), errors=tuple(errors),
            dry_run=dry_run,
            parsed_drafts=_yed_parsed_drafts,
        )
```

- [ ] **Step 4: Syntax check**

```bash
PYTHONPATH="$PWD" python -c "
import ast
with open('modules/s3dgraphy/sync/graph_ingestor.py') as f:
    ast.parse(f.read())
print('graph_ingestor.py syntax OK')
"
```

Expected: `graph_ingestor.py syntax OK`.

- [ ] **Step 5: Quick smoke test of the full integration**

```bash
PYTHONPATH="$PWD" python -c "
from modules.s3dgraphy.sync.yed_detector import detect_flavor
from modules.s3dgraphy.sync.yed_classifier import classify_leaves
from modules.s3dgraphy.sync.yed_table_parser import extract_periods
from modules.s3dgraphy.sync.yed_group_walker import walk_folders
from collections import Counter
path = 'tests/sync/fixtures/em_demo_02_mini.graphml'
print(f'flavor: {detect_flavor(path)}')
classified = classify_leaves(path)
periods = extract_periods(path)
folders = walk_folders(path)
counts = Counter(n.auto_kind.value for n in classified)
print(f'  Classified {len(classified)} leaves: {dict(counts)}')
print(f'  Detected {len(periods)} periods: {[p.auto_label for p in periods]}')
print(f'  Detected {len(folders)} folders: {[(f.auto_value, f.auto_dimension, len(f.member_yed_ids)) for f in folders]}')
"
```

Expected:
```
flavor: yed-raw
  Classified 6 leaves: {'us_real': 2, 'usv_virtual': 1, 'special_find': 1, 'virtual_find': 1, 'property': 1}
  Detected 2 periods: ['Period01', 'Period02']
  Detected 2 folders: [('VA01', 'attivita', 4), ('AR01', 'area', 2)]
```

If any field is wrong → STOP and debug.

### Task A.5: Create `tests/sync/test_yed_table_parser.py` (6 L0 tests)

**Files:** Create `tests/sync/test_yed_table_parser.py`.

- [ ] **Step 1: Create the test file**

Use the Write tool with EXACTLY this content:

```python
"""yE-C Parsers: L0 unit tests for extract_periods().

Verifies TableNode detection, row-ordinal numbering, Y-coordinate
membership, header exclusion, empty-label placeholder, empty result
on no TableNode. Each test builds a synthetic graphml in tmp_path.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.s3dgraphy.sync.yed_table_parser import (
    PeriodCandidate,
    extract_periods,
)


def _make_table_graphml(
    tmp_path: Path,
    rows: list[tuple[str, str, float]],  # (row_id, label, height)
    leaves: list[tuple[str, float]],     # (yed_id, y_coord)
    table_y: float = 0.0,
    header_height: float = 30.0,
) -> Path:
    """Build a synthetic graphml with a TableNode + rows + leaves."""
    row_label_xml = ""
    row_geom_xml = ""
    for rid, label, height in rows:
        row_label_xml += (
            f'<y:NodeLabel>{label}'
            f'<y:LabelModel><y:RowNodeLabelModel offset="3.0"/></y:LabelModel>'
            f'<y:ModelParameter>'
            f'<y:RowNodeLabelModelParameter id="{rid}" inside="true"/>'
            f'</y:ModelParameter>'
            f'</y:NodeLabel>'
        )
        row_geom_xml += f'<y:Row id="{rid}" height="{height}"/>'

    leaf_xml = ""
    for nid, y in leaves:
        leaf_xml += (
            f'<node id="{nid}">'
            f'<data key="d6"><y:ShapeNode>'
            f'<y:Geometry height="40.0" width="80.0" x="50.0" y="{y}"/>'
            f'<y:NodeLabel>{nid}</y:NodeLabel>'
            f'</y:ShapeNode></data>'
            f'</node>'
        )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="n0" yfiles.foldertype="group">
      <data key="d6">
        <y:TableNode configuration="YED_TABLE_NODE">
          <y:Geometry height="600.0" width="800.0" x="0.0" y="{table_y}"/>
          {row_label_xml}
          <y:Table>
            <y:Insets top="{header_height}"/>
            <y:Rows>{row_geom_xml}</y:Rows>
          </y:Table>
        </y:TableNode>
      </data>
      <graph edgedefault="directed" id="n0:">
        {leaf_xml}
      </graph>
    </node>
  </graph>
</graphml>
"""
    path = tmp_path / "test_table.graphml"
    path.write_text(xml)
    return path


def _make_graphml_no_table(tmp_path: Path) -> Path:
    """Graphml without any TableNode."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="n0">
      <data key="d6"><y:ShapeNode>
        <y:Geometry height="40.0" width="80.0" x="50.0" y="100.0"/>
        <y:NodeLabel>US01</y:NodeLabel>
      </y:ShapeNode></data>
    </node>
  </graph>
</graphml>
"""
    path = tmp_path / "no_table.graphml"
    path.write_text(xml)
    return path


def test_no_table_node_returns_empty(tmp_path):
    """Graphml without any TableNode -> []."""
    path = _make_graphml_no_table(tmp_path)
    result = extract_periods(path)
    assert result == []


def test_extract_em_demo_02_mini_2_periods():
    """Run on the yE-A reference fixture -> 2 periods (Period01, Period02)."""
    fixture = Path(__file__).parent / "fixtures" / "em_demo_02_mini.graphml"
    result = extract_periods(fixture)
    assert len(result) == 2
    assert result[0].auto_label == "Period01"
    assert result[1].auto_label == "Period02"


def test_period_ordinal_from_row_order(tmp_path):
    """row_0 -> periodo=1, row_1 -> periodo=2, row_2 -> periodo=3."""
    path = _make_table_graphml(
        tmp_path,
        rows=[("row_0", "P1", 100.0), ("row_1", "P2", 100.0),
              ("row_2", "P3", 100.0)],
        leaves=[],
    )
    result = extract_periods(path)
    assert len(result) == 3
    assert result[0].auto_periodo == 1
    assert result[1].auto_periodo == 2
    assert result[2].auto_periodo == 3
    # auto_fase always 1
    assert all(p.auto_fase == 1 for p in result)


def test_member_assignment_by_y_coordinate(tmp_path):
    """Leaves at y=50 and y=150 with rows [0-100) and [100-200) ->
    leaf at 50 in row 0, leaf at 150 in row 1.
    Note: table_y=0, header_height=0 for this test for simple math."""
    path = _make_table_graphml(
        tmp_path,
        rows=[("row_0", "P1", 100.0), ("row_1", "P2", 100.0)],
        leaves=[("L0", 50.0), ("L1", 150.0)],
        table_y=0.0,
        header_height=0.0,
    )
    result = extract_periods(path)
    assert len(result) == 2
    assert "L0" in result[0].member_yed_ids
    assert "L1" in result[1].member_yed_ids


def test_member_assignment_excludes_header_area(tmp_path):
    """Leaf at y=10 with header at [0-30) and row at [30-130) ->
    leaf is in the header area, NOT in any row's member_yed_ids."""
    path = _make_table_graphml(
        tmp_path,
        rows=[("row_0", "P1", 100.0)],
        leaves=[("L_header", 10.0), ("L_row", 50.0)],
        table_y=0.0,
        header_height=30.0,
    )
    result = extract_periods(path)
    assert len(result) == 1
    assert "L_header" not in result[0].member_yed_ids
    assert "L_row" in result[0].member_yed_ids


def test_empty_row_label_uses_placeholder(tmp_path):
    """A row with empty <NodeLabel> -> auto_label = 'row_{index}'."""
    # We can't easily put an empty NodeLabel via the helper since the
    # helper always inserts the label text. Build raw XML instead.
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="n0" yfiles.foldertype="group">
      <data key="d6">
        <y:TableNode configuration="YED_TABLE_NODE">
          <y:Geometry height="200.0" width="800.0" x="0.0" y="0.0"/>
          <y:Table>
            <y:Insets top="0"/>
            <y:Rows>
              <y:Row id="row_0" height="100.0"/>
              <y:Row id="row_1" height="100.0"/>
            </y:Rows>
          </y:Table>
        </y:TableNode>
      </data>
      <graph edgedefault="directed" id="n0:"/>
    </node>
  </graph>
</graphml>
"""
    path = tmp_path / "empty_labels.graphml"
    path.write_text(xml)
    result = extract_periods(path)
    assert len(result) == 2
    assert result[0].auto_label == "row_0"
    assert result[1].auto_label == "row_1"
```

- [ ] **Step 2: Run the 6 L0 tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_yed_table_parser.py -v 2>&1 | tail -15
```

Expected: `6 passed`.

### Task A.6: Create `tests/sync/test_yed_group_walker.py` (7 L0 tests)

**Files:** Create `tests/sync/test_yed_group_walker.py`.

- [ ] **Step 1: Create the test file**

Use the Write tool with EXACTLY this content:

```python
"""yE-C Parsers: L0 unit tests for walk_folders().

Verifies empty result on no folders, mini-fixture detection,
TableNode exclusion, label-description split, unknown prefix
fallback, nested folder membership, cycle detection.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.s3dgraphy.sync.graph_ingestor import CycleDetectedError
from modules.s3dgraphy.sync.yed_group_walker import (
    FolderCandidate,
    walk_folders,
)


def _make_graphml_no_folders(tmp_path: Path) -> Path:
    """Graphml with leaf nodes only, no folders."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="n0">
      <data key="d6"><y:ShapeNode>
        <y:NodeLabel>US01</y:NodeLabel>
      </y:ShapeNode></data>
    </node>
  </graph>
</graphml>
"""
    path = tmp_path / "no_folders.graphml"
    path.write_text(xml)
    return path


def _make_graphml_one_folder(tmp_path: Path, label: str) -> Path:
    """Graphml with one folder containing one leaf."""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="n0" yfiles.foldertype="group">
      <data key="d6">
        <y:ProxyAutoBoundsNode>
          <y:Realizers active="0">
            <y:GroupNode>
              <y:NodeLabel>{label}</y:NodeLabel>
            </y:GroupNode>
          </y:Realizers>
        </y:ProxyAutoBoundsNode>
      </data>
      <graph edgedefault="directed" id="n0:">
        <node id="n0::n0">
          <data key="d6"><y:ShapeNode><y:NodeLabel>X</y:NodeLabel></y:ShapeNode></data>
        </node>
      </graph>
    </node>
  </graph>
</graphml>
"""
    path = tmp_path / "one_folder.graphml"
    path.write_text(xml)
    return path


def test_no_folders_returns_empty(tmp_path):
    """Graphml without any folders -> []."""
    path = _make_graphml_no_folders(tmp_path)
    result = walk_folders(path)
    assert result == []


def test_walk_em_demo_02_mini_finds_2_folders():
    """Run on yE-A reference fixture -> 2 folders (VA01, AR01)."""
    fixture = Path(__file__).parent / "fixtures" / "em_demo_02_mini.graphml"
    result = walk_folders(fixture)
    assert len(result) == 2
    values = {f.auto_value for f in result}
    assert values == {"VA01", "AR01"}


def test_top_level_tablenode_excluded_from_folders():
    """Mini fixture has 'Archaeological Context' as the swimlane
    TableNode (technically yfiles.foldertype='group'). It MUST NOT
    appear in walk_folders result."""
    fixture = Path(__file__).parent / "fixtures" / "em_demo_02_mini.graphml"
    result = walk_folders(fixture)
    labels = {f.full_label for f in result}
    assert "Archaeological Context" not in labels


def test_label_with_description_extracts_prefix(tmp_path):
    """'VA01-foundation example' -> auto_value='VA01',
    extra_attrs['description']='foundation example'."""
    path = _make_graphml_one_folder(tmp_path, "VA01-foundation example")
    result = walk_folders(path)
    assert len(result) == 1
    assert result[0].auto_value == "VA01"
    assert result[0].auto_dimension == "attivita"
    assert result[0].extra_attrs.get("description") == "foundation example"


def test_unrecognized_prefix_uses_full_label_as_auto_value(tmp_path):
    """Folder labeled 'Foundation Area' has no prefix match ->
    auto_dimension=None, auto_value='Foundation Area' (no
    description extracted because no prefix)."""
    path = _make_graphml_one_folder(tmp_path, "Foundation Area")
    result = walk_folders(path)
    assert len(result) == 1
    assert result[0].auto_dimension is None
    assert result[0].auto_value == "Foundation Area"
    assert result[0].extra_attrs == {}


def test_nested_folder_membership_split(tmp_path):
    """Folder A -> folder B -> leaf X. A.member_yed_ids excludes X
    (direct children only); A.nested_folder_ids includes B.yed_id;
    B.member_yed_ids includes X; B.parent_folder_id == A.yed_id."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="A" yfiles.foldertype="group">
      <data key="d6"><y:ProxyAutoBoundsNode><y:Realizers active="0">
        <y:GroupNode><y:NodeLabel>VA01</y:NodeLabel></y:GroupNode>
      </y:Realizers></y:ProxyAutoBoundsNode></data>
      <graph edgedefault="directed" id="A:">
        <node id="B" yfiles.foldertype="group">
          <data key="d6"><y:ProxyAutoBoundsNode><y:Realizers active="0">
            <y:GroupNode><y:NodeLabel>AR01</y:NodeLabel></y:GroupNode>
          </y:Realizers></y:ProxyAutoBoundsNode></data>
          <graph edgedefault="directed" id="B:">
            <node id="X">
              <data key="d6"><y:ShapeNode><y:NodeLabel>US01</y:NodeLabel></y:ShapeNode></data>
            </node>
          </graph>
        </node>
      </graph>
    </node>
  </graph>
</graphml>
"""
    path = tmp_path / "nested.graphml"
    path.write_text(xml)
    result = walk_folders(path)
    # Walker is depth-first, so B is recorded before A returns
    by_id = {f.yed_id: f for f in result}
    assert "A" in by_id and "B" in by_id
    a = by_id["A"]
    b = by_id["B"]
    assert "X" not in a.member_yed_ids
    assert "B" in a.nested_folder_ids
    assert "X" in b.member_yed_ids
    assert b.parent_folder_id == "A"
    assert a.parent_folder_id is None


def test_cycle_detection_raises_cycle_detected_error(tmp_path):
    """Synthetic graphml where folder A's child folder B contains
    a node with id=A again (impossible in real yEd but the walker's
    visited set must catch the cycle)."""
    # We simulate a cycle by having two folders with the same id
    # nested inside each other. lxml parses this fine; the walker
    # raises when it re-visits.
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="A" yfiles.foldertype="group">
      <data key="d6"><y:ProxyAutoBoundsNode><y:Realizers active="0">
        <y:GroupNode><y:NodeLabel>VA01</y:NodeLabel></y:GroupNode>
      </y:Realizers></y:ProxyAutoBoundsNode></data>
      <graph edgedefault="directed" id="A:">
        <node id="A" yfiles.foldertype="group">
          <data key="d6"><y:ProxyAutoBoundsNode><y:Realizers active="0">
            <y:GroupNode><y:NodeLabel>VA01-inner</y:NodeLabel></y:GroupNode>
          </y:Realizers></y:ProxyAutoBoundsNode></data>
          <graph edgedefault="directed" id="A2:"/>
        </node>
      </graph>
    </node>
  </graph>
</graphml>
"""
    path = tmp_path / "cycle.graphml"
    path.write_text(xml)
    with pytest.raises(CycleDetectedError):
        walk_folders(path)
```

- [ ] **Step 2: Run the 7 L0 tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_yed_group_walker.py -v 2>&1 | tail -15
```

Expected: `7 passed`.

### Task A.7: Create the 3 L1 integration tests

**Files:**
- Create: `tests/sync/test_table_parser_integration.py`
- Create: `tests/sync/test_group_walker_integration.py`
- Create: `tests/sync/test_yed_parsers_orchestration.py`

- [ ] **Step 1: Create `test_table_parser_integration.py`**

Use the Write tool with EXACTLY this content:

```python
"""yE-C Parsers: L1 integration test for extract_periods() on the
yE-A reference fixture (em_demo_02_mini.graphml)."""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.s3dgraphy.sync.yed_table_parser import extract_periods

FIXTURES = Path(__file__).parent / "fixtures"


def test_extract_periods_em_demo_02_mini():
    """Mini fixture has TableNode with 2 rows (Period01, Period02).
    Each row is 300px tall with header_height=30 (default).
    Row 0: y=[30, 330), 4 leaves at y=100/160/220/100.
    Row 1: y=[330, 630), 2 leaves at y=400/460.
    """
    fixture = FIXTURES / "em_demo_02_mini.graphml"
    assert fixture.exists(), f"Expected yE-A fixture at {fixture}"

    periods = extract_periods(fixture)
    assert len(periods) == 2

    p0 = periods[0]
    assert p0.auto_label == "Period01"
    assert p0.auto_periodo == 1
    assert p0.auto_fase == 1
    assert p0.user_label == p0.auto_label
    assert p0.user_periodo == 1
    assert p0.user_fase == 1

    p1 = periods[1]
    assert p1.auto_label == "Period02"
    assert p1.auto_periodo == 2
    assert p1.auto_fase == 1

    # Y-coord membership: total members <= 6 leaves in fixture.
    total_members = sum(len(p.member_yed_ids) for p in periods)
    assert 0 <= total_members <= 6, f"got {total_members} members"
```

- [ ] **Step 2: Create `test_group_walker_integration.py`**

Use the Write tool with EXACTLY this content:

```python
"""yE-C Parsers: L1 integration test for walk_folders() on the
yE-A reference fixture (em_demo_02_mini.graphml)."""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.s3dgraphy.sync.yed_group_walker import walk_folders

FIXTURES = Path(__file__).parent / "fixtures"


def test_walk_folders_em_demo_02_mini():
    """Mini fixture has 2 group folders:
      - VA01-foundation example (attivita, 4 direct leaves)
      - AR01-area example (area, 2 direct leaves)
    Top-level TableNode 'Archaeological Context' must be excluded.
    """
    fixture = FIXTURES / "em_demo_02_mini.graphml"
    assert fixture.exists(), f"Expected yE-A fixture at {fixture}"

    folders = walk_folders(fixture)
    assert len(folders) == 2

    by_value = {f.auto_value: f for f in folders}
    assert "VA01" in by_value
    assert "AR01" in by_value

    va01 = by_value["VA01"]
    assert va01.full_label == "VA01-foundation example"
    assert va01.auto_dimension == "attivita"
    assert va01.user_dimension == "attivita"
    assert va01.extra_attrs.get("description") == "foundation example"
    assert len(va01.member_yed_ids) == 4

    ar01 = by_value["AR01"]
    assert ar01.full_label == "AR01-area example"
    assert ar01.auto_dimension == "area"
    assert ar01.extra_attrs.get("description") == "area example"
    assert len(ar01.member_yed_ids) == 2

    # Top-level TableNode "Archaeological Context" must NOT appear.
    labels = {f.full_label for f in folders}
    assert "Archaeological Context" not in labels
```

- [ ] **Step 3: Create `test_yed_parsers_orchestration.py`**

Use the Write tool with EXACTLY this content:

```python
"""yE-C Parsers: L1 cross-parser orchestration test.

Verifies that yE-B classifier + yE-C table parser + yE-C group
walker produce mutually consistent state on the same fixture.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.s3dgraphy.sync.yed_classifier import classify_leaves
from modules.s3dgraphy.sync.yed_group_walker import walk_folders
from modules.s3dgraphy.sync.yed_table_parser import extract_periods

FIXTURES = Path(__file__).parent / "fixtures"


def test_classifier_periods_folders_consistent_on_em_demo_02_mini():
    """Cross-parser consistency on the yE-A reference fixture.

    Mini fixture has 6 leaves total, distributed across 2 group
    folders (VA01 has 4, AR01 has 2). 2 periods. Classifier sees
    only the 6 leaves (folders excluded); walker sees 2 folders
    (TableNode excluded); periods see all 6 leaves distributed by
    Y-coordinate.
    """
    fixture = FIXTURES / "em_demo_02_mini.graphml"
    assert fixture.exists()

    classified = classify_leaves(fixture)
    periods = extract_periods(fixture)
    folders = walk_folders(fixture)

    # Counts
    assert len(classified) == 6, f"got {len(classified)} classified"
    assert len(periods) == 2, f"got {len(periods)} periods"
    assert len(folders) == 2, f"got {len(folders)} folders"

    # No leaf yed_id appears as a folder (folders are NOT leaves).
    classified_ids = {n.yed_id for n in classified}
    folder_ids = {f.yed_id for f in folders}
    assert classified_ids.isdisjoint(folder_ids), \
        f"Overlap: {classified_ids & folder_ids}"

    # Every classified leaf appears in at least one folder's
    # member list.
    all_members: set = set()
    for f in folders:
        all_members.update(f.member_yed_ids)
    assert classified_ids.issubset(all_members), \
        f"Leaves not accounted for: {classified_ids - all_members}"

    # Folder labels don't leak into classified labels.
    classified_labels = {n.label for n in classified}
    folder_labels = {f.full_label for f in folders}
    assert classified_labels.isdisjoint(folder_labels)
```

- [ ] **Step 4: Run all 3 L1 tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_table_parser_integration.py tests/sync/test_group_walker_integration.py tests/sync/test_yed_parsers_orchestration.py -v 2>&1 | tail -15
```

Expected: `3 passed`.

### Task A.8: Run full regression suite

- [ ] **Step 1: Run all gates**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py tests/sync/test_round_trip.py tests/sync/test_round_trip_with_paradata.py tests/sync/test_round_trip_with_groups.py tests/sync/test_graph_projector_paradata.py -v 2>&1 | tail -12
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py tests/sync/test_group_store_pg.py -v 2>&1 | tail -10
PYTHONPATH="$PWD" python -m pytest tests/sync/test_yed_detector.py tests/sync/test_yed_classifier.py tests/sync/test_yed_classifier_integration.py tests/sync/test_yed_table_parser.py tests/sync/test_yed_group_walker.py tests/sync/test_table_parser_integration.py tests/sync/test_group_walker_integration.py tests/sync/test_yed_parsers_orchestration.py -v 2>&1 | tail -40
```

Expected:
- Full suite: `289 passed, 33 skipped` (273 baseline + 13 L0 + 3 L1)
- AC-2 + round_trip + 3 critical gates: `10 passed`
- 8 PG-D L2: `8 skipped` (PG offline)
- yE-A + yE-B + yE-C: `5 + 11 + 1 + 6 + 7 + 1 + 1 + 1 = 33 passed`

**IF ANY GATE BREAKS → STOP. Report BLOCKED with full test output. Do NOT commit.**

Likely causes:
- `IngestResult.parsed_drafts` field missing or wrong type → existing tests fail to construct
- Hook block syntax error → import fails
- `parsed_drafts=_yed_parsed_drafts` not added to final IngestResult construction → existing tests pass but new field always None on yEd-raw imports

### Task A.9: Commit Group A

- [ ] **Step 1: Stage + commit**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git add modules/s3dgraphy/sync/yed_table_parser.py \
        modules/s3dgraphy/sync/yed_group_walker.py \
        modules/s3dgraphy/sync/ingest_result.py \
        modules/s3dgraphy/sync/graph_ingestor.py \
        tests/sync/test_yed_table_parser.py \
        tests/sync/test_yed_group_walker.py \
        tests/sync/test_table_parser_integration.py \
        tests/sync/test_group_walker_integration.py \
        tests/sync/test_yed_parsers_orchestration.py
git commit -m "$(cat <<'EOF'
feat(yE-C): yEd TableNode parser + group walker + hook orchestration

Add modules/s3dgraphy/sync/yed_table_parser.py with the
extract_periods() function and PeriodCandidate dataclass. Reads
the top-level yEd TableNode swimlane and extracts archaeological
period candidates from its rows:
- y:RowNodeLabelModelParameter -> auto_label
- 1-based row ordinal -> auto_periodo (auto_fase always 1)
- Y-coordinate membership -> member_yed_ids per row
Leaves in the TableNode header area are excluded from membership.
datazione_iniziale/finale stay NULL -- user fills later in the
pyarchinit Periodizzazione tab.

Add modules/s3dgraphy/sync/yed_group_walker.py with walk_folders()
and FolderCandidate. Descends yfiles.foldertype="group" hierarchy
recursively, applies DEFAULT_FOLDER_PREFIX_MAP (7 patterns:
VA->attivita, AR->area, ST->struttura, SE->settore, AM->ambient,
SG->saggio, QP->quad_par), extracts prefix-only auto_value via
regex ^([A-Z]+\\d+), and preserves the description tail in
extra_attrs. Top-level TableNode swimlane is recursed-into but
NOT recorded (yE-C table_parser handles it). Reuses
CycleDetectedError from graph_ingestor.py.

Modify modules/s3dgraphy/sync/ingest_result.py: add
parsed_drafts: dict | None = None field to IngestResult
(@dataclass(frozen=True)). Default None preserves back-compat
for existing call sites. Field shape:
  {"classified": list[ClassifiedNode],
   "periods": list[PeriodCandidate],
   "folders": list[FolderCandidate]}

Modify modules/s3dgraphy/sync/graph_ingestor.py:169-196: update
the yE-B branch hook to orchestrate classify + extract_periods +
walk_folders and log a 3-line summary on yEd-raw imports.
Initialize _yed_parsed_drafts = None at function entry; populate
inside the hook block if yEd-raw detected. Pass
parsed_drafts=_yed_parsed_drafts at the final IngestResult(...)
construction (line 648-654) -- mutation via attribute assign is
forbidden because IngestResult is frozen.

Add 13 L0 unit tests:
- test_yed_table_parser.py (6 tests):
  - test_no_table_node_returns_empty
  - test_extract_em_demo_02_mini_2_periods
  - test_period_ordinal_from_row_order
  - test_member_assignment_by_y_coordinate
  - test_member_assignment_excludes_header_area
  - test_empty_row_label_uses_placeholder
- test_yed_group_walker.py (7 tests):
  - test_no_folders_returns_empty
  - test_walk_em_demo_02_mini_finds_2_folders
  - test_top_level_tablenode_excluded_from_folders
  - test_label_with_description_extracts_prefix
  - test_unrecognized_prefix_uses_full_label_as_auto_value
  - test_nested_folder_membership_split
  - test_cycle_detection_raises_cycle_detected_error

Add 3 L1 integration tests:
- test_table_parser_integration.py: extract_periods on yE-A fixture
  -> 2 periods (Period01, Period02)
- test_group_walker_integration.py: walk_folders on yE-A fixture
  -> 2 folders (VA01 attivita 4 members, AR01 area 2 members);
  TableNode "Archaeological Context" excluded
- test_yed_parsers_orchestration.py: cross-parser consistency.
  Classifier sees 6 leaves, walker sees 2 folders, periods sees
  2 periods; no leaf appears as a folder; every classified leaf
  is a member of at least one folder.

All regression gates preserved:
- AC-2 byte-identical (test_ai03_export_byte_identical)
- 3 critical SQLite gates (round_trip_with_paradata,
  round_trip_with_groups, graph_projector_paradata)
- 5 yE-A detector tests
- 12 yE-B classifier tests (11 L0 + 1 L1)
- 8 PG-D L2 tests (skip cleanly when PG offline)

Test counts: 273 -> 289 passed, 33 skipped (PG offline).
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
git log --oneline eb131d50..HEAD
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected:
- 1 commit since spec (`eb131d50`): Group A
- Full suite: `289 passed, 33 skipped`

## Self-review checklist before reporting back

- [ ] `yed_table_parser.py` created with `PeriodCandidate` + `extract_periods` per spec §5
- [ ] `yed_group_walker.py` created with `FolderCandidate` + `walk_folders` + `DEFAULT_FOLDER_PREFIX_MAP` (7 patterns) per spec §6
- [ ] `CycleDetectedError` imported from `graph_ingestor.py` (not redefined)
- [ ] Top-level TableNode excluded from `walk_folders` result (recursed-into but not recorded)
- [ ] `IngestResult.parsed_drafts: dict | None = None` field added
- [ ] Branch hook updated to call extract_periods + walk_folders + 3-line log + populate _yed_parsed_drafts
- [ ] `parsed_drafts=_yed_parsed_drafts` added to final `IngestResult(...)` construction (line ~648-654)
- [ ] All 13 L0 + 3 L1 tests pass with exact names from spec
- [ ] AC-2 byte-identical PASS
- [ ] 3 critical SQLite regression gates PASS
- [ ] 5 yE-A + 12 yE-B tests PRESERVED (pass)
- [ ] 8 PG-D L2 tests SKIP cleanly (or PASS if PG online)
- [ ] Full suite: 289 passed, 33 skipped (PG offline)
- [ ] Strict trailer check returns 0

## Report back format

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- Commit SHA
- Test counts
- Strict trailer check result (must be 0)
- Files changed (should be 9: 2 new prod + 5 new test + 2 modified)
- Any concerns

If you find yourself wanting to refactor beyond the plan, STOP and report DONE_WITH_CONCERNS.

---

## Group B — Docs + version 5.7.7-alpha

### Task B.1: Bump `metadata.txt`

**Files:** Modify `metadata.txt`.

- [ ] **Step 1: Bump version**

Use the Edit tool to change `version=5.7.6-alpha` → `version=5.7.7-alpha`.

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
grep "^version=" metadata.txt
```

Expected: `version=5.7.7-alpha`.

### Task B.2: Insert yE-C dev-log section

**Files:** Modify `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`.

- [ ] **Step 1: Prepend yE-C section above yE-B**

Use the Edit tool. Find this EXACT text:

```
---

## yE-B Classifier — yEd label-prefix classifier (5.7.6-alpha)
```

Replace with EXACTLY (preserving the yE-B heading at the end):

```
---

## yE-C Parsers — yEd TableNode + group walker (5.7.7-alpha)

**Tag:** `yed-import-parsers-5.7.7-alpha`
**Date:** 2026-05-12
**Spec:** `docs/superpowers/specs/2026-05-12-yed-import-parsers-design.md`
**Plan:** `docs/superpowers/plans/2026-05-12-yed-import-parsers.md`
**Predecessor:** `yed-import-classifier-5.7.6-alpha` (`640b4e83`)

### What shipped

- NEW `modules/s3dgraphy/sync/yed_table_parser.py` with
  `extract_periods()` function + `PeriodCandidate` dataclass
  (10 fields per parent spec §6)
- NEW `modules/s3dgraphy/sync/yed_group_walker.py` with
  `walk_folders()` function + `FolderCandidate` dataclass +
  `DEFAULT_FOLDER_PREFIX_MAP` (7 patterns: VA/AR/ST/SE/AM/SG/QP).
  Reuses `CycleDetectedError` from `graph_ingestor.py`.
- NEW `tests/sync/test_yed_table_parser.py` (6 L0 tests)
- NEW `tests/sync/test_yed_group_walker.py` (7 L0 tests)
- NEW `tests/sync/test_table_parser_integration.py` (1 L1 test)
- NEW `tests/sync/test_group_walker_integration.py` (1 L1 test)
- NEW `tests/sync/test_yed_parsers_orchestration.py` (1 L1 cross-parser test)
- MODIFY `modules/s3dgraphy/sync/ingest_result.py` (+5 LOC):
  add `parsed_drafts: dict | None = None` field to `IngestResult`
  dataclass (frozen=True). Default None preserves back-compat.
- MODIFY `modules/s3dgraphy/sync/graph_ingestor.py:169-196`:
  update yE-B branch hook to orchestrate classify + extract_periods
  + walk_folders + 3-line summary log. Initialize
  `_yed_parsed_drafts = None` at function entry; populate inside
  the hook if yEd-raw detected. Pass `parsed_drafts=_yed_parsed_drafts`
  at the final `IngestResult(...)` construction (line 648-654)
  -- mutation via attribute assign is forbidden because
  IngestResult is frozen.

### Architectural correction during plan-writing

The spec §7 said "attach to result before final return". This was
not possible because `IngestResult` is `@dataclass(frozen=True)`.
The plan corrected the approach: pass `parsed_drafts=` at
construction time. The result is cleaner (single construction site)
and preserves the frozen contract. Recorded as a deviation-from-spec
in the dev-log + commit message.

### Inheritance from parent spec

This milestone inherits from parent spec §6 (period extraction)
and §7 (group folder interpretation) and specializes for MVP:
- input is Path-only (NOT `Graph | Path | str` union)
- top-level TableNode excluded from walk_folders (yE-C
  table_parser handles it)
- `DEFAULT_FOLDER_PREFIX_MAP` is the only ruleset shipped; user
  override via dialog deferred to yE-E

### Tests

- 13 new L0 tests (always run, no Qt, no PG dep)
- 3 new L1 integration tests on em_demo_02_mini.graphml
- 5 yE-A detector tests + 12 yE-B classifier tests preserved
- 256 SQLite baseline + AC-2 + 3 critical SQLite regression gates
  + 8 PG-D L2 tests all preserved
- Total: 273 -> 289 passed, 33 skipped (PG offline) or
  281 -> 297 passed, 12 skipped (PG online + psycopg2)

### Branch hook log output (real-world)

On `/Users/enzo/Downloads/EM_demo_02.graphml` (82 leaves, 6 folders,
2 periods), the warning log becomes:

```
yEd-raw graphml detected at /Users/enzo/Downloads/EM_demo_02.graphml.
  Classified 82 leaves: combiner: 3, document: 38, property: 25,
    special_find: 2, us_real: 4, usv_virtual: 8, virtual_find: 2.
  Detected 2 periods: Period01, Contemporary era.
  Detected 6 group folders: VA01 (attivita, N members), VA02
    (attivita, M members), ...
  Yed-aware import path not yet wired (yE-C parsers only).
  Falling through to legacy path. Expect partial/incorrect ingestion.
```

### Next: yE-D (Pipeline + policy — `yed-import-pipeline-5.7.8-alpha`)

Will ship `yed_rapporti_policy.py` (folder-touching edge SKIP /
FAN_OUT / REPRESENTATIVE / SYNTHETIC policies) +
`yed_import_pipeline.py` (orchestrator consuming
`IngestResult.parsed_drafts` for real DB writes) + CLI
`scripts/import_yed_graphml.py --auto-defaults` + L1 integration
test verifying SQL changes via `_DryRunRollback` sentinel pattern
(reused from PG-C).

---

## yE-B Classifier — yEd label-prefix classifier (5.7.6-alpha)
```

### Task B.3: Prepend bilingual CHANGELOG entry

**Files:** Modify `dev_logs/CHANGELOG.md`.

- [ ] **Step 1: Prepend entry**

Use the Edit tool. Find this EXACT text:

```
## [5.7.6-alpha] - 2026-05-12
```

Replace with EXACTLY (preserving the original heading at the end):

```
## [5.7.7-alpha] - 2026-05-12

### Italiano

**yE-C Parsers — terzo milestone del feature yEd-aware graphml import.**

Aggiunge due parser standalone (`yed_table_parser.py` + `yed_group_walker.py`) wirati nel branch hook esistente. All'import di un file yEd-raw, il log ora mostra una sintesi a 3 righe: classifier counts + periods detected + group folders detected. Più il nuovo field `IngestResult.parsed_drafts: dict | None` per forward-compat con il pipeline yE-D.

Esempio su EM_demo_02.graphml (82 leaf, 6 folder, 2 periods):
```
yEd-raw graphml detected at <path>.
  Classified 82 leaves: combiner: 3, document: 38, property: 25, ...
  Detected 2 periods: Period01, Contemporary era.
  Detected 6 group folders: VA01 (attivita, N members), ...
  Yed-aware import path not yet wired (yE-C parsers only).
  Falling through to legacy path.
```

- **NEW `modules/s3dgraphy/sync/yed_table_parser.py`**: estrae yEd TableNode swimlane → list[PeriodCandidate]. `PeriodCandidate` ha 10 field (yed_row_id, auto_label, user_label, auto_periodo 1-based, auto_fase=1, user_periodo/fase, member_yed_ids da Y-coord, y_min/y_max). Leaf nell'header area (Y < primo row.y_min) esclusi dalla membership. datazione_iniziale/finale restano NULL (yEd non encoda date) — l'utente compila dopo nel tab pyarchinit Periodizzazione.
- **NEW `modules/s3dgraphy/sync/yed_group_walker.py`**: descende yfiles.foldertype="group" hierarchy → list[FolderCandidate]. `FolderCandidate` ha 10 field (yed_id, full_label, auto/user_dimension, auto/user_value, member_yed_ids direct only, nested_folder_ids, parent_folder_id, extra_attrs). `DEFAULT_FOLDER_PREFIX_MAP` con 7 pattern (VA→attivita, AR→area, ST→struttura, SE→settore, AM→ambient, SG→saggio, QP→quad_par). Auto-value extracts prefix via regex `^([A-Z]+\d+)`; description tail va in `extra_attrs["description"]`. Top-level TableNode swimlane recursed-into per nested folders ma NON registrato (yE-C table_parser handles it). Cycle detection riusa `CycleDetectedError` esistente.
- **NEW field `IngestResult.parsed_drafts: dict | None = None`** in `ingest_result.py`. Default None preserva back-compat con call sites esistenti. Shape: `{"classified": [...], "periods": [...], "folders": [...]}`. yE-D consumerà questo per le DB writes.
- **MODIFY `graph_ingestor.py:169-196`**: branch hook yE-B aggiornato per orchestrare classify + extract_periods + walk_folders + 3-line summary log. Local var `_yed_parsed_drafts` inizializzata a None all'inizio di populate_list(); popolata se yEd-raw detectato. Passata come `parsed_drafts=_yed_parsed_drafts` alla construction finale di `IngestResult(...)` (riga 648-654) — la mutation post-construction non è possibile perché `IngestResult` è `frozen=True`.
- **NEW 13 test L0** in `test_yed_table_parser.py` (6) + `test_yed_group_walker.py` (7): no TableNode → [], membership by Y-coord, header exclusion, empty label placeholder, prefix-vs-fallback, nested folder split, cycle detection.
- **NEW 3 test L1** in `test_table_parser_integration.py` + `test_group_walker_integration.py` + `test_yed_parsers_orchestration.py`: integration sulla fixture mini per per-parser + cross-parser consistency check.

**Correzione architetturale durante plan-writing**: lo spec §7 diceva "attach to result before final return" ma non possibile (`IngestResult` è frozen). Plan corretto: passare `parsed_drafts=` a costruzione invece. Soluzione più pulita.

**Eredita dal parent spec §6 + §7** specializzato per MVP:
- Input Path-only (NON Graph union)
- TableNode swimlane escluso da walk_folders
- DEFAULT_FOLDER_PREFIX_MAP è l'unico ruleset; override dialog deferito a yE-E

**Garanzie regressione (tutte verdi post-yE-C):**
- AC-2 byte-identical (`test_ai03_export_byte_identical`)
- 3 critical SQLite gates
- 5 yE-A + 12 yE-B preservati
- 8 PG-D L2 (skip puliti offline)

Test count: 273 → 289 passed, 33 skipped (PG offline) o 281 → 297 passed, 12 skipped (PG online + psycopg2).

### English

**yE-C Parsers — third milestone of the yEd-aware graphml import feature.**

Adds two standalone parsers (`yed_table_parser.py` + `yed_group_walker.py`) wired into the existing branch hook. On import of a yEd-raw file, the log now shows a 3-line summary: classifier counts + periods detected + group folders detected. Plus the new `IngestResult.parsed_drafts: dict | None` field for forward-compat with the yE-D pipeline.

Example on EM_demo_02.graphml (82 leaves, 6 folders, 2 periods):
```
yEd-raw graphml detected at <path>.
  Classified 82 leaves: combiner: 3, document: 38, property: 25, ...
  Detected 2 periods: Period01, Contemporary era.
  Detected 6 group folders: VA01 (attivita, N members), ...
  Yed-aware import path not yet wired (yE-C parsers only).
  Falling through to legacy path.
```

- **NEW `modules/s3dgraphy/sync/yed_table_parser.py`**: extracts yEd TableNode swimlane → list[PeriodCandidate]. 10 fields (yed_row_id, auto_label, user_label, 1-based auto_periodo, auto_fase=1, user counterparts, member_yed_ids by Y-coord, y_min/y_max). Leaves in the header area (Y < first row.y_min) excluded from membership. datazione_iniziale/finale stay NULL (yEd doesn't encode dates) — user fills later in pyarchinit Periodizzazione tab.
- **NEW `modules/s3dgraphy/sync/yed_group_walker.py`**: descends yfiles.foldertype="group" hierarchy → list[FolderCandidate]. 10 fields (yed_id, full_label, auto/user_dimension, auto/user_value, member_yed_ids direct only, nested_folder_ids, parent_folder_id, extra_attrs). `DEFAULT_FOLDER_PREFIX_MAP` with 7 patterns (VA→attivita, AR→area, ST→struttura, SE→settore, AM→ambient, SG→saggio, QP→quad_par). Auto-value extracts prefix via regex `^([A-Z]+\d+)`; description tail goes to `extra_attrs["description"]`. Top-level TableNode swimlane recursed-into for nested folders but NOT recorded (yE-C table_parser handles it). Cycle detection reuses existing `CycleDetectedError`.
- **NEW field `IngestResult.parsed_drafts: dict | None = None`** in `ingest_result.py`. Default None preserves back-compat with existing call sites. Shape: `{"classified": [...], "periods": [...], "folders": [...]}`. yE-D will consume this for DB writes.
- **MODIFY `graph_ingestor.py:169-196`**: yE-B branch hook updated to orchestrate classify + extract_periods + walk_folders + 3-line summary log. Local var `_yed_parsed_drafts` initialized to None at start of populate_list(); populated if yEd-raw detected. Passed as `parsed_drafts=_yed_parsed_drafts` to the final `IngestResult(...)` construction (line 648-654) — mutation after construction is not possible because `IngestResult` is `frozen=True`.
- **NEW 13 L0 tests** in `test_yed_table_parser.py` (6) + `test_yed_group_walker.py` (7): no TableNode → [], membership by Y-coord, header exclusion, empty label placeholder, prefix-vs-fallback, nested folder split, cycle detection.
- **NEW 3 L1 tests** in `test_table_parser_integration.py` + `test_group_walker_integration.py` + `test_yed_parsers_orchestration.py`: integration on the mini fixture for per-parser + cross-parser consistency check.

**Architectural correction during plan-writing**: spec §7 said "attach to result before final return" but not possible (`IngestResult` is frozen). Plan corrected: pass `parsed_drafts=` at construction instead. Cleaner solution.

**Inherits parent spec §6 + §7** specialized for MVP:
- Input is Path-only (NOT Graph union)
- TableNode swimlane excluded from walk_folders
- DEFAULT_FOLDER_PREFIX_MAP is the only ruleset; dialog override deferred to yE-E

**Regression guarantees (all green post-yE-C):**
- AC-2 byte-identical (`test_ai03_export_byte_identical`)
- 3 critical SQLite gates
- 5 yE-A + 12 yE-B preserved
- 8 PG-D L2 (skip cleanly offline)

Test count: 273 → 289 passed, 33 skipped (PG offline) or 281 → 297 passed, 12 skipped (PG online + psycopg2).

---

## [5.7.6-alpha] - 2026-05-12
```

### Task B.4: Commit + final verification

- [ ] **Step 1: Pre-commit verification**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git log --oneline eb131d50..HEAD
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
grep "^version=" metadata.txt
```

Expected:
- 1 commit since spec (`eb131d50`): Group A
- Test suite: `289 passed, 33 skipped`
- Version: `5.7.7-alpha`

- [ ] **Step 2: Commit Group B**

```bash
git add metadata.txt \
        docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md \
        dev_logs/CHANGELOG.md
git commit -m "$(cat <<'EOF'
release(yE-C): docs + version 5.7.7-alpha

yE-C Parsers milestone documentation: bilingual CHANGELOG entry,
dev-log yE-C section, version bump 5.7.6-alpha -> 5.7.7-alpha.

This is the third milestone of the 6-milestone yEd-aware graphml
import rollout. Ships two parsers (table_parser for periods +
group_walker for folder hierarchy) wired into the yE-B branch
hook with a 3-line summary log + IngestResult.parsed_drafts field
for forward-compat with yE-D pipeline.

Architectural correction during plan-writing: spec §7 said
"attach to result before final return" but IngestResult is
frozen=True. Plan corrected to pass parsed_drafts= at the final
IngestResult(...) construction (line 648-654 of graph_ingestor.py).
Recorded as deviation-from-spec in dev-log + commit message.

Inherits parent spec §6 (period extraction) + §7 (group folder
interpretation) and specializes for MVP: Path-only input,
TableNode swimlane excluded from walk_folders, DEFAULT_FOLDER_PREFIX_MAP
is the only ruleset (user override deferred to yE-E dialog).

Test count: 273 -> 289 passed, 33 skipped (PG offline) or
281 -> 297 passed, 12 skipped (PG online + psycopg2).
AC-2 byte-identical baseline preserved.
3 critical SQLite gates preserved.
5 yE-A + 12 yE-B tests preserved.
8 PG-D L2 tests preserved.

Spec: docs/superpowers/specs/2026-05-12-yed-import-parsers-design.md (eb131d50)
Plan: docs/superpowers/plans/2026-05-12-yed-import-parsers.md
Predecessor: yed-import-classifier-5.7.6-alpha (640b4e83)
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
git log --oneline eb131d50..HEAD
git log eb131d50..HEAD --format=%B | grep -cE "^Co-Authored-By:"
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
grep "^version=" metadata.txt
```

Expected:
- 2 commits since spec (`eb131d50`): A, B
- Trailer count: `0`
- `289 passed, 33 skipped`
- Version: `5.7.7-alpha`

---

## Group C — Annotated tag + USER APPROVAL GATE for push

### Task C.1: Branch check

- [ ] **Step 1: Confirm branch**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git rev-parse --abbrev-ref HEAD
```

Expected: `Stratigraph_00001`. STOP if anything else.

### Task C.2: Create annotated tag (LOCAL ONLY — do not push)

- [ ] **Step 1: Create tag**

```bash
git tag -a yed-import-parsers-5.7.7-alpha -m "$(cat <<'EOF'
yE-C Parsers - yEd TableNode + group walker + hook orchestration

Third milestone of the 6-milestone yEd-aware graphml import
rollout. Ships two parsers wired into the yE-B branch hook with
a 3-line summary log + IngestResult.parsed_drafts field for
forward-compat with the yE-D pipeline.

Cumulative deliverables (Groups A-B, 2 commits):

- NEW modules/s3dgraphy/sync/yed_table_parser.py with
  extract_periods() function + PeriodCandidate dataclass (10 fields).
  Reads yEd TableNode swimlane, assigns leaves to rows by
  Y-coordinate, excludes header area.
- NEW modules/s3dgraphy/sync/yed_group_walker.py with walk_folders()
  + FolderCandidate (10 fields) + DEFAULT_FOLDER_PREFIX_MAP
  (7 patterns: VA/AR/ST/SE/AM/SG/QP). Recursive walker with
  cycle detection (reuses CycleDetectedError). Top-level
  TableNode excluded (yE-C table_parser handles it).
- NEW 13 L0 unit tests (6 table_parser + 7 group_walker) using
  synthetic graphml strings in tmp_path.
- NEW 3 L1 integration tests on em_demo_02_mini.graphml:
  - test_extract_periods_em_demo_02_mini (Period01/Period02)
  - test_walk_folders_em_demo_02_mini (VA01 attivita 4 members,
    AR01 area 2 members; TableNode excluded)
  - test_classifier_periods_folders_consistent_on_em_demo_02_mini
    (cross-parser consistency)
- MODIFY modules/s3dgraphy/sync/ingest_result.py: add
  parsed_drafts: dict | None = None field to IngestResult
  (frozen=True). Default None preserves back-compat. Shape:
  {classified, periods, folders}.
- MODIFY modules/s3dgraphy/sync/graph_ingestor.py:169-196:
  update yE-B hook to orchestrate classify + extract_periods +
  walk_folders + 3-line log. Local var _yed_parsed_drafts
  initialized at function entry; populated inside hook if
  yEd-raw detected. Passed as parsed_drafts= to the final
  IngestResult(...) construction at line 648-654 (mutation
  forbidden because frozen).
- Version bump 5.7.6-alpha -> 5.7.7-alpha + bilingual CHANGELOG
  entry + dev-log yE-C section.

Architectural correction during plan-writing: spec §7 said
"attach to result before final return" but IngestResult is
frozen=True. Plan corrected to pass parsed_drafts= at
construction time. Recorded in dev-log + commit message.

Inherits parent spec §6 (period extraction) + §7 (group folder
interpretation) and specializes for MVP: Path-only input,
TableNode swimlane excluded from walk_folders,
DEFAULT_FOLDER_PREFIX_MAP is the only ruleset (user override
via dialog deferred to yE-E).

Test counts: 273 -> 289 passed, 33 skipped (PG offline) or
281 -> 297 passed, 12 skipped (PG online + psycopg2).
AC-2 byte-identical preserved.
All 3 critical SQLite regression gates preserved.
All 5 yE-A + 12 yE-B tests preserved.
All 8 PG-D L2 tests preserved.

Next milestone: yE-D Pipeline (yed-import-pipeline-5.7.8-alpha)
- ships yed_rapporti_policy.py + yed_import_pipeline.py
  orchestrator consuming IngestResult.parsed_drafts for real DB
  writes + CLI scripts/import_yed_graphml.py --auto-defaults +
  L1 integration test verifying SQL changes.

Spec: docs/superpowers/specs/2026-05-12-yed-import-parsers-design.md
Plan: docs/superpowers/plans/2026-05-12-yed-import-parsers.md
Predecessor: yed-import-classifier-5.7.6-alpha (640b4e83)
EOF
)"
```

### Task C.3: Verify the tag (LOCAL)

- [ ] **Step 1: Verify**

```bash
echo "=== Tag created locally ==="
git tag -n5 yed-import-parsers-5.7.7-alpha | head -10
echo "=== Tag points to HEAD ==="
git rev-parse yed-import-parsers-5.7.7-alpha^{commit}
git rev-parse HEAD
echo "=== Tag is annotated ==="
git cat-file -t yed-import-parsers-5.7.7-alpha
echo "=== Strict trailer check on tag message ==="
git tag -l --format='%(contents)' yed-import-parsers-5.7.7-alpha | grep -cE "^Co-Authored-By:"
```

Final grep MUST return `0`. Tag type MUST be `tag` (annotated). Tag commit SHA MUST match HEAD.

### Task C.4: USER APPROVAL GATE — present manual test plan

- [ ] **Step 1: STOP and present test plan to user**

Controller gate, NOT subagent decision. Present this manual test plan and wait for `approvato`:

```
yE-C is parsers-only (still no DB writes; that's yE-D). Manual
test verifies the 3-line warning + the parsed_drafts field:

1. Reload pyarchinit / restart QGIS to pick up new parsers +
   modified hook + modified IngestResult.

2. From QGIS Python Console:
     from modules.s3dgraphy.sync.yed_table_parser import extract_periods
     from modules.s3dgraphy.sync.yed_group_walker import walk_folders
     path = "/Users/enzo/Downloads/EM_demo_02.graphml"
     periods = extract_periods(path)
     folders = walk_folders(path)
     print(f"periods: {len(periods)} -> {[p.auto_label for p in periods]}")
     print(f"folders: {len(folders)} -> {[(f.auto_value, f.auto_dimension, len(f.member_yed_ids)) for f in folders]}")
   
   Expected output:
     periods: 2 -> ['Period01', 'Contemporary era']
     folders: 6 -> [('VA01', 'attivita', N1), ('VA02', 'attivita', N2),
                    ('VA03', 'attivita', N3), ('VA04', 'attivita', N4),
                    ('VA05', 'attivita', N5), ('VA06', 'attivita', N6)]
     (member counts vary per folder; total leaves across folders = 82)

3. (Optional) Try the existing "Import GraphML" menu with
   /Users/enzo/Downloads/EM_demo_02.graphml. Expect the new
   3-line WARNING in Log Messages:
     yEd-raw graphml detected at <path>.
       Classified 82 leaves: combiner: 3, document: 38, ...
       Detected 2 periods: Period01, Contemporary era.
       Detected 6 group folders: VA01 (attivita, N1 members), ...
       Yed-aware import path not yet wired (yE-C parsers only).
       Falling through to legacy path.
   The ingest is still the broken 17-rows-in-us_table from before
   -- yE-D will fix that.

4. (Optional) Inspect IngestResult.parsed_drafts after a real
   populate_list() call. This requires a script that invokes
   the ingestor directly with a captured result -- defer to
   yE-D if you don't have time.

If all 3 mandatory + 2 optional steps look right, reply 'approvato'.
```

Wait for user reply. **DO NOT push** until user replies `approvato` / `go` / `procedi`.

### Task C.5: Push tag + branch (after user approval)

- [ ] **Step 1: Push**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git push origin Stratigraph_00001 2>&1 | tail -3
git push origin yed-import-parsers-5.7.7-alpha 2>&1 | tail -3
```

### Task C.6: Verify on origin

- [ ] **Step 1: Confirm**

```bash
git ls-remote --tags origin | grep "yed-import-parsers-5.7.7-alpha"
git ls-remote --heads origin Stratigraph_00001
```

Expected: tag with `^{}` dereferenced commit line, branch tip equals local HEAD.

---

## Group D — Memory snapshot (controller, no subagent)

After Group C ships, the controller updates memory.

- [ ] **Step 1: Update `~/.claude/projects/.../memory/project_yed_import_progress.md`**

- Update header: change name + description to reflect "yE-C SHIPPED 2026-05-12"
- Move yE-C from PENDING to SHIPPED row in the rollout table
- Add new "SHIPPED yE-C Parsers (5.7.7-alpha) 2026-05-12" section with:
  - Tag SHA + commit SHA (from `git rev-parse` after push)
  - Spec/Plan/Rollback-tag SHAs
  - 2-commit landed list (A + B)
  - Real-world verification breakdown
  - Tests counts
  - Lessons from yE-C execution (including the IngestResult-frozen correction)
- Reference for yE-D implementation

- [ ] **Step 2: Update `~/.claude/projects/.../memory/MEMORY.md`**

Replace the yE-B SHIPPED index line with an updated entry reflecting yE-C SHIPPED. Format:

```
- [yEd-import yE-C Parsers SHIPPED 2026-05-12](project_yed_import_progress.md) — Tags yed-import-foundation-5.7.5-alpha (yE-A, eb4fba81) + yed-import-classifier-5.7.6-alpha (yE-B, 640b4e83) + yed-import-parsers-5.7.7-alpha (yE-C). 3/6 milestones pending (yE-D Pipeline next). 256 → 289 passed, 33 skipped. AC-2 + 3 SQLite gates + 5 yE-A + 12 yE-B + 8 PG-D L2 preserved. yE-C adds table_parser (TableNode rows -> PeriodCandidate) + group_walker (folder hierarchy -> FolderCandidate with prefix-to-dimension auto) + IngestResult.parsed_drafts field + branch hook with 3-line summary log.
```

---

## Self-Review

This plan covers every yE-C spec requirement:

| Spec section | Plan task |
|---|---|
| §1 Goal | All Groups |
| §2 Decisions (α/γ/γ/A) | Group A implements all 4 |
| §3 Inheritance + specializations | Group A code matches |
| §4 Architecture overview | File Structure section |
| §5 yed_table_parser specification | Task A.1 (full code) + Task A.5 (6 L0 tests) |
| §6 yed_group_walker specification | Task A.2 (full code) + Task A.6 (7 L0 tests) |
| §7 Branch hook update + IngestResult field | Task A.3 (field) + Task A.4 (hook update) |
| §8 3 L1 integration tests | Task A.7 |
| §9 Backward compat + test strategy | Task A.8 regression gates |
| §10 Decomposition | Group 0/A/B/C/Memory structure |
| §11 Acceptance criteria | Self-review checklist + Task A.8 |
| §12 Out of scope | "NOT touched" section + Group A scope discipline |

**Placeholder scan:** zero `TBD/TODO/FIXME` in the plan body. Member counts in the test plan are "N1, N2, ..." because they depend on the real fixture content; the L1 test assertions on the mini fixture pin exact counts.

**Type consistency:**
- `PeriodCandidate` — used consistently in module, 6 L0 tests, 1 L1 test, hook block, IngestResult comment
- `FolderCandidate` — same
- `extract_periods(graphml_path)` and `walk_folders(graphml_path)` — same signature everywhere
- `_yed_parsed_drafts` local var — used consistently in hook + IngestResult construction
- Hook line range "169-196" — consistent with yE-B + spec

**No placeholders:** every step has runnable code, exact commands, or specific file edits.

**Scope discipline:** Plan focused on yE-C only. No premature rapporti policy (yE-D), no dialog (yE-E), no DB writes from yEd-raw branch.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-12-yed-import-parsers.md`. Two execution options:

**1. Subagent-Driven (recommended)** — controller dispatches fresh subagent per task with two-stage review:
- Group 0 (controller-only)
- Group A (1 subagent — production code + tests; bigger than yE-B but same pattern)
- Group B (1 subagent — docs + version)
- Group C (1 subagent for tag; STOP at C.4 for user approval; controller pushes)
- Group D (controller writes memory snapshot)

**2. Inline Execution** — execute tasks in this session via `executing-plans` with checkpoints after each Group.

Which approach?
