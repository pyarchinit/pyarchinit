# yE-A Foundation — yEd-import Detection Hook Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the smallest, foundational milestone of the yEd-aware graphml import feature: a `detect_flavor()` helper that distinguishes pyarchinit-projected from yEd-raw graphmls, plus a no-op branch hook in `GraphIngestor.populate_list()` that will be replaced by real dispatch logic in yE-B+. No user-visible behavior change.

**Architecture:** Pure additive — one new module (`yed_detector.py`) + one new test file + one new yEd-raw fixture + a 7-line if-branch at the top of `populate_list()` that logs a warning and falls through to the existing code. The pyarchinit-projected path stays byte-identically unchanged, so AC-2 + 3 critical SQLite regression gates + 8 PG-D L2 tests all stay green untouched.

**Tech Stack:** Python 3.9+, `lxml.etree.iterparse` (with `xml.etree.iterparse` fallback when lxml unavailable), pytest, SQLAlchemy 2.0+ (already a dep — not touched).

**Spec source of truth:** `docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md` (commit `43fc5cb8`).

**Predecessor tag:** `phase3-pgcompat-consolidation-5.7.4-alpha` (commit `7064b1d1`).

**Target tag:** `yed-import-foundation-5.7.5-alpha`.

**Memory notes to consult before refactoring:**
- `~/.claude/projects/.../memory/feedback_no_claude_coauthor.md` — strict commit-author rule
- `~/.claude/projects/.../memory/project_pg_compat_progress.md` — Phase 3 state + Foundation/PG patterns
- `~/.claude/projects/.../memory/MEMORY.md` — top-level index

**Strict commit-author rule:** never include trailers identifying Claude as a co-author. After each commit run `git log -1 --format=%B HEAD | grep -cE '^Co-Authored-By:'` — must return `0`. **CAUTION:** avoid the literal hyphenated phrase in commit body prose (the regex-anchored check filters it correctly, but unsuspecting `grep -c Co-Authored-By` would not).

---

## Detection logic — design decision (read before Task A.1)

**The detection marker is the presence of ANY `pyarchinit.*` key in the top-level `<key>` declarations of the graphml, NOT specifically `pyarchinit.node_uuid`.**

Evidence from this codebase (verified before writing the plan):

```bash
$ grep -oE '<key[^>]*attr\.name="pyarchinit\.[^"]*"' tests/sync/fixtures/mini_volterra_baseline_ai03.graphml | head
<key for="graph" id="d23" attr.name="pyarchinit.epochs_meta"
<key for="node" id="d0" attr.name="pyarchinit.us"
<key for="node" id="d1" attr.name="pyarchinit.area"
<key for="node" id="d2" attr.name="pyarchinit.sito"
<key for="node" id="d3" attr.name="pyarchinit.unita_tipo"
... (no pyarchinit.node_uuid in this fixture)

$ grep -oE '<key[^>]*attr\.name="pyarchinit\.[^"]*"' /Users/enzo/Downloads/EM_demo_02.graphml
(empty — yEd-raw)
```

The spec §4 says `pyarchinit.node_uuid`, but that specific key may not be emitted on every projected graphml (it's added when `node_uuid` is populated, which depends on Phase 1 migration state). The robust marker is **any `pyarchinit.*` namespaced key**, since the writer always emits at least `pyarchinit.us`, `pyarchinit.area`, `pyarchinit.sito`, etc. on every projected node.

The plan encodes this corrected logic, and the dev-log/changelog entries record this as a deviation-from-spec discovered during plan-writing.

---

## File Structure

### Created

| Path | Responsibility |
|---|---|
| `modules/s3dgraphy/sync/yed_detector.py` | `detect_flavor(graphml_path) -> "pyarchinit-projected" \| "yed-raw"`. O(1) header scan via lxml/xml.etree iterparse. Safe-default `"yed-raw"` on parse error / missing file. |
| `tests/sync/test_yed_detector.py` | 4 L0 tests covering: projected fixture detection, yEd-raw fixture detection, malformed-xml safe default, empty-file safe default. Pure pytest, no Qt, no PG. |
| `tests/sync/fixtures/em_demo_02_mini.graphml` | Minimal yEd-raw fixture (~3-5 KB) for L0 detector tests and reuse in later milestones (yE-B/C/D/E). 1 TableNode + 2 rows + 2 group folders + 6 leaves + 5 edges. |

### Modified

| Path | Why |
|---|---|
| `modules/s3dgraphy/sync/graph_ingestor.py` | Add a 7-line if-branch at the top of `populate_list()`: when `graphml_path is not None` and `detect_flavor()` returns `"yed-raw"`, emit warning log + fall through. yE-B+ will replace the no-op with real dispatch. | ~10 LOC delta |
| `metadata.txt` | Bump `version=5.7.4-alpha` → `version=5.7.5-alpha`. | 1 line |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.5-alpha]` section describing yE-A scope. | ~50 LOC |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Add "yE-A Foundation (5.7.5-alpha)" section. | ~40 LOC |

### Explicitly NOT touched

- The pyarchinit-projected branch of `populate_list()` — stays byte-identically the same
- `_NON_STRAT_TYPES`, `_S3DGRAPHY_TYPE_TO_UNITA_TIPO`, `_resolve_unita_tipo`, `_apply_group_folders_to_sql` — yE-B+ territory
- Any code paths in `graph_projector.py`, `paradata_store.py`, `group_store.py`, `vocab_provider.py`, the dialog code, the SQL queries — all out of yE-A scope
- DB schema — no migrations, no new columns, no new tables
- `requirements.txt` — no new dependencies (lxml already in tree per `_apply_group_folders_to_sql`)

### Total LOC

- Production: ~60 (~50 in `yed_detector.py` + ~10 delta in `graph_ingestor.py`)
- Test: ~80 (`test_yed_detector.py`)
- Fixture: ~120 lines XML (`em_demo_02_mini.graphml`)
- Docs: ~90
- **Grand total: ~350 LOC** (smallest possible milestone — by design)

---

## Test strategy

- **L0 unit (NEW):** `test_yed_detector.py` — 4 cases. Pure pytest, no Qt, no PG dependency. Always runs.
- **L1 SQLite (existing 256):** Stay green. The pyarchinit-projected branch is unchanged.
- **L2 PG (existing 8 from PG-D):** Stay green or skip cleanly. They never touch graphml-import code.
- **L3 regression guards (existing, MUST stay green after Group A):**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v   # AC-2
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py tests/sync/test_round_trip_with_groups.py tests/sync/test_graph_projector_paradata.py -v   # 3 critical SQLite gates
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py tests/sync/test_group_store_pg.py -v   # 8 PG-D L2 (skip cleanly when PG offline)
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no
```

After Group A, ALL of these must PASS (or SKIP for PG L2 when PG offline). If any breaks → STOP and report BLOCKED.

### Decision pinning

| Decision / Acceptance | Pinning test |
|---|---|
| Detection marker = ANY `pyarchinit.*` key (NOT specifically `pyarchinit.node_uuid`) | `test_detect_pyarchinit_projected_via_us_key` in `test_yed_detector.py` |
| Empty/malformed/missing-file → safe `"yed-raw"` default | `test_detect_malformed_falls_back_to_yed_raw` + `test_detect_empty_file_returns_yed_raw` + `test_detect_missing_file_returns_yed_raw` |
| `lxml` graceful degrade | Manual: temporarily uninstall lxml and re-run (or use monkeypatch trick — see Task A.2 step 5) |
| AC-2 byte-identical preserved | Existing `test_ai03_export_byte_identical.py` still passes after `graph_ingestor.py` modification |
| 3 SQLite regression gates preserved | Existing 3 critical tests pass |
| Branch hook is a no-op fall-through | Manual: add a `print()` to the warning log path, run any existing yEd-raw-style test, observe fall-through (or rely on the existing tests staying green — they exercise pyarchinit-projected only, so the new branch never fires for them) |

### Test count progression

- Pre yE-A (post Phase 3 + spec): `256 passed, 33 skipped` (PG offline)
- Post Group A (+ 4 L0 detector tests): `260 passed, 33 skipped`
- Post Group B (docs only): `260 passed, 33 skipped` (unchanged — docs don't add tests)
- Post Group C (tag only): unchanged
- **Final (PG offline):** `260 passed, 33 skipped`
- **Final (PG online + psycopg2):** `268 passed, 12 skipped`

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
- HEAD: `43fc5cb8 spec(yed-import): yEd-aware graphml import design`
- ahead/behind origin: `1\t0` (1 commit ahead — the spec — not yet pushed)

If branch is anything else → **STOP and ask** before proceeding.

- [ ] **Step 2: Verify predecessor tag**

```bash
git tag --list | grep -E "phase3-pgcompat-consolidation-5.7.4-alpha"
```

Expected: `phase3-pgcompat-consolidation-5.7.4-alpha` listed.

- [ ] **Step 3: Capture baselines (regression gates)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py tests/sync/test_round_trip_with_groups.py tests/sync/test_graph_projector_paradata.py -v 2>&1 | tail -10
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py tests/sync/test_group_store_pg.py -v 2>&1 | tail -10
```

Expected:
- Full suite: `256 passed, 33 skipped`
- AC-2: `1 passed`
- round_trip: `1 passed`
- 3 critical gates: `8 passed`
- 8 PG-D L2: `8 skipped` (PG offline — acceptable)

### Task 0.2: Create rollback safety tag

- [ ] **Step 1: Create + push rollback tag**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git tag -a pre-yed-import-foundation -m "Rollback point before yE-A Foundation milestone

Predecessor tag: phase3-pgcompat-consolidation-5.7.4-alpha (7064b1d1)
Spec commit: 43fc5cb8 (local-only at tag time)

If yE-A needs to be reverted, reset hard to this tag."
git push origin pre-yed-import-foundation 2>&1 | tail -3
```

Expected: `* [new tag]         pre-yed-import-foundation -> pre-yed-import-foundation`

---

## Group A — `yed_detector.py` + branch hook + 4 L0 tests + mini fixture

The only production-code Group. ~60 LOC production + ~80 LOC test + ~120 lines fixture XML.

**CRITICAL RULES (surface in subagent prompt):**
- Detection marker: presence of ANY `pyarchinit.<*>` key, NOT specifically `pyarchinit.node_uuid` (verified evidence in §"Detection logic — design decision" above)
- `lxml.etree.iterparse` preferred; `xml.etree.iterparse` fallback wrapped in try/except ImportError
- Detection is O(1) — stop iterating as soon as flavor is known (don't load full file)
- Empty/malformed/missing-file → safe `"yed-raw"` default
- The `populate_list()` modification is **A SINGLE if-branch at the top**, falling through to existing code. AC-2 byte-identical MUST pass after.
- **AC-2 + 3 critical SQLite regression gates + 8 PG-D L2 tests sanity ping IMMEDIATELY after the commit** — if any breaks, STOP and report BLOCKED

### Task A.1: Create the mini yEd-raw fixture

**Files:**
- Create: `tests/sync/fixtures/em_demo_02_mini.graphml`

- [ ] **Step 1: Create the fixture file**

Use the Write tool to create `tests/sync/fixtures/em_demo_02_mini.graphml` with EXACTLY this content (yEd-styled XML, no `pyarchinit.*` keys, ~120 lines):

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:yed="http://www.yworks.com/xml/yed/3" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <!--Created manually as a yEd-raw fixture for yE-A Foundation tests-->
  <key attr.name="description" attr.type="string" for="node" id="d5"/>
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <key for="edge" id="d10" yfiles.type="edgegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="n0" yfiles.foldertype="group">
      <data key="d5"><![CDATA[Archaeological Context]]></data>
      <data key="d6">
        <y:TableNode configuration="YED_TABLE_NODE">
          <y:Geometry height="600.0" width="800.0" x="0.0" y="0.0"/>
          <y:NodeLabel modelName="custom" rotationAngle="270.0">Period01<y:LabelModel><y:RowNodeLabelModel offset="3.0"/></y:LabelModel><y:ModelParameter><y:RowNodeLabelModelParameter horizontalPosition="0.0" id="row_0" inside="true"/></y:ModelParameter></y:NodeLabel>
          <y:NodeLabel modelName="custom" rotationAngle="270.0">Period02<y:LabelModel><y:RowNodeLabelModel offset="3.0"/></y:LabelModel><y:ModelParameter><y:RowNodeLabelModelParameter horizontalPosition="0.0" id="row_1" inside="true"/></y:ModelParameter></y:NodeLabel>
          <y:Table>
            <y:Rows>
              <y:Row id="row_0" height="300.0"/>
              <y:Row id="row_1" height="300.0"/>
            </y:Rows>
          </y:Table>
        </y:TableNode>
      </data>
      <graph edgedefault="directed" id="n0:">
        <node id="n0::n0" yfiles.foldertype="group">
          <data key="d5"><![CDATA[VA01-foundation example]]></data>
          <data key="d6">
            <y:ProxyAutoBoundsNode>
              <y:Realizers active="0">
                <y:GroupNode>
                  <y:NodeLabel>VA01-foundation example</y:NodeLabel>
                </y:GroupNode>
              </y:Realizers>
            </y:ProxyAutoBoundsNode>
          </data>
          <graph edgedefault="directed" id="n0::n0:">
            <node id="n0::n0::n0">
              <data key="d6">
                <y:ShapeNode>
                  <y:Geometry height="40.0" width="80.0" x="50.0" y="100.0"/>
                  <y:NodeLabel>US01</y:NodeLabel>
                </y:ShapeNode>
              </data>
            </node>
            <node id="n0::n0::n1">
              <data key="d6">
                <y:ShapeNode>
                  <y:Geometry height="40.0" width="80.0" x="50.0" y="160.0"/>
                  <y:NodeLabel>US02</y:NodeLabel>
                </y:ShapeNode>
              </data>
            </node>
            <node id="n0::n0::n2">
              <data key="d6">
                <y:ShapeNode>
                  <y:Geometry height="40.0" width="80.0" x="50.0" y="220.0"/>
                  <y:NodeLabel>USV101</y:NodeLabel>
                </y:ShapeNode>
              </data>
            </node>
            <node id="n0::n0::n3">
              <data key="d6">
                <y:ShapeNode>
                  <y:Geometry height="40.0" width="80.0" x="160.0" y="100.0"/>
                  <y:NodeLabel>material</y:NodeLabel>
                </y:ShapeNode>
              </data>
            </node>
          </graph>
        </node>
        <node id="n0::n1" yfiles.foldertype="group">
          <data key="d5"><![CDATA[AR01-area example]]></data>
          <data key="d6">
            <y:ProxyAutoBoundsNode>
              <y:Realizers active="0">
                <y:GroupNode>
                  <y:NodeLabel>AR01-area example</y:NodeLabel>
                </y:GroupNode>
              </y:Realizers>
            </y:ProxyAutoBoundsNode>
          </data>
          <graph edgedefault="directed" id="n0::n1:">
            <node id="n0::n1::n0">
              <data key="d6">
                <y:ShapeNode>
                  <y:Geometry height="40.0" width="80.0" x="300.0" y="400.0"/>
                  <y:NodeLabel>SF105</y:NodeLabel>
                </y:ShapeNode>
              </data>
            </node>
            <node id="n0::n1::n1">
              <data key="d6">
                <y:ShapeNode>
                  <y:Geometry height="40.0" width="80.0" x="300.0" y="460.0"/>
                  <y:NodeLabel>VSF107</y:NodeLabel>
                </y:ShapeNode>
              </data>
            </node>
          </graph>
        </node>
      </graph>
    </node>
    <edge id="e0" source="n0::n0::n0" target="n0::n0::n1"/>
    <edge id="e1" source="n0::n0::n2" target="n0::n0::n0"/>
    <edge id="e2" source="n0::n0" target="n0::n0::n0"/>
    <edge id="e3" source="n0::n0::n1" target="n0::n0"/>
    <edge id="e4" source="n0::n0" target="n0::n1"/>
  </graph>
</graphml>
```

- [ ] **Step 2: Verify fixture parses + has zero pyarchinit keys**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
python3 -c "
from xml.etree.ElementTree import parse
tree = parse('tests/sync/fixtures/em_demo_02_mini.graphml')
root = tree.getroot()
ns = '{http://graphml.graphdrawing.org/xmlns}'
keys = root.findall(f'{ns}key')
pyarch_keys = [k for k in keys if (k.get('attr.name') or '').startswith('pyarchinit.')]
print(f'Total keys: {len(keys)}, pyarchinit.* keys: {len(pyarch_keys)}')
assert len(pyarch_keys) == 0, 'Fixture must have ZERO pyarchinit keys (yEd-raw)'
print('Fixture validation OK — yEd-raw confirmed')
"
```

Expected: `Total keys: 3, pyarchinit.* keys: 0` + `Fixture validation OK — yEd-raw confirmed`.

### Task A.2: Create `yed_detector.py`

**Files:**
- Create: `modules/s3dgraphy/sync/yed_detector.py`

- [ ] **Step 1: Create the module**

Use the Write tool to create `modules/s3dgraphy/sync/yed_detector.py` with EXACTLY this content:

```python
"""yEd-flavor detection for graphml import.

Distinguishes graphmls produced by pyarchinit's own GraphProjector
(`pyarchinit-projected`) from graphmls authored externally in yEd
or other tools (`yed-raw`).

The detection marker is the presence of ANY `pyarchinit.<*>` key in
the top-level `<key>` declarations of the graphml — NOT specifically
`pyarchinit.node_uuid` (that key is conditionally emitted only when
the source DB has node_uuid populated; the robust marker is the
namespace prefix).

O(1) header scan: stops at the first `<graph>` element. Safe-default
to `"yed-raw"` on parse error / missing file / empty file — the
yEd-aware pipeline downstream will surface the problem to the user.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

GraphMLFlavor = Literal["pyarchinit-projected", "yed-raw"]


def detect_flavor(graphml_path: Path | str) -> GraphMLFlavor:
    """Return the graphml flavor based on key declarations.

    Args:
        graphml_path: filesystem path to the .graphml file.

    Returns:
        ``"pyarchinit-projected"`` if any top-level ``<key>`` declares an
        attribute name starting with ``pyarchinit.``; ``"yed-raw"``
        otherwise (including all error cases: file not found,
        unparseable XML, empty content).

    Behaviour:
        - lxml.etree.iterparse preferred for speed
        - xml.etree.iterparse fallback when lxml unavailable
        - stops scanning at the first ``<graph>`` element open event
          (key declarations always precede the graph in valid graphml)
        - O(1) in graphml size — file is not fully loaded
    """
    path = Path(graphml_path)
    if not path.exists():
        return "yed-raw"

    try:
        from lxml import etree as _ET
    except ImportError:
        import xml.etree.ElementTree as _ET  # type: ignore[no-redef]

    GRAPHML_NS = "{http://graphml.graphdrawing.org/xmlns}"

    try:
        # iterparse emits (event, element) tuples; we want both 'start' for the
        # graph element (to know when to stop) and 'end' for key (data fully read).
        context = _ET.iterparse(str(path), events=("start", "end"))
        for event, elem in context:
            tag = elem.tag
            if event == "end" and tag == f"{GRAPHML_NS}key":
                attr_name = elem.get("attr.name") or ""
                if attr_name.startswith("pyarchinit."):
                    return "pyarchinit-projected"
                # Free memory for processed key (large yEd graphs have hundreds)
                elem.clear()
            elif event == "start" and tag == f"{GRAPHML_NS}graph":
                # All <key> declarations are above <graph> in valid graphml.
                # If we got here without finding a pyarchinit.* key, it's yEd-raw.
                return "yed-raw"
    except Exception:
        # Malformed XML, encoding errors, IO errors → safe default
        return "yed-raw"

    # Empty file or file with no <graph> element → safe default
    return "yed-raw"
```

- [ ] **Step 2: Verify the module imports cleanly**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
PYTHONPATH="$PWD" python -c "
from modules.s3dgraphy.sync.yed_detector import detect_flavor, GraphMLFlavor
print('imports OK')
print('detect_flavor:', detect_flavor)
# Smoke test on the new fixture
print('yEd-raw fixture:', detect_flavor('tests/sync/fixtures/em_demo_02_mini.graphml'))
print('pyarchinit-projected baseline:', detect_flavor('tests/sync/fixtures/mini_volterra_baseline_ai03.graphml'))
"
```

Expected:
```
imports OK
detect_flavor: <function detect_flavor at 0x...>
yEd-raw fixture: yed-raw
pyarchinit-projected baseline: pyarchinit-projected
```

If either result is wrong → debug the detection logic before continuing.

### Task A.3: Create `test_yed_detector.py`

**Files:**
- Create: `tests/sync/test_yed_detector.py`

- [ ] **Step 1: Create the test file**

Use the Write tool to create `tests/sync/test_yed_detector.py` with EXACTLY this content:

```python
"""yE-A Foundation: L0 unit tests for detect_flavor().

Verifies the 4 acceptance criteria:
  1. pyarchinit-projected graphml (existing AC-2 baseline fixture)
     is detected as "pyarchinit-projected" via its pyarchinit.us /
     pyarchinit.area / pyarchinit.sito etc. key declarations.
  2. yEd-raw graphml (NEW em_demo_02_mini fixture, zero pyarchinit.*
     keys) is detected as "yed-raw".
  3. Malformed XML returns "yed-raw" (safe default, lets the
     downstream pipeline surface the problem to the user).
  4. Missing file returns "yed-raw" (safe default — no exception
     leaks out of the detector).

The detection marker is presence of ANY pyarchinit.* key, NOT
specifically pyarchinit.node_uuid (that key is conditionally
emitted; the namespace prefix is the robust marker).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.s3dgraphy.sync.yed_detector import detect_flavor

FIXTURES = Path(__file__).parent / "fixtures"


def test_detect_pyarchinit_projected_via_us_key():
    """The AC-2 baseline graphml has 'pyarchinit.us', 'pyarchinit.area',
    'pyarchinit.sito' etc. key declarations → detect_flavor must
    return 'pyarchinit-projected'."""
    baseline = FIXTURES / "mini_volterra_baseline_ai03.graphml"
    assert baseline.exists(), f"Expected fixture at {baseline}"
    assert detect_flavor(baseline) == "pyarchinit-projected"


def test_detect_yed_raw_em_demo_02_mini():
    """The yE-A mini fixture has zero pyarchinit.* keys → 'yed-raw'."""
    fixture = FIXTURES / "em_demo_02_mini.graphml"
    assert fixture.exists(), f"Expected fixture at {fixture}"
    assert detect_flavor(fixture) == "yed-raw"


def test_detect_malformed_falls_back_to_yed_raw(tmp_path):
    """Truncated XML mid-tag → safe default 'yed-raw' (no exception)."""
    bad = tmp_path / "broken.graphml"
    bad.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n'
        '  <key id="d0" attr.nam'  # truncated mid-attribute
    )
    assert detect_flavor(bad) == "yed-raw"


def test_detect_empty_file_returns_yed_raw(tmp_path):
    """Empty file → safe default 'yed-raw'."""
    empty = tmp_path / "empty.graphml"
    empty.write_text("")
    assert detect_flavor(empty) == "yed-raw"


def test_detect_missing_file_returns_yed_raw(tmp_path):
    """Non-existent path → safe default 'yed-raw' (no FileNotFoundError leak)."""
    missing = tmp_path / "does_not_exist.graphml"
    assert not missing.exists()
    assert detect_flavor(missing) == "yed-raw"
```

NOTE: this file has 5 tests, not 4 as the spec/briefing said. The extra `test_detect_missing_file_returns_yed_raw` was added during plan-writing because it's a separate code path (existence check) that deserves a separate test. Total stays small (~80 LOC).

- [ ] **Step 2: Run the 5 new L0 tests**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
PYTHONPATH="$PWD" python -m pytest tests/sync/test_yed_detector.py -v 2>&1 | tail -12
```

Expected: `5 passed`. All 5 tests pass.

### Task A.4: Add the branch hook in `populate_list()`

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_ingestor.py`

- [ ] **Step 1: Locate the insertion point**

Read `populate_list()` definition and find the right insertion point — AFTER the existing prelude (handle resolution, schema check) and BEFORE the existing main per-node loop.

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
grep -n "def populate_list\|def _run\|_resolve_db_handle\|SchemaMismatchError" modules/s3dgraphy/sync/graph_ingestor.py | head -20
```

The current `populate_list()` body delegates to `_run()` after handle resolution and schema check. The detector branch should fire AT THE TOP of `populate_list()`, BEFORE `_run()` is called — so if it's a yEd-raw file, the warning logs and the existing path proceeds.

Recommended location: immediately after the docstring of `populate_list()`, before any handle/schema resolution.

- [ ] **Step 2: Make the edit**

Use the Edit tool to add the branch hook. The exact code to insert:

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
                        "yEd-raw graphml detected at %s — yed-aware "
                        "import path not yet implemented (yE-A "
                        "foundation only). Falling through to legacy "
                        "path. Expect partial/incorrect ingestion.",
                        graphml_path,
                    )
            except Exception:
                # Detection is best-effort; never block the legacy path
                pass
        # ── existing pyarchinit-projected path UNCHANGED below ──
```

Insert this block at the top of the `populate_list()` body (after the docstring, before any existing code).

NOTE: the indentation MUST match the surrounding method body (typically 8 spaces inside a class method). Confirm by reading the existing code first.

- [ ] **Step 3: Syntax check the modified file**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
PYTHONPATH="$PWD" python -c "
import ast
with open('modules/s3dgraphy/sync/graph_ingestor.py') as f:
    ast.parse(f.read())
print('graph_ingestor.py syntax OK')
"
```

Expected: `graph_ingestor.py syntax OK`.

- [ ] **Step 4: Run the full sync+migrations suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `260 passed, 33 skipped` (baseline 256 + 4 new detector tests).

Wait — Task A.3 created 5 detector tests, not 4. Updated expectation: `261 passed, 33 skipped`.

- [ ] **Step 5: Run AC-2 + 3 critical SQLite regression gates**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py tests/sync/test_round_trip_with_groups.py tests/sync/test_graph_projector_paradata.py -v 2>&1 | tail -10
```

Expected: ALL PASS.

- [ ] **Step 6: Run 8 PG-D L2 tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py tests/sync/test_group_store_pg.py -v 2>&1 | tail -10
```

Expected (PG offline): `8 skipped`. If PG online: `8 passed`.

**If any of the regression gates (Steps 5-6) fail → STOP. Do not commit. Report BLOCKED.**

Likely causes if a gate breaks:
- The branch hook accidentally short-circuited the existing pyarchinit-projected path (check indentation, missed the "fall through" semantics, didn't preserve the original code below)
- The new file `yed_detector.py` was imported eagerly at module top of `graph_ingestor.py` causing an import-time side effect (the hook code uses lazy import inside the function — verify this)

### Task A.5: Commit Group A

- [ ] **Step 1: Stage + commit**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git add modules/s3dgraphy/sync/yed_detector.py \
        tests/sync/test_yed_detector.py \
        tests/sync/fixtures/em_demo_02_mini.graphml \
        modules/s3dgraphy/sync/graph_ingestor.py
git commit -m "$(cat <<'EOF'
feat(yE-A): yEd-flavor detector + branch hook (no-op)

Add modules/s3dgraphy/sync/yed_detector.py with the detect_flavor()
helper that distinguishes pyarchinit-projected from yEd-raw
graphmls via O(1) header scan.

Detection marker: presence of ANY pyarchinit.<*> key in top-level
<key> declarations. NOT specifically pyarchinit.node_uuid (the
spec mentioned that key, but evidence in tests/sync/fixtures
shows it is conditionally emitted; the namespace prefix is the
robust marker — pyarchinit.us / pyarchinit.area / pyarchinit.sito
etc. always present on projected graphs).

Implementation:
- lxml.etree.iterparse preferred for speed
- xml.etree.iterparse fallback when lxml unavailable
- stops scanning at the first <graph> element open event
- empty / malformed / missing file all return safe-default yed-raw

Add tests/sync/test_yed_detector.py with 5 L0 tests:
- test_detect_pyarchinit_projected_via_us_key (against AC-2 baseline)
- test_detect_yed_raw_em_demo_02_mini (against new fixture)
- test_detect_malformed_falls_back_to_yed_raw
- test_detect_empty_file_returns_yed_raw
- test_detect_missing_file_returns_yed_raw

Add tests/sync/fixtures/em_demo_02_mini.graphml as the reference
yEd-raw fixture for this and later yE-B/C/D/E milestones. 1
TableNode with 2 rows (Period01/Period02), 2 group folders
(VA01 attivita and AR01 area to cover multiple dimensions),
6 leaves (2 US, 1 USV, 1 SF, 1 VSF, 1 PropertyNode), 5 edges
(2 leaf-to-leaf, 1 folder-to-leaf, 1 leaf-to-folder, 1
folder-to-folder). Zero pyarchinit.* keys.

Modify modules/s3dgraphy/sync/graph_ingestor.py: add a
7-line if-branch at the top of populate_list() that detects
yEd-raw graphmls and logs a warning. Branch is a no-op
placeholder — falls through to the existing pyarchinit-projected
path unchanged. yE-B (Classifier) and later will replace the
no-op with real dispatch to yed_import_pipeline.import_yed_raw().

AC-2 byte-identical preserved (the pyarchinit-projected branch
is unchanged). All 3 critical SQLite regression gates
(round_trip_with_paradata, round_trip_with_groups,
graph_projector_paradata) preserved. All 8 PG-D L2 tests
preserved.

Test counts: 256 -> 261 passed, 33 skipped (PG offline).
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
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `261 passed, 33 skipped`.

## Self-review checklist before reporting back

- [ ] `yed_detector.py` created with `detect_flavor()` + `GraphMLFlavor` type alias
- [ ] Detection marker is ANY `pyarchinit.*` key (not specifically `pyarchinit.node_uuid`) — matches the evidence-corrected design decision
- [ ] lxml preferred + xml.etree fallback via try/except ImportError
- [ ] O(1) early-out at first `<graph>` element
- [ ] Empty/malformed/missing-file all return `"yed-raw"`
- [ ] `test_yed_detector.py` created with 5 L0 tests (added test_detect_missing_file beyond the original 4)
- [ ] `em_demo_02_mini.graphml` fixture created and validated (zero pyarchinit.* keys, parses cleanly)
- [ ] `graph_ingestor.py` modified with single if-branch at top of `populate_list()`, no-op fall-through, lazy import of `detect_flavor`
- [ ] AC-2 byte-identical PASS (test_ai03_export_byte_identical)
- [ ] 3 critical SQLite regression gates PASS
- [ ] 8 PG-D L2 tests SKIP cleanly (or PASS if PG online)
- [ ] Full suite: 261 passed, 33 skipped (PG offline)
- [ ] Strict trailer check returns 0
- [ ] No leftover changes after commit

## Report back format

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- Commit SHA
- Test count (full suite + AC-2 + 3 SQLite gates + 8 PG-D L2)
- Strict trailer check result (must be 0)
- Files changed (should be 4: yed_detector.py + test_yed_detector.py + em_demo_02_mini.graphml + graph_ingestor.py)
- Any concerns

If you find yourself wanting to refactor anything beyond the plan (e.g., add caching to detection, refactor populate_list signature, add more tests beyond the 5), STOP and report DONE_WITH_CONCERNS describing what you wanted to do.

---

## Group B — Docs + version 5.7.5-alpha

### Task B.1: Bump `metadata.txt`

**Files:**
- Modify: `metadata.txt`

- [ ] **Step 1: Bump version**

Use the Edit tool to change the `version=` line from `version=5.7.4-alpha` to `version=5.7.5-alpha`.

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
grep "^version=" metadata.txt
```

Expected after edit: `version=5.7.5-alpha`.

### Task B.2: Insert yE-A dev-log section

**Files:**
- Modify: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

- [ ] **Step 1: Prepend yE-A section**

Use the Edit tool. Find this exact text (the start of the Phase 3 closure section):

```
---

## Phase 3 — Consolidation (5.7.4-alpha) — Phase 3 CLOSURE
```

Replace with:

```
---

## yE-A Foundation — yEd-import detection hook (5.7.5-alpha)

**Tag:** `yed-import-foundation-5.7.5-alpha`
**Date:** 2026-05-12
**Spec:** `docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md`
**Plan:** `docs/superpowers/plans/2026-05-12-yed-import-foundation.md`
**Predecessor:** `phase3-pgcompat-consolidation-5.7.4-alpha` (`7064b1d1`)

### What shipped

- NEW `modules/s3dgraphy/sync/yed_detector.py` with `detect_flavor()`
  helper distinguishing pyarchinit-projected from yEd-raw graphmls
  via O(1) header scan
- NEW `tests/sync/test_yed_detector.py` with 5 L0 tests
- NEW `tests/sync/fixtures/em_demo_02_mini.graphml` reference yEd-raw
  fixture (will be reused by yE-B/C/D/E milestones)
- MODIFY `modules/s3dgraphy/sync/graph_ingestor.py` with a 7-line
  branch hook at top of `populate_list()` that logs a warning on
  yEd-raw detection and falls through to the existing path
  (no-op placeholder, replaced in yE-B+)

### Deviation-from-spec discovered during plan-writing

The spec §4 listed `pyarchinit.node_uuid` as the detection marker,
but evidence from `tests/sync/fixtures/mini_volterra_baseline_ai03.graphml`
showed that key is conditionally emitted (depends on Phase 1
migration state of the source DB). The robust marker is the
**namespace prefix** `pyarchinit.*` — keys like `pyarchinit.us`,
`pyarchinit.area`, `pyarchinit.sito` are always present on
projected graphs. The plan records the corrected logic; future
yE-B/C/D/E milestones inherit the corrected marker.

### Tests

- 5 new L0 detector tests (always run, no Qt, no PG dependency)
- All 256 SQLite tests + AC-2 + 3 critical SQLite regression gates
  preserved
- All 8 PG-D L2 tests preserved (skip cleanly when PG offline)
- Total: 261 passed, 33 skipped (PG offline) or 269 passed, 12
  skipped (PG online with psycopg2)

### Next: yE-B (Classifier — `yed-import-classifier-5.7.6-alpha`)

Will ship `yed_classifier.py` with label-prefix → ClassificationKind
mapping + L0 tests. No UI yet. The branch hook in `populate_list()`
will start dispatching to a stub pipeline that invokes the
classifier and logs results (still no DB writes from the yEd-raw
branch).

---

## Phase 3 — Consolidation (5.7.4-alpha) — Phase 3 CLOSURE
```

### Task B.3: Prepend bilingual CHANGELOG entry

**Files:**
- Modify: `dev_logs/CHANGELOG.md`

- [ ] **Step 1: Prepend entry**

Use the Edit tool. Find this exact text (current top of changelog):

```
## [5.7.4-alpha] - 2026-05-11
```

Replace with:

```
## [5.7.5-alpha] - 2026-05-12

### Italiano

**yE-A Foundation — primo milestone del feature yEd-aware graphml import.**

Apre la rollout in 6 milestone della feature di import yEd-raw (graphml authored in yEd da team archeologici esterni, senza data keys `pyarchinit.*`). yE-A shippa **solo la detection** + un hook no-op nel codice ingestor: nessun cambiamento visibile per l'utente, ma la fondazione per le milestone successive (yE-B Classifier → yE-C Parsers → yE-D Pipeline → yE-E Dialog → yE-Closure).

- **NEW `modules/s3dgraphy/sync/yed_detector.py`**: helper `detect_flavor(graphml_path) -> "pyarchinit-projected" | "yed-raw"`. Header scan O(1) via `lxml.etree.iterparse` (con fallback `xml.etree`), stop al primo `<graph>` element. Default sicuro `"yed-raw"` su file vuoto / malformato / mancante (la pipeline a valle in yE-B+ gestisce il problema).
- **Detection marker**: presenza di QUALSIASI `pyarchinit.<*>` key in top-level `<key>` declarations (NON specificamente `pyarchinit.node_uuid` come scritto nello spec — quella key è emessa condizionalmente, il namespace prefix è il marker robusto, confermato da evidenza sui fixture esistenti).
- **MODIFY `modules/s3dgraphy/sync/graph_ingestor.py`**: aggiunto un if-branch di 7 righe al top di `populate_list()`. Quando rileva yEd-raw, emette un warning log + cade attraverso al path esistente (no-op placeholder). yE-B+ sostituirà il no-op con dispatch reale a `yed_import_pipeline.import_yed_raw()`.
- **NEW fixture `tests/sync/fixtures/em_demo_02_mini.graphml`**: yEd-raw minimale (~120 righe XML, ~4 KB) con 1 TableNode con 2 row Period01/Period02, 2 group folder (VA01 attivita + AR01 area), 6 leaf (2 US + 1 USV + 1 SF + 1 VSF + 1 PropertyNode), 5 edge (2 leaf-to-leaf + 1 folder-to-leaf + 1 leaf-to-folder + 1 folder-to-folder). Sarà riusato in yE-B/C/D/E.
- **NEW 5 test L0** in `tests/sync/test_yed_detector.py`: detection corretta su baseline AC-2 + fixture nuova + malformed XML + file vuoto + file mancante.

**Garanzie regressione (tutte verde post-yE-A):**
- AC-2 byte-identical (`test_ai03_export_byte_identical`)
- 3 critical SQLite gates (`test_round_trip_with_paradata`, `test_round_trip_with_groups`, `test_graph_projector_paradata`)
- 8 PG-D L2 (skip cleanly offline, pass online)
- Pipeline pyarchinit-projected esistente: invariata byte-by-byte

Test count: 256 → 261 passed, 33 skipped (PG offline) o 269 passed, 12 skipped (PG online + psycopg2).

### English

**yE-A Foundation — first milestone of the yEd-aware graphml import feature.**

Opens the 6-milestone rollout of the yEd-raw graphml import feature (graphmls authored in yEd by external archaeological teams, without `pyarchinit.*` data keys). yE-A ships **detection only** + a no-op hook in the ingestor code: no user-visible behavior change, but the foundation for subsequent milestones (yE-B Classifier → yE-C Parsers → yE-D Pipeline → yE-E Dialog → yE-Closure).

- **NEW `modules/s3dgraphy/sync/yed_detector.py`**: helper `detect_flavor(graphml_path) -> "pyarchinit-projected" | "yed-raw"`. O(1) header scan via `lxml.etree.iterparse` (with `xml.etree` fallback), stops at first `<graph>` element. Safe default `"yed-raw"` on empty / malformed / missing file (the downstream pipeline in yE-B+ surfaces the issue).
- **Detection marker**: presence of ANY `pyarchinit.<*>` key in top-level `<key>` declarations (NOT specifically `pyarchinit.node_uuid` as the spec said — that key is conditionally emitted; the namespace prefix is the robust marker, confirmed by evidence on existing fixtures).
- **MODIFY `modules/s3dgraphy/sync/graph_ingestor.py`**: added a 7-line if-branch at the top of `populate_list()`. On yEd-raw detection, emits a warning log + falls through to the existing path (no-op placeholder). yE-B+ will replace the no-op with real dispatch to `yed_import_pipeline.import_yed_raw()`.
- **NEW fixture `tests/sync/fixtures/em_demo_02_mini.graphml`**: minimal yEd-raw (~120 XML lines, ~4 KB) with 1 TableNode + 2 rows Period01/Period02, 2 group folders (VA01 attivita + AR01 area), 6 leaves (2 US + 1 USV + 1 SF + 1 VSF + 1 PropertyNode), 5 edges (2 leaf-to-leaf + 1 folder-to-leaf + 1 leaf-to-folder + 1 folder-to-folder). Will be reused in yE-B/C/D/E.
- **NEW 5 L0 tests** in `tests/sync/test_yed_detector.py`: correct detection on AC-2 baseline + new fixture + malformed XML + empty file + missing file.

**Regression guarantees (all green post-yE-A):**
- AC-2 byte-identical (`test_ai03_export_byte_identical`)
- 3 critical SQLite gates (`test_round_trip_with_paradata`, `test_round_trip_with_groups`, `test_graph_projector_paradata`)
- 8 PG-D L2 (skip cleanly offline, pass online)
- Existing pyarchinit-projected pipeline: byte-by-byte unchanged

Test count: 256 → 261 passed, 33 skipped (PG offline) or 269 passed, 12 skipped (PG online + psycopg2).

---

## [5.7.4-alpha] - 2026-05-11
```

### Task B.4: Commit + final verification

- [ ] **Step 1: Pre-commit verification**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git log --oneline 43fc5cb8..HEAD
git log 43fc5cb8..HEAD --format=%B | grep -cE "^Co-Authored-By:"
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
grep "^version=" metadata.txt
```

Expected:
- 1 commit since spec (`43fc5cb8`): Group A (the production commit)
- Trailer count: `0`
- Test suite: `261 passed, 33 skipped`
- AC-2 PASS
- Version: `5.7.5-alpha`

- [ ] **Step 2: Commit docs + version**

```bash
git add metadata.txt \
        docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md \
        dev_logs/CHANGELOG.md
git commit -m "$(cat <<'EOF'
release(yE-A): docs + version 5.7.5-alpha

yE-A Foundation milestone documentation: bilingual CHANGELOG entry,
dev-log yE-A section, version bump 5.7.4-alpha -> 5.7.5-alpha.

This is the first milestone of the 6-milestone yEd-aware graphml
import rollout. Ships detection-only + no-op branch hook. Real
pipeline dispatch ships in yE-B (Classifier).

The dev-log records the deviation-from-spec discovered during
plan-writing: detection marker is the pyarchinit.* namespace
prefix (any key), not specifically pyarchinit.node_uuid.

Test count: 256 -> 261 passed, 33 skipped (PG offline) or
264 -> 269 passed, 12 skipped (PG online + psycopg2).
AC-2 byte-identical baseline preserved.

Spec: docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md (43fc5cb8)
Plan: docs/superpowers/plans/2026-05-12-yed-import-foundation.md
Predecessor: phase3-pgcompat-consolidation-5.7.4-alpha (7064b1d1)
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
git log --oneline 43fc5cb8..HEAD
git log 43fc5cb8..HEAD --format=%B | grep -cE "^Co-Authored-By:"
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
grep "^version=" metadata.txt
```

Expected:
- 2 commits since spec (`43fc5cb8`): A, B
- Trailer count: `0`
- `261 passed, 33 skipped`
- Version: `5.7.5-alpha`

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
git tag -a yed-import-foundation-5.7.5-alpha -m "$(cat <<'EOF'
yE-A Foundation - yEd-aware graphml import detection hook

First milestone of the 6-milestone yEd-aware graphml import
rollout. Ships detection-only + no-op branch hook. No user-visible
behavior change.

Cumulative deliverables (Groups A-B, 2 commits):

- NEW modules/s3dgraphy/sync/yed_detector.py with detect_flavor()
  helper. O(1) header scan via lxml.etree.iterparse (xml.etree
  fallback). Distinguishes pyarchinit-projected from yEd-raw by
  presence of ANY pyarchinit.* key in top-level <key> declarations.
  Safe default yed-raw on empty / malformed / missing file.
- NEW tests/sync/test_yed_detector.py with 5 L0 tests covering:
  detection of AC-2 baseline pyarchinit-projected fixture, the
  new em_demo_02_mini yEd-raw fixture, malformed XML, empty file,
  missing file.
- NEW tests/sync/fixtures/em_demo_02_mini.graphml: minimal yEd-raw
  reference fixture for this and later yE-B/C/D/E milestones.
  1 TableNode + 2 rows, 2 group folders (VA01 attivita + AR01
  area), 6 leaves, 5 edges. Zero pyarchinit.* keys.
- MODIFY modules/s3dgraphy/sync/graph_ingestor.py with a 7-line
  branch hook at top of populate_list(). On yEd-raw detection,
  emits a warning log + falls through to the existing path
  unchanged. yE-B+ will replace this no-op with real dispatch.
- Version bump 5.7.4-alpha -> 5.7.5-alpha + bilingual CHANGELOG
  entry + dev-log yE-A section.

Deviation-from-spec discovered during plan-writing: detection
marker is the pyarchinit.* namespace prefix (any key), not
specifically pyarchinit.node_uuid. Recorded in dev-log and
CHANGELOG. Future yE-B/C/D/E inherit the corrected marker.

Test counts: 256 -> 261 passed, 33 skipped (PG offline) or
261 -> 269 passed, 12 skipped (PG online + psycopg2).
AC-2 byte-identical preserved.
All 3 critical SQLite regression gates preserved.
All 8 PG-D L2 tests preserved.

Next milestone: yE-B Classifier (yed-import-classifier-5.7.6-alpha)
- ships modules/s3dgraphy/sync/yed_classifier.py with label-prefix
  -> ClassificationKind mapping + L0 tests. No UI. Branch hook
  starts invoking the classifier and logging results.

Spec: docs/superpowers/specs/2026-05-12-yed-aware-graphml-import-design.md
Plan: docs/superpowers/plans/2026-05-12-yed-import-foundation.md
Predecessor: phase3-pgcompat-consolidation-5.7.4-alpha (7064b1d1)
EOF
)"
```

### Task C.3: Verify the tag (LOCAL)

- [ ] **Step 1: Verify**

```bash
echo "=== Tag created locally ==="
git tag -n5 yed-import-foundation-5.7.5-alpha | head -10
echo "=== Tag points to HEAD ==="
git rev-parse yed-import-foundation-5.7.5-alpha^{commit}
git rev-parse HEAD
echo "=== Tag is annotated ==="
git cat-file -t yed-import-foundation-5.7.5-alpha
echo "=== Strict trailer check on tag message ==="
git tag -l --format='%(contents)' yed-import-foundation-5.7.5-alpha | grep -cE "^Co-Authored-By:"
```

The final grep MUST return `0`. The tag must be type `tag` (annotated), not `commit`.

### Task C.4: USER APPROVAL GATE — present test plan

- [ ] **Step 1: STOP and ask the user to approve the push**

This is a controller gate, NOT a subagent decision. Before pushing the tag + branch + spec commit to origin, present a brief manual-test plan to the user (similar to the Consolidation 5.7.4-alpha plan flow). Suggested test plan:

```
yE-A is detection-only with no user-visible UI changes, so the
manual test surface is very small:

1. Reload pyarchinit in QGIS (Plugins → Manage → uncheck/recheck) OR
   restart QGIS to pick up the modified graph_ingestor.py.

2. In QGIS Python Console:
     from modules.s3dgraphy.sync.yed_detector import detect_flavor
     detect_flavor("/path/to/any/pyarchinit-projected.graphml")
       # Expected: "pyarchinit-projected"
     detect_flavor("/Users/enzo/Downloads/EM_demo_02.graphml")
       # Expected: "yed-raw"

3. (Optional) Try the existing "Import GraphML" menu item with a
   pyarchinit-projected file you already use — should behave
   IDENTICALLY to before (the new branch only fires for yEd-raw).

4. (Optional) Try the same menu with /Users/enzo/Downloads/EM_demo_02.graphml
   — should show the new WARNING log in the QGIS Log Messages panel
   ("yEd-raw graphml detected ... falling through to legacy path"),
   then ingest with the same (broken) behavior as before. This is
   the no-op placeholder — yE-B+ will fix.

If all 4 steps look right, reply 'approvato' to push the tag.
If anything is wrong, describe what you saw and I'll fix.
```

Wait for the user's response. **DO NOT push** until the user replies `approvato` / `go` / `procedi`.

### Task C.5: Push tag + branch (after user approval)

- [ ] **Step 1: Push spec commit + Group A + Group B + tag**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git push origin Stratigraph_00001 2>&1 | tail -3
git push origin yed-import-foundation-5.7.5-alpha 2>&1 | tail -3
```

### Task C.6: Verify on origin

- [ ] **Step 1: Confirm push**

```bash
git ls-remote --tags origin | grep "yed-import-foundation-5.7.5-alpha"
git ls-remote --heads origin Stratigraph_00001
```

Expected: tag listed (with `^{}` dereferenced commit line), branch tip equals local HEAD.

---

## Group D — Memory snapshot (controller, no subagent)

After Group C ships, the controller (NOT a subagent) updates memory.

- [ ] **Step 1: Update `project_pg_compat_progress.md` OR create a new memory file for yEd-import**

Since yEd-import is a new project distinct from pg-compat, create:
- File: `~/.claude/projects/-Users-enzo-Library-Application-Support-QGIS-QGIS3-profiles-default-python-plugins-pyarchinit/memory/project_yed_import_progress.md`
- Content: project memory tracking the 6-milestone rollout, with yE-A marked SHIPPED and yE-B-yE-Closure marked PENDING with their target tags + scope summary

- [ ] **Step 2: Add index line to `MEMORY.md`**

Insert at the top of the project list (above the PG-Compat closure line):

```
- [yEd-import Foundation (yE-A) SHIPPED](project_yed_import_progress.md) — Tag `yed-import-foundation-5.7.5-alpha` (commit TBD, tag obj TBD). yEd-flavor detector + no-op branch hook in populate_list(). AC-2 preserved. yE-B Classifier next.
```

(Fill in the commit SHA + tag obj SHA from the actual `git rev-parse` output after the push.)

---

## Self-Review

This plan covers every yE-A spec requirement:

| Spec section | Plan task |
|---|---|
| §3 Architecture overview | Group A creates all the listed new files except those deferred to yE-B+ |
| §4 Detection logic | Task A.2 (yed_detector.py) + Task A.3 (test_yed_detector.py) |
| §10 Backward compat | Task A.4 step 5 (AC-2 + 3 SQLite gates verification) |
| §11 Milestone yE-A scope | Entire Group A |
| §11 versioning 5.7.5-alpha | Task B.1 |
| §13 references to spec/plan | Commit messages + dev-log + CHANGELOG |

**Placeholder scan:** zero `TBD/TODO/FIXME` in the plan body. The "fill in commit SHA after push" in Task D.2 is intentional — those values are post-execution.

**Type consistency:**
- `GraphMLFlavor` = `Literal["pyarchinit-projected", "yed-raw"]` — used consistently in yed_detector.py + tests
- `detect_flavor(graphml_path)` — used consistently in tests + the populate_list() hook
- Fixture filename `em_demo_02_mini.graphml` — used consistently throughout

**No placeholders:** every step has runnable code, exact commands, or specific file edits.

**Scope discipline:** Plan focused on yE-A only. No pre-built classifier, no parsers, no dialog, no pipeline orchestration. Those are explicitly future milestones.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-12-yed-import-foundation.md`. Two execution options:

**1. Subagent-Driven (recommended)** — controller dispatches fresh subagent per task with two-stage review (spec compliance → code quality); recommended batching:
- Group 0 (controller-only, pure git)
- Group A (1 subagent — production code + tests + fixture)
- Group B (1 subagent — docs + version)
- Group C (1 subagent for tag creation; STOP at Task C.4 for user approval; then 1 more action for push)
- Group D (controller writes memory snapshot)

**2. Inline Execution** — execute tasks in this session via `executing-plans` with checkpoints after each Group.

Which approach?
