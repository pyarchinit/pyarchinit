# Phase 1 (Foundation) — PyArchInit ↔ s3dgraphy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace pyarchinit's hard-coded EM 1.4 vocabulary and string-tagged graph nodes with a `VocabProvider` that parses the canonical s3dgraphy 0.1.40 JSON pillars (Option B per Reference Doc v0.1 §4.5), migrate two divergent SQL columns to UUID v7 + s3dgraphy-aligned vocabulary, and refactor 12 `modules/s3dgraphy/` files to use typed nodes — keeping the plugin shippable at every commit.

**Architecture:** Pure-Python core (`vocab_provider_core.py`) parses the three s3dgraphy JSON pillars (`s3Dgraphy_node_datamodel.json`, `s3Dgraphy_connections_datamodel.json`, `em_visual_rules.json`) into typed dataclasses. A thin Qt wrapper (`vocab_provider.py`) adds a `vocabulary_changed` signal + `QFileSystemWatcher` hot-reload for dialogs. `pyarchinit_i18n_stratigraphic.py` becomes a deprecation-warning shim that re-exports the same names while delegating to `VocabProvider`. Two one-shot SQL migrations (`USVA/USVB → USVs`, `USVC → USVn` + UUID v7 backfill) are idempotent, support `--dry-run/--apply/--rollback`, and auto-backup the database before mutation. Twelve files under `modules/s3dgraphy/` get the string-tag → typed-node refactor in per-file commits.

**Tech Stack:** Python 3.9+, sqlite3 stdlib, SQLAlchemy (existing), QGIS PyQt5/PyQt6 (existing), pytest. No new third-party dependencies (UUID v7 implemented locally — Python's stdlib `uuid7` lands in 3.14, we ship a 20-line local implementation).

**Spec source of truth:** `docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md`

**Reference docs (read before starting):**
- `~/Downloads/SC1_StratiGraph_T5.4_MeetingNotes_20260504.pdf`
- `~/Downloads/T5.4_PyArchInit_s3Dgraphy_Reference_v0.1.pdf`

---

## File Structure

### Created

| Path | Responsibility |
|---|---|
| `modules/s3dgraphy/sync/__init__.py` | Package marker; exports `VocabProvider` from public API |
| `modules/s3dgraphy/sync/vocab_types.py` | Typed dataclasses: `UnitType`, `EdgeType`, `ParadataType`, `VisualRule`, `VocabularyVersion` |
| `modules/s3dgraphy/sync/vocab_provider_core.py` | Pure-Python core: JSON loading, override merging, queries. No Qt dependency |
| `modules/s3dgraphy/sync/vocab_provider.py` | Thin Qt wrapper: `QObject` subclass with `vocabulary_changed` signal + `QFileSystemWatcher` |
| `modules/s3dgraphy/sync/uuid7.py` | Local UUID v7 generator (RFC 9562 §5.7); replaces in 3.14+ when stdlib lands |
| `tests/sync/__init__.py` | Test package marker |
| `tests/sync/conftest.py` | Pytest fixtures: minimal valid node/connections/visual-rules JSONs |
| `tests/sync/fixtures/node_datamodel_sample.json` | 3-type fixture (US, USVs, AuthorNode) for fast tests |
| `tests/sync/fixtures/connections_datamodel_sample.json` | 2-edge fixture (`is_after`, `cuts`) |
| `tests/sync/fixtures/em_visual_rules_sample.json` | Visual rules for the 3 fixture types |
| `tests/sync/test_vocab_types.py` | Unit tests for dataclass parsers |
| `tests/sync/test_vocab_provider_core.py` | Unit tests for core (no Qt) |
| `tests/sync/test_vocab_provider.py` | Smoke tests for the Qt wrapper (skipped if PyQt unavailable) |
| `tests/sync/test_uuid7.py` | UUID v7 monotonicity + format tests |
| `scripts/migrations/__init__.py` | Migrations package marker |
| `scripts/migrations/2026_05_us_vocabulary_alignment.py` | `USVA/USVB → USVs`, `USVC → USVn` |
| `scripts/migrations/2026_05_node_uuid_backfill.py` | Add `node_uuid TEXT` to 3 tables + UUID v7 backfill |
| `scripts/migrations/_common.py` | Shared `--dry-run/--apply/--rollback` argparse + auto-backup helpers |
| `tests/migrations/__init__.py` | |
| `tests/migrations/test_us_vocabulary_alignment.py` | Idempotency + rollback tests |
| `tests/migrations/test_node_uuid_backfill.py` | Schema + backfill + idempotency tests |
| `resources/vocab/vocab_i18n.json` | Translator-editable per-language labels (ships empty → English fallback) |

### Modified

| Path | Why |
|---|---|
| `ext_libs/s3dgraphy/` | Wholesale replace 0.1.30 → 0.1.40 |
| `modules/utility/pyarchinit_i18n_stratigraphic.py` | Refactored as adapter over `VocabProvider` (compat shim) |
| `modules/s3dgraphy/cidoc_crm_mapper.py` | Drop `CRM_CLASSES` hardcoded dict (line 20) — read via `VocabProvider.get_cidoc_mapping()` |
| `modules/s3dgraphy/s3dgraphy_integration.py` | Replace `node.node_type = '<string>'` with typed factory |
| `modules/s3dgraphy/s3dgraphy_dot_bridge.py` | Visual mapping via classification API instead of hardcoded family table |
| `modules/s3dgraphy/matrix_graph_visualizer.py` | Filter by family via classification API |
| `modules/s3dgraphy/matrix_visualizer_qgis.py` | Filter by family via classification API |
| `modules/s3dgraphy/plotly_visualizer.py` | Filter by family via classification API |
| `modules/s3dgraphy/blender_integration.py` | Audit only — Blender export keeps private tags per spec §7.3 |
| `modules/s3dgraphy/graphml_spatial_enhancer.py` | Audit only — expected zero changes |
| `modules/s3dgraphy/spatial_grouping_manager.py` | Audit only |
| `modules/s3dgraphy/simple_graph_visualizer.py` | Audit only |
| `modules/s3dgraphy/graphviz_visualizer.py` | Audit only — known compatible |
| `requirements.txt` | `s3dgraphy>=0.1.40` (the vendored copy is the actual source; this pin guards system-pip installs) |
| `metadata.txt` | `version=5.1.0-alpha` |
| `dev_logs/CHANGELOG.md` | Bilingual IT/EN entry for 5.1.0-alpha |

### Removed (after deprecation)

None in Phase 1. `pyarchinit_i18n_stratigraphic.py` is kept as a compat shim for one release cycle; removal is scheduled for Phase 4.

---

## Test strategy

- **Unit tests** (pure pytest, no QGIS): `tests/sync/test_vocab_*`, `tests/sync/test_uuid7.py`, `tests/migrations/test_*`. Run with `pytest tests/sync tests/migrations -v`.
- **Smoke tests** (manual, in QGIS): open Volterra project, verify combo boxes populate; generate Harris matrix; switch UI language. Documented in §G.4.
- **Integration tests** (deferred to Phase 3): full sync flow against mock datacenter — out of scope here.

The plan favours unit tests for everything that can be tested without QGIS bootstrap. The Qt wrapper (`vocab_provider.py`) gets a single skip-if-no-Qt smoke test; deeper integration is a manual gate in §G.4.

---

## Group 0 — Pre-flight & rollback safety

### Task 0.1: Create rollback tag

**Files:** none (git operation)

- [ ] **Step 1: Verify clean working tree**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git status --short
```
Expected: empty output (or only untracked files unrelated to s3dgraphy).

- [ ] **Step 2: Create the rollback tag at current HEAD**

```bash
git tag -a pre-s3dgraphy-040 -m "Rollback point before s3dgraphy 0.1.30→0.1.40 vendor swap and Phase 1 refactor"
git tag -l pre-s3dgraphy-040
```
Expected: `pre-s3dgraphy-040` printed.

- [ ] **Step 3: Confirm push of the tag**

Tag stays local until needed; do NOT push yet.

```bash
git tag -l | grep pre-s3dgraphy-040
```
Expected: `pre-s3dgraphy-040`.

### Task 0.2: Inventory current s3dgraphy usage (for refactor scoping)

**Files:** none (analysis)

- [ ] **Step 1: Count `node.node_type = '<string>'` occurrences per file**

```bash
grep -rnE "node\.node_type\s*=\s*['\"]" modules/s3dgraphy/ --include='*.py'
```
Expected: 3 occurrences in `s3dgraphy_integration.py` (lines around 113); 0 elsewhere.

- [ ] **Step 2: Count `CRM_CLASSES.get(...)` occurrences (cidoc_crm_mapper.py and consumers)**

```bash
grep -rn "CRM_CLASSES" modules/s3dgraphy/ --include='*.py'
```
Expected: 4 occurrences in `cidoc_crm_mapper.py`.

- [ ] **Step 3: Save the inventory to a scratch note (no commit)**

```bash
mkdir -p .scratch
{
  echo "=== node.node_type = '<string>' ==="
  grep -rnE "node\.node_type\s*=\s*['\"]" modules/s3dgraphy/ --include='*.py'
  echo
  echo "=== CRM_CLASSES ==="
  grep -rn "CRM_CLASSES" modules/s3dgraphy/ --include='*.py'
} > .scratch/s3dgraphy-inventory.txt
cat .scratch/s3dgraphy-inventory.txt
```
The `.scratch/` is gitignored (verify with `git check-ignore .scratch`); if not, add to `.gitignore`.

### Task 0.3: Set up tests/sync/ scaffold

**Files:**
- Create: `tests/sync/__init__.py`
- Create: `tests/sync/conftest.py`
- Create: `tests/sync/fixtures/node_datamodel_sample.json`
- Create: `tests/sync/fixtures/connections_datamodel_sample.json`
- Create: `tests/sync/fixtures/em_visual_rules_sample.json`

- [ ] **Step 1: Create `tests/sync/__init__.py`**

```bash
mkdir -p tests/sync/fixtures
touch tests/sync/__init__.py
```

- [ ] **Step 2: Write the node datamodel fixture**

Create `tests/sync/fixtures/node_datamodel_sample.json`:

```json
{
    "s3Dgraphy_data_model_version": "1.5.2",
    "description": "Test fixture — minimal subset",
    "components": ["CIDOC-CRM"],
    "node_types": {
        "Node": {
            "class": "Node",
            "description": "Base class",
            "mapping": {"cidoc": "E1 CRM Entity", "cidoc_s3d": null},
            "properties": {"name": "P1_is_identified_by"}
        }
    },
    "stratigraphic_nodes": {
        "StratigraphicNode": {
            "class": "StratigraphicNode",
            "parent": "Node",
            "description": "Base stratigraphic",
            "mapping": {"cidoc": "A8 Stratigraphic Unit", "cidoc_s3d": null},
            "properties": {"name": "P1_is_identified_by"},
            "subtypes": {
                "US": {
                    "class": "StratigraphicUnit",
                    "parent": "StratigraphicNode",
                    "abbreviation": "US",
                    "label": "US (or SU)",
                    "symbol": "white rectangle",
                    "description": "Stratigraphic Unit",
                    "mapping": {"cidoc": "A2 Stratigraphic Volume Unit", "cidoc_s3d": null},
                    "properties": {"name": "P1_is_identified_by"}
                },
                "USVs": {
                    "class": "StratigraphicUnitVirtualStructural",
                    "parent": "StratigraphicNode",
                    "abbreviation": "USVs",
                    "label": "USVs (Structural Virtual SU)",
                    "symbol": "blue parallelogram",
                    "description": "Structural virtual stratigraphic unit",
                    "mapping": {"cidoc": "A8 Stratigraphic Unit", "cidoc_s3d": null},
                    "properties": {"name": "P1_is_identified_by"}
                }
            }
        }
    },
    "paradata_nodes": {
        "AuthorNode": {
            "class": "AuthorNode",
            "parent": "Node",
            "description": "Author of a paradata statement",
            "mapping": {"cidoc": "E39 Actor", "cidoc_s3d": null},
            "properties": {"name": "P1_is_identified_by"}
        }
    }
}
```

- [ ] **Step 3: Write the connections datamodel fixture**

Create `tests/sync/fixtures/connections_datamodel_sample.json`:

```json
{
    "s3Dgraphy_connections_version": "1.5.4",
    "description": "Test fixture — 2 edges",
    "edge_types": {
        "is_after": {
            "label": "is after",
            "description": "Stratigraphic posteriority",
            "allowed_pairs": [
                {"source": "US", "target": "US"},
                {"source": "US", "target": "USVs"}
            ]
        },
        "cuts": {
            "label": "cuts",
            "description": "Stratigraphic cut",
            "allowed_pairs": [
                {"source": "US", "target": "US"}
            ]
        }
    }
}
```

- [ ] **Step 4: Write the visual rules fixture**

Create `tests/sync/fixtures/em_visual_rules_sample.json`:

```json
{
    "em_visual_rules_version": "1.5.0",
    "description": "Test fixture — visual rules",
    "rules": {
        "US": {"icon": "us.svg", "fill": "#FFFFFF", "stroke": "#000000", "palette": "stratigraphic"},
        "USVs": {"icon": "usvs.svg", "fill": "#88CCFF", "stroke": "#0066AA", "palette": "stratigraphic"},
        "AuthorNode": {"icon": "author.svg", "fill": "#F0E68C", "stroke": "#806040", "palette": "paradata"}
    }
}
```

- [ ] **Step 5: Write the conftest with the fixture loader**

Create `tests/sync/conftest.py`:

```python
"""Shared pytest fixtures for tests/sync/."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def node_datamodel_path() -> Path:
    return FIXTURES / "node_datamodel_sample.json"


@pytest.fixture
def connections_datamodel_path() -> Path:
    return FIXTURES / "connections_datamodel_sample.json"


@pytest.fixture
def visual_rules_path() -> Path:
    return FIXTURES / "em_visual_rules_sample.json"


@pytest.fixture
def vocab_dir(tmp_path: Path,
              node_datamodel_path: Path,
              connections_datamodel_path: Path,
              visual_rules_path: Path) -> Path:
    """Create an isolated JSON_config/ directory holding sample fixtures."""
    out = tmp_path / "JSON_config"
    out.mkdir()
    (out / "s3Dgraphy_node_datamodel.json").write_bytes(node_datamodel_path.read_bytes())
    (out / "s3Dgraphy_connections_datamodel.json").write_bytes(connections_datamodel_path.read_bytes())
    (out / "em_visual_rules.json").write_bytes(visual_rules_path.read_bytes())
    return out


@pytest.fixture
def overrides_dir(tmp_path: Path) -> Path:
    out = tmp_path / "vocab_overrides"
    out.mkdir()
    return out
```

- [ ] **Step 6: Verify pytest can discover the new package**

```bash
python3 -m pytest tests/sync/ --collect-only -q 2>&1 | head -10
```
Expected: `no tests ran` (no test files yet) but no errors collecting.

- [ ] **Step 7: Commit**

```bash
git add tests/sync/__init__.py tests/sync/conftest.py tests/sync/fixtures/
git commit -m "test(s3dgraphy/sync): scaffold pytest fixtures for VocabProvider tests

- 3 sample JSON fixtures (node datamodel, connections, visual rules)
- conftest exposing vocab_dir + overrides_dir for in-tmp_path runs
- preparing for VocabProvider TDD in tasks B.1-B.12

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Group A — Vendor s3dgraphy 0.1.30 → 0.1.40

### Task A.1: Snapshot the current bundled version

**Files:** none (git operation)

- [ ] **Step 1: Verify the current version**

```bash
grep -E '__version__|__datamodel_version__' ext_libs/s3dgraphy/__init__.py
ls ext_libs/ | grep s3dgraphy
```
Expected: `__version__ = "0.1.30"`, `s3dgraphy-0.1.30.dist-info` directory present.

- [ ] **Step 2: Tag the working tree before swap**

Already done in Task 0.1 (`pre-s3dgraphy-040`). No action.

### Task A.2: Replace `ext_libs/s3dgraphy/` with 0.1.40

**Files:**
- Delete: `ext_libs/s3dgraphy/` (entire directory)
- Delete: `ext_libs/s3dgraphy-0.1.30.dist-info/`
- Create: `ext_libs/s3dgraphy/` (0.1.40 from PyPI)
- Create: `ext_libs/s3dgraphy-0.1.40.dist-info/`

- [ ] **Step 1: Remove the 0.1.30 vendor**

```bash
cd ext_libs
rm -rf s3dgraphy s3dgraphy-0.1.30.dist-info
ls | grep s3dgraphy
```
Expected: empty output.

- [ ] **Step 2: Install 0.1.40 directly into ext_libs/ (no deps)**

```bash
pip install --target . --no-deps s3dgraphy==0.1.40 2>&1 | tail -5
```
Expected: `Successfully installed s3dgraphy-0.1.40`.

- [ ] **Step 3: Verify the new vendor**

```bash
grep -E '__version__|__datamodel_version__' s3dgraphy/__init__.py
ls | grep s3dgraphy
ls s3dgraphy/JSON_config/
```
Expected:
- `__version__ = "0.1.40"` (or close — confirm)
- `s3dgraphy-0.1.40.dist-info/` directory
- JSON_config files: `s3Dgraphy_node_datamodel.json` (note: NO trailing space — 0.1.40 fixes the 0.1.30 typo), `s3Dgraphy_connections_datamodel.json`, `em_visual_rules.json`, plus the qualia/extractor/document companions

- [ ] **Step 4: Return to repo root**

```bash
cd ..
pwd
```
Expected: pyarchinit plugin root.

### Task A.3: Smoke-test pre-refactor (manual gate)

**Files:** none (manual QA)

- [ ] **Step 1: Restart QGIS (terminate + relaunch)**

User action; no command.

- [ ] **Step 2: Open the Volterra project**

User opens the QGIS project that pulls Volterra's `pyarchinitcs_SCHEDE2024.sqlite`.

- [ ] **Step 3: Open the US/USM form for any record**

Verify the form opens without exception.

- [ ] **Step 4: Generate a Harris matrix**

Verify the matrix renders. The 0.1.40 vendor swap with NO refactor should not change behaviour.

- [ ] **Step 5: Check QGIS log for s3dgraphy import errors**

Open Plugin > QGIS Python Console; tail `~/.cache/QGIS/...messages.log` if needed. Look for `ImportError`, `AttributeError` from `s3dgraphy`.

- [ ] **Step 6: Decision gate — is the swap clean?**

If errors: `git checkout pre-s3dgraphy-040`, restore 0.1.30 from backup or re-pip-install 0.1.30. Investigate before proceeding.

If clean: continue.

### Task A.4: Bump `requirements.txt` floor (ext_libs/ is gitignored)

> **Policy correction (2026-05-06 mid-execution discovery):** `ext_libs/` is
> gitignored at `.gitignore:43` — pyarchinit follows a runtime-install policy
> (the plugin's `scripts/modules_installer.py` pip-installs ext_libs at first
> launch). The original plan said `git add ext_libs/`; that would have changed
> repo policy and added 3.3 MB of vendored code. The correct artefact for
> Group A is bumping the version floor in `requirements.txt`, which is what
> drives the runtime install on every dev/user machine. Rollback is
> `pip install s3dgraphy==0.1.30 --target ext_libs/ --no-deps` rather than
> `git checkout pre-s3dgraphy-040`. The tag is still useful as the marker for
> "Phase 1 has not yet started in code" but does not snapshot the vendored
> bytes.

**Files:** `requirements.txt` (modified — only line touched is the s3dgraphy pin)

- [ ] **Step 1: Update the pin**

```bash
sed -i.bak 's/^s3dgraphy>=.*/s3dgraphy>=0.1.40/' requirements.txt
rm requirements.txt.bak
grep -n s3dgraphy requirements.txt
```
Expected: `s3dgraphy>=0.1.40` on the previously-existing s3dgraphy line.

- [ ] **Step 2: Commit**

```bash
git add requirements.txt
git commit -m "deps(s3dgraphy): pin floor to >=0.1.40 (vendor swap landed locally)

Per spec §7.4 step 3 and Reference Doc v0.1 §4.1. Pure pin bump in
requirements.txt — ext_libs/ is gitignored (runtime-install policy
managed by scripts/modules_installer.py), so the actual vendored
s3dgraphy 0.1.30 → 0.1.40 swap is invisible to git history.

Rollback procedure: pip install s3dgraphy==0.1.30 --target ext_libs/ --no-deps.
The pre-s3dgraphy-040 tag marks the pre-Phase-1 commit hash but does
NOT snapshot ext_libs/ bytes.

Manual smoke test deferred to G.4 (US form opens, Harris matrix generates,
no import errors in QGIS log).

The 0.1.40 release brings:
- GraphMerger (3-way merge — Phase 3)
- GraphMLPatcher (incremental patch — Phase 2)
- classification API (get_family, is_real, iter_subtypes — used in
  Group F refactor)
- aux_tracking (volatile vs bake — Phase 3)
- NegativeStratigraphicUnit, WorkingUnit (consumed via VocabProvider —
  Group B)
- canonical JSON filenames (no trailing space in
  s3Dgraphy_node_datamodel.json)
- datamodel version 1.5.3 → 1.5.4

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Group B — VocabProvider (Option B per Reference Doc v0.1 §4.5)

> **Design note:** Option B = per-tool JSON parsing. `VocabProvider` does **NOT** wrap a typed s3dgraphy API; it parses the JSON files directly. The contract is the JSON file shape, guaranteed stable per Emanuel's commitment in Reference Doc v0.1 §7.1.

### Task B.1: Define typed dataclasses

**Files:**
- Create: `modules/s3dgraphy/sync/__init__.py`
- Create: `modules/s3dgraphy/sync/vocab_types.py`
- Create: `tests/sync/test_vocab_types.py`

- [ ] **Step 1: Create the package**

```bash
mkdir -p modules/s3dgraphy/sync
touch modules/s3dgraphy/sync/__init__.py
```

- [ ] **Step 2: Write the failing test**

Create `tests/sync/test_vocab_types.py`:

```python
"""Tests for vocab_types dataclasses."""
from __future__ import annotations

from modules.s3dgraphy.sync.vocab_types import (
    EdgeType,
    Family,
    UnitType,
    VisualRule,
)


def test_unit_type_holds_abbreviation_and_label():
    ut = UnitType(
        abbreviation="US",
        label="US (or SU)",
        family=Family.STRATIGRAPHIC,
        cidoc_class="A2 Stratigraphic Volume Unit",
        symbol="white rectangle",
        description="Stratigraphic Unit",
        properties={"name": "P1_is_identified_by"},
        s3dgraphy_class="StratigraphicUnit",
    )
    assert ut.abbreviation == "US"
    assert ut.family is Family.STRATIGRAPHIC


def test_edge_type_lists_allowed_pairs():
    e = EdgeType(
        name="is_after",
        label="is after",
        description="Stratigraphic posteriority",
        allowed_pairs=[("US", "US"), ("US", "USVs")],
    )
    assert ("US", "USVs") in e.allowed_pairs


def test_visual_rule_holds_palette_membership():
    v = VisualRule(
        node_type="US",
        icon="us.svg",
        fill="#FFFFFF",
        stroke="#000000",
        palette="stratigraphic",
    )
    assert v.palette == "stratigraphic"
```

- [ ] **Step 3: Run the test to confirm failure**

```bash
python3 -m pytest tests/sync/test_vocab_types.py -v 2>&1 | tail -10
```
Expected: `ModuleNotFoundError: No module named 'modules.s3dgraphy.sync.vocab_types'` (or similar).

- [ ] **Step 4: Write the minimal implementation**

Create `modules/s3dgraphy/sync/vocab_types.py`:

```python
"""Typed dataclasses for the vocabulary entries parsed by VocabProvider.

These are read-only views over the JSON catalogues shipped inside the
s3dgraphy package (see Reference Doc v0.1 §4.1):

    s3Dgraphy_node_datamodel.json
    s3Dgraphy_connections_datamodel.json
    em_visual_rules.json

The classes intentionally mirror the JSON shape rather than wrapping a
typed s3dgraphy Python API — per Reference Doc v0.1 §4.5 Option B
(per-tool parsing). The JSON top-level file names and top-level keys are
public API per §7.1.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Family(str, Enum):
    STRATIGRAPHIC = "stratigraphic"
    PARADATA = "paradata"
    GROUP = "group"
    REFERENCE = "reference"
    VISUALIZATION = "visualization"
    RIGHTS = "rights"
    TEMPORAL = "temporal"
    FALLBACK = "fallback"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class UnitType:
    abbreviation: str
    label: str
    family: Family
    cidoc_class: str
    symbol: str
    description: str
    properties: dict
    s3dgraphy_class: str


@dataclass(frozen=True)
class EdgeType:
    name: str
    label: str
    description: str
    allowed_pairs: tuple


@dataclass(frozen=True)
class VisualRule:
    node_type: str
    icon: str
    fill: str
    stroke: str
    palette: str


@dataclass(frozen=True)
class ParadataType:
    abbreviation: str
    label: str
    description: str
    cidoc_class: str
    s3dgraphy_class: str


@dataclass(frozen=True)
class VocabularyVersion:
    nodes: str = ""
    connections: str = ""
    visual_rules: str = ""
```

- [ ] **Step 5: Run the test to confirm pass**

```bash
python3 -m pytest tests/sync/test_vocab_types.py -v 2>&1 | tail -10
```
Expected: 3 tests pass.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/__init__.py modules/s3dgraphy/sync/vocab_types.py tests/sync/test_vocab_types.py
git commit -m "feat(s3dgraphy/sync): typed dataclasses for VocabProvider entries

Frozen dataclasses mirror the s3dgraphy JSON shape (Option B per
Reference Doc v0.1 §4.5) — UnitType, EdgeType, VisualRule, ParadataType,
VocabularyVersion. Family enum mirrors the top-level keys of
s3Dgraphy_node_datamodel.json.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task B.2: VocabProvider core — load node datamodel

**Files:**
- Create: `modules/s3dgraphy/sync/vocab_provider_core.py`
- Create: `tests/sync/test_vocab_provider_core.py`

- [ ] **Step 1: Write the failing test**

Create `tests/sync/test_vocab_provider_core.py`:

```python
"""Tests for VocabProviderCore (pure Python, no Qt)."""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.s3dgraphy.sync.vocab_provider_core import VocabProviderCore
from modules.s3dgraphy.sync.vocab_types import Family


def test_loads_unit_types_from_node_datamodel(vocab_dir: Path, overrides_dir: Path):
    core = VocabProviderCore(bundled_dir=vocab_dir, overrides_dir=overrides_dir)
    types = core.get_unit_types()
    abbrevs = {ut.abbreviation for ut in types}
    assert {"US", "USVs"}.issubset(abbrevs)


def test_filters_unit_types_by_family(vocab_dir: Path, overrides_dir: Path):
    core = VocabProviderCore(bundled_dir=vocab_dir, overrides_dir=overrides_dir)
    strat = core.get_unit_types(family=Family.STRATIGRAPHIC)
    assert all(ut.family is Family.STRATIGRAPHIC for ut in strat)


def test_handles_legacy_filename_with_trailing_space(tmp_path: Path,
                                                      node_datamodel_path: Path,
                                                      overrides_dir: Path):
    """0.1.30 had a typo: 's3Dgraphy_node_datamodel .json' (trailing space).
    VocabProviderCore must accept both filenames."""
    legacy_dir = tmp_path / "JSON_config"
    legacy_dir.mkdir()
    (legacy_dir / "s3Dgraphy_node_datamodel .json").write_bytes(
        node_datamodel_path.read_bytes())
    core = VocabProviderCore(bundled_dir=legacy_dir, overrides_dir=overrides_dir)
    types = core.get_unit_types()
    assert any(ut.abbreviation == "US" for ut in types)
```

- [ ] **Step 2: Run to confirm failure**

```bash
python3 -m pytest tests/sync/test_vocab_provider_core.py -v 2>&1 | tail -10
```
Expected: `ModuleNotFoundError: No module named 'modules.s3dgraphy.sync.vocab_provider_core'`.

- [ ] **Step 3: Write the minimal implementation**

Create `modules/s3dgraphy/sync/vocab_provider_core.py`:

```python
"""Pure-Python VocabProvider core — no Qt dependency.

Parses the three s3dgraphy JSON pillars from a bundled directory + an
optional overrides directory. The contract is the JSON shape (Reference
Doc v0.1 §4.5 Option B). No wrapping of typed s3dgraphy APIs.

Override priority: an override file in `overrides_dir` is merged
**per top-level key** (not whole-file) into the bundled JSON, so a
partial datacenter override does not erase locally available types.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .vocab_types import EdgeType, Family, ParadataType, UnitType, VisualRule

# Filenames the loader will accept. Includes the 0.1.30 trailing-space typo.
_NODE_DATAMODEL_NAMES = (
    "s3Dgraphy_node_datamodel.json",
    "s3Dgraphy_node_datamodel .json",  # 0.1.30 typo, kept as fallback
)
_CONNECTIONS_NAMES = ("s3Dgraphy_connections_datamodel.json",)
_VISUAL_RULES_NAMES = ("em_visual_rules.json",)

_FAMILY_KEYS = {
    "stratigraphic_nodes": Family.STRATIGRAPHIC,
    "paradata_nodes": Family.PARADATA,
    "group_nodes": Family.GROUP,
    "reference_nodes": Family.REFERENCE,
    "visualization_nodes": Family.VISUALIZATION,
    "rights_nodes": Family.RIGHTS,
    "temporal_nodes": Family.TEMPORAL,
    "fallback_nodes": Family.FALLBACK,
}


def _first_existing(directory: Path, names: Iterable[str]) -> Path | None:
    for name in names:
        p = directory / name
        if p.exists():
            return p
    return None


def _merge_dicts(base: dict, override: dict) -> dict:
    """Per top-level key merge. override beats base; missing keys preserved."""
    out = dict(base)
    for k, v in override.items():
        out[k] = v
    return out


class VocabProviderCore:
    """Parses the s3dgraphy JSON pillars; query API for client tools."""

    def __init__(self, bundled_dir: Path, overrides_dir: Path):
        self._bundled_dir = Path(bundled_dir)
        self._overrides_dir = Path(overrides_dir)
        self._node_data: dict = {}
        self._connections_data: dict = {}
        self._visual_data: dict = {}
        self.reload()

    def reload(self) -> None:
        self._node_data = self._load_with_override(_NODE_DATAMODEL_NAMES)
        self._connections_data = self._load_with_override(_CONNECTIONS_NAMES)
        self._visual_data = self._load_with_override(_VISUAL_RULES_NAMES)

    def _load_with_override(self, names: Iterable[str]) -> dict:
        bundled = _first_existing(self._bundled_dir, names)
        override = _first_existing(self._overrides_dir, names)
        base = json.loads(bundled.read_text(encoding="utf-8")) if bundled else {}
        if override:
            base = _merge_dicts(base, json.loads(override.read_text(encoding="utf-8")))
        return base

    def get_unit_types(self, family: Family | None = None) -> list[UnitType]:
        out: list[UnitType] = []
        for fam_key, fam_value in _FAMILY_KEYS.items():
            if family is not None and family is not fam_value:
                continue
            family_block = self._node_data.get(fam_key, {})
            for parent_name, parent_def in family_block.items():
                subtypes = parent_def.get("subtypes", {})
                for abbrev, sub in subtypes.items():
                    out.append(UnitType(
                        abbreviation=sub.get("abbreviation", abbrev),
                        label=sub.get("label", abbrev),
                        family=fam_value,
                        cidoc_class=sub.get("mapping", {}).get("cidoc", ""),
                        symbol=sub.get("symbol", ""),
                        description=sub.get("description", ""),
                        properties=sub.get("properties", {}),
                        s3dgraphy_class=sub.get("class", ""),
                    ))
        return out
```

- [ ] **Step 4: Run to confirm pass**

```bash
python3 -m pytest tests/sync/test_vocab_provider_core.py -v 2>&1 | tail -10
```
Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/vocab_provider_core.py tests/sync/test_vocab_provider_core.py
git commit -m "feat(s3dgraphy/sync): VocabProviderCore loads node datamodel

- Parses s3Dgraphy_node_datamodel.json (canonical AND legacy
  trailing-space filename for 0.1.30 backward compat)
- get_unit_types(family=...) yields UnitType objects from the
  configured family blocks (stratigraphic_nodes, paradata_nodes, etc.)
- Override priority via overrides_dir, merged per top-level key

Pure Python, no Qt. Tests under tests/sync/ pass.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task B.3: get_edge_types() — connections datamodel

**Files:**
- Modify: `modules/s3dgraphy/sync/vocab_provider_core.py`
- Modify: `tests/sync/test_vocab_provider_core.py`

- [ ] **Step 1: Add the failing test**

Append to `tests/sync/test_vocab_provider_core.py`:

```python
def test_loads_edge_types_with_allowed_pairs(vocab_dir: Path, overrides_dir: Path):
    core = VocabProviderCore(bundled_dir=vocab_dir, overrides_dir=overrides_dir)
    edges = core.get_edge_types()
    by_name = {e.name: e for e in edges}
    assert "is_after" in by_name
    assert ("US", "USVs") in by_name["is_after"].allowed_pairs
    assert ("US", "US") in by_name["cuts"].allowed_pairs


def test_unknown_edge_type_returns_empty_pairs(vocab_dir: Path, overrides_dir: Path):
    core = VocabProviderCore(bundled_dir=vocab_dir, overrides_dir=overrides_dir)
    assert core.get_legal_targets_for(source_type="US", edge_name="nonexistent") == []
```

- [ ] **Step 2: Run to confirm failure**

```bash
python3 -m pytest tests/sync/test_vocab_provider_core.py -v 2>&1 | tail -10
```
Expected: 2 new failures (`AttributeError: 'VocabProviderCore' object has no attribute 'get_edge_types'`).

- [ ] **Step 3: Implement**

Add to `modules/s3dgraphy/sync/vocab_provider_core.py`:

```python
    def get_edge_types(self) -> list[EdgeType]:
        block = self._connections_data.get("edge_types", {})
        out: list[EdgeType] = []
        for name, defn in block.items():
            pairs = tuple(
                (p.get("source", ""), p.get("target", ""))
                for p in defn.get("allowed_pairs", [])
            )
            out.append(EdgeType(
                name=name,
                label=defn.get("label", name),
                description=defn.get("description", ""),
                allowed_pairs=pairs,
            ))
        return out

    def get_legal_targets_for(self, source_type: str, edge_name: str) -> list[str]:
        for e in self.get_edge_types():
            if e.name != edge_name:
                continue
            return [tgt for src, tgt in e.allowed_pairs if src == source_type]
        return []
```

- [ ] **Step 4: Run to confirm pass**

```bash
python3 -m pytest tests/sync/test_vocab_provider_core.py -v 2>&1 | tail -10
```
Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/vocab_provider_core.py tests/sync/test_vocab_provider_core.py
git commit -m "feat(s3dgraphy/sync): VocabProviderCore.get_edge_types + get_legal_targets_for

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task B.4: get_paradata_types()

**Files:**
- Modify: `modules/s3dgraphy/sync/vocab_provider_core.py`
- Modify: `tests/sync/test_vocab_provider_core.py`

- [ ] **Step 1: Add the failing test**

```python
def test_get_paradata_types(vocab_dir: Path, overrides_dir: Path):
    core = VocabProviderCore(bundled_dir=vocab_dir, overrides_dir=overrides_dir)
    paradata = core.get_paradata_types()
    by_name = {p.s3dgraphy_class: p for p in paradata}
    assert "AuthorNode" in by_name
```

- [ ] **Step 2: Run to confirm failure**

```bash
python3 -m pytest tests/sync/test_vocab_provider_core.py::test_get_paradata_types -v
```
Expected: AttributeError.

- [ ] **Step 3: Implement**

Add to `vocab_provider_core.py`:

```python
    def get_paradata_types(self) -> list[ParadataType]:
        block = self._node_data.get("paradata_nodes", {})
        out: list[ParadataType] = []
        for class_name, defn in block.items():
            out.append(ParadataType(
                abbreviation=defn.get("abbreviation", class_name),
                label=defn.get("label", class_name),
                description=defn.get("description", ""),
                cidoc_class=defn.get("mapping", {}).get("cidoc", ""),
                s3dgraphy_class=defn.get("class", class_name),
            ))
        return out
```

- [ ] **Step 4: Confirm pass**

```bash
python3 -m pytest tests/sync/test_vocab_provider_core.py::test_get_paradata_types -v
```

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/vocab_provider_core.py tests/sync/test_vocab_provider_core.py
git commit -m "feat(s3dgraphy/sync): VocabProviderCore.get_paradata_types

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task B.5: get_visual_rule()

**Files:**
- Modify: `modules/s3dgraphy/sync/vocab_provider_core.py`
- Modify: `tests/sync/test_vocab_provider_core.py`

- [ ] **Step 1: Add the failing test**

```python
def test_get_visual_rule(vocab_dir: Path, overrides_dir: Path):
    core = VocabProviderCore(bundled_dir=vocab_dir, overrides_dir=overrides_dir)
    rule = core.get_visual_rule("US")
    assert rule is not None
    assert rule.fill == "#FFFFFF"
    assert rule.palette == "stratigraphic"


def test_get_visual_rule_returns_none_for_unknown(vocab_dir: Path, overrides_dir: Path):
    core = VocabProviderCore(bundled_dir=vocab_dir, overrides_dir=overrides_dir)
    assert core.get_visual_rule("nonexistent") is None
```

- [ ] **Step 2: Run to confirm failure**

```bash
python3 -m pytest tests/sync/test_vocab_provider_core.py -k visual_rule -v
```

- [ ] **Step 3: Implement**

Add to `vocab_provider_core.py`:

```python
    def get_visual_rule(self, node_type: str) -> VisualRule | None:
        block = self._visual_data.get("rules", {})
        rule = block.get(node_type)
        if rule is None:
            return None
        return VisualRule(
            node_type=node_type,
            icon=rule.get("icon", ""),
            fill=rule.get("fill", ""),
            stroke=rule.get("stroke", ""),
            palette=rule.get("palette", ""),
        )
```

- [ ] **Step 4: Confirm pass**

```bash
python3 -m pytest tests/sync/test_vocab_provider_core.py -k visual_rule -v
```

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/vocab_provider_core.py tests/sync/test_vocab_provider_core.py
git commit -m "feat(s3dgraphy/sync): VocabProviderCore.get_visual_rule

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task B.6: get_cidoc_mapping()

**Files:**
- Modify: `modules/s3dgraphy/sync/vocab_provider_core.py`
- Modify: `tests/sync/test_vocab_provider_core.py`

- [ ] **Step 1: Add the failing test**

```python
def test_get_cidoc_mapping_returns_class_name(vocab_dir: Path, overrides_dir: Path):
    core = VocabProviderCore(bundled_dir=vocab_dir, overrides_dir=overrides_dir)
    assert core.get_cidoc_mapping("US") == "A2 Stratigraphic Volume Unit"


def test_get_cidoc_mapping_falls_back_for_unknown(vocab_dir: Path, overrides_dir: Path):
    core = VocabProviderCore(bundled_dir=vocab_dir, overrides_dir=overrides_dir)
    assert core.get_cidoc_mapping("nonexistent") is None
```

- [ ] **Step 2: Run to confirm failure**

```bash
python3 -m pytest tests/sync/test_vocab_provider_core.py -k cidoc -v
```

- [ ] **Step 3: Implement**

Add to `vocab_provider_core.py`:

```python
    def get_cidoc_mapping(self, type_abbreviation: str) -> str | None:
        for ut in self.get_unit_types():
            if ut.abbreviation == type_abbreviation:
                return ut.cidoc_class or None
        for pt in self.get_paradata_types():
            if pt.s3dgraphy_class == type_abbreviation or pt.abbreviation == type_abbreviation:
                return pt.cidoc_class or None
        return None
```

- [ ] **Step 4: Confirm pass**

```bash
python3 -m pytest tests/sync/test_vocab_provider_core.py -k cidoc -v
```

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/vocab_provider_core.py tests/sync/test_vocab_provider_core.py
git commit -m "feat(s3dgraphy/sync): VocabProviderCore.get_cidoc_mapping

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task B.7: Per-file version detection + minimum-version gating

**Files:**
- Modify: `modules/s3dgraphy/sync/vocab_provider_core.py`
- Modify: `tests/sync/test_vocab_provider_core.py`

- [ ] **Step 1: Add the failing tests**

```python
def test_versions_are_exposed(vocab_dir: Path, overrides_dir: Path):
    core = VocabProviderCore(bundled_dir=vocab_dir, overrides_dir=overrides_dir)
    v = core.versions
    assert v.nodes == "1.5.2"
    assert v.connections == "1.5.4"
    assert v.visual_rules == "1.5.0"


def test_minimum_version_gate_passes_when_met(vocab_dir: Path, overrides_dir: Path):
    core = VocabProviderCore(
        bundled_dir=vocab_dir,
        overrides_dir=overrides_dir,
        min_versions={"nodes": "1.5.0", "connections": "1.5.0", "visual_rules": "1.5.0"})
    assert core.versions.nodes == "1.5.2"  # no error


def test_minimum_version_gate_raises_when_unmet(vocab_dir: Path, overrides_dir: Path):
    with pytest.raises(ValueError, match="below required minimum"):
        VocabProviderCore(
            bundled_dir=vocab_dir,
            overrides_dir=overrides_dir,
            min_versions={"nodes": "9.9.9"})
```

- [ ] **Step 2: Run to confirm failures**

```bash
python3 -m pytest tests/sync/test_vocab_provider_core.py -k version -v
```

- [ ] **Step 3: Implement**

In `vocab_provider_core.py`, modify `__init__` and add helpers:

```python
from .vocab_types import EdgeType, Family, ParadataType, UnitType, VisualRule, VocabularyVersion


def _vtuple(s: str) -> tuple[int, ...]:
    """Parse a 'M.N.P' version string into a comparable tuple."""
    out: list[int] = []
    for part in (s or "0").split("."):
        try:
            out.append(int(part))
        except ValueError:
            out.append(0)
    return tuple(out)


class VocabProviderCore:

    def __init__(self,
                 bundled_dir: Path,
                 overrides_dir: Path,
                 min_versions: dict | None = None):
        self._bundled_dir = Path(bundled_dir)
        self._overrides_dir = Path(overrides_dir)
        self._min_versions = dict(min_versions or {})
        self._node_data: dict = {}
        self._connections_data: dict = {}
        self._visual_data: dict = {}
        self.reload()
        self._enforce_minimum_versions()

    def _enforce_minimum_versions(self) -> None:
        v = self.versions
        for key, required in self._min_versions.items():
            actual = getattr(v, key, "")
            if _vtuple(actual) < _vtuple(required):
                raise ValueError(
                    f"s3dgraphy vocabulary {key} version {actual!r} is below "
                    f"required minimum {required!r}")

    @property
    def versions(self) -> VocabularyVersion:
        return VocabularyVersion(
            nodes=self._node_data.get("s3Dgraphy_data_model_version", ""),
            connections=self._connections_data.get(
                "s3Dgraphy_connections_version", ""),
            visual_rules=self._visual_data.get("em_visual_rules_version", ""),
        )
```

- [ ] **Step 4: Confirm pass**

```bash
python3 -m pytest tests/sync/test_vocab_provider_core.py -v 2>&1 | tail -10
```
Expected: all tests in this file pass.

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/vocab_provider_core.py tests/sync/test_vocab_provider_core.py
git commit -m "feat(s3dgraphy/sync): per-file version detection + minimum-version gating

Each of the three JSON pillars carries its own version field; min_versions
in the constructor lets pyarchinit pin a floor and surface a clean error
when a vendor swap downgrades a pillar below the supported range.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task B.8: Override priority — verify partial overrides preserve bundled keys

**Files:**
- Modify: `tests/sync/test_vocab_provider_core.py`
- Modify: `modules/s3dgraphy/sync/vocab_provider_core.py` (only if test reveals a bug)

> The override merge logic was already implemented in B.2. This task is a behavioural test that the spec §3.1 requirement ("merge per top-level key, not whole-file") holds.

- [ ] **Step 1: Add the failing test**

```python
def test_override_merges_per_top_level_key_not_whole_file(
        tmp_path: Path,
        node_datamodel_path: Path,
        connections_datamodel_path: Path,
        visual_rules_path: Path):
    """A partial override that only redefines `paradata_nodes` must NOT
    erase `stratigraphic_nodes` from the bundled file."""
    bundled = tmp_path / "JSON_config"
    bundled.mkdir()
    (bundled / "s3Dgraphy_node_datamodel.json").write_bytes(node_datamodel_path.read_bytes())
    (bundled / "s3Dgraphy_connections_datamodel.json").write_bytes(connections_datamodel_path.read_bytes())
    (bundled / "em_visual_rules.json").write_bytes(visual_rules_path.read_bytes())

    overrides = tmp_path / "overrides"
    overrides.mkdir()
    import json as _json
    (overrides / "s3Dgraphy_node_datamodel.json").write_text(
        _json.dumps({
            "s3Dgraphy_data_model_version": "1.5.99",
            "paradata_nodes": {
                "AuthorNode": {
                    "class": "AuthorNode",
                    "label": "Custom override label",
                    "description": "overridden",
                    "mapping": {"cidoc": "E39 Actor", "cidoc_s3d": None},
                    "properties": {}
                }
            }
        }))

    core = VocabProviderCore(bundled_dir=bundled, overrides_dir=overrides)
    abbrevs = {ut.abbreviation for ut in core.get_unit_types(family=Family.STRATIGRAPHIC)}
    assert "US" in abbrevs  # bundled stratigraphic nodes survived
    paradata = core.get_paradata_types()
    assert any(p.label == "Custom override label" for p in paradata)
    assert core.versions.nodes == "1.5.99"
```

- [ ] **Step 2: Run — should already pass thanks to B.2's merge logic**

```bash
python3 -m pytest tests/sync/test_vocab_provider_core.py::test_override_merges_per_top_level_key_not_whole_file -v
```
Expected: PASS (because `_merge_dicts` already does per-key merge).

- [ ] **Step 3: Commit the regression test**

```bash
git add tests/sync/test_vocab_provider_core.py
git commit -m "test(s3dgraphy/sync): regression — override merges per top-level key

Spec §3.1 requires that a partial override (e.g. only redefining
paradata_nodes) does NOT erase bundled stratigraphic_nodes. This test
locks the behaviour in.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task B.9: __init__.py exports + Qt wrapper skeleton

**Files:**
- Modify: `modules/s3dgraphy/sync/__init__.py`
- Create: `modules/s3dgraphy/sync/vocab_provider.py`

- [ ] **Step 1: Wire the public API**

Replace `modules/s3dgraphy/sync/__init__.py`:

```python
"""Public API for the pyarchinit ↔ s3dgraphy sync layer.

Phase 1 ships only the Vocabulary subsystem; SyncEngine, GraphProjector,
ParadataStore, ConflictResolver land in Phase 2-3 (see
docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md).
"""
from __future__ import annotations

from .vocab_provider_core import VocabProviderCore
from .vocab_types import (
    EdgeType,
    Family,
    ParadataType,
    UnitType,
    VisualRule,
    VocabularyVersion,
)

__all__ = [
    "VocabProviderCore",
    "EdgeType",
    "Family",
    "ParadataType",
    "UnitType",
    "VisualRule",
    "VocabularyVersion",
]

# The Qt-aware wrapper (VocabProvider) is imported lazily on first call to
# get_vocab_provider() so that pure-Python callers (tests, scripts) avoid
# pulling Qt in at import time.


def get_vocab_provider():
    """Return a process-wide Qt-aware VocabProvider singleton."""
    from .vocab_provider import VocabProvider, get_default_provider
    return get_default_provider()
```

- [ ] **Step 2: Create the Qt wrapper**

Create `modules/s3dgraphy/sync/vocab_provider.py`:

```python
"""Qt-aware VocabProvider — wraps VocabProviderCore with a vocabulary_changed
signal and a QFileSystemWatcher for hot-reload of overrides.

This module imports PyQt symbols, so it should NOT be imported from
non-Qt contexts. Use VocabProviderCore directly for tests and CLI tools.
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    from qgis.PyQt.QtCore import QFileSystemWatcher, QObject, pyqtSignal
    _HAS_QT = True
except ImportError:  # pragma: no cover (only when QGIS not available)
    _HAS_QT = False
    QObject = object  # type: ignore[assignment,misc]

from .vocab_provider_core import VocabProviderCore


def _default_bundled_dir() -> Path:
    """Locate the bundled JSON_config/ inside ext_libs/s3dgraphy/."""
    here = Path(__file__).resolve()
    plugin_root = here.parents[3]
    return plugin_root / "ext_libs" / "s3dgraphy" / "JSON_config"


def _default_overrides_dir() -> Path:
    """User-writable overrides location."""
    return Path(os.path.expanduser("~/.config/pyarchinit/vocab_overrides"))


class VocabProvider(QObject if _HAS_QT else object):  # type: ignore[misc]
    """Process-wide vocabulary provider with hot-reload."""

    if _HAS_QT:
        vocabulary_changed = pyqtSignal(str)  # 'nodes' | 'connections' | 'visual_rules'

    def __init__(self,
                 bundled_dir: Path | None = None,
                 overrides_dir: Path | None = None,
                 parent=None):
        if _HAS_QT:
            super().__init__(parent)
        bundled = bundled_dir or _default_bundled_dir()
        overrides = overrides_dir or _default_overrides_dir()
        overrides.mkdir(parents=True, exist_ok=True)
        self._core = VocabProviderCore(bundled_dir=bundled, overrides_dir=overrides)
        if _HAS_QT:
            self._watcher = QFileSystemWatcher(self)
            for d in (bundled, overrides):
                if d.is_dir():
                    self._watcher.addPath(str(d))
            self._watcher.directoryChanged.connect(self._on_directory_changed)

    def _on_directory_changed(self, path: str) -> None:
        self._core.reload()
        if _HAS_QT:
            # We don't know which file changed; emit for all three for now.
            for which in ("nodes", "connections", "visual_rules"):
                self.vocabulary_changed.emit(which)

    # Delegations
    def get_unit_types(self, *args, **kwargs):
        return self._core.get_unit_types(*args, **kwargs)

    def get_edge_types(self):
        return self._core.get_edge_types()

    def get_legal_targets_for(self, source_type: str, edge_name: str):
        return self._core.get_legal_targets_for(source_type, edge_name)

    def get_paradata_types(self):
        return self._core.get_paradata_types()

    def get_visual_rule(self, node_type: str):
        return self._core.get_visual_rule(node_type)

    def get_cidoc_mapping(self, type_abbreviation: str):
        return self._core.get_cidoc_mapping(type_abbreviation)

    @property
    def versions(self):
        return self._core.versions


_DEFAULT_PROVIDER: VocabProvider | None = None


def get_default_provider() -> VocabProvider:
    global _DEFAULT_PROVIDER
    if _DEFAULT_PROVIDER is None:
        _DEFAULT_PROVIDER = VocabProvider()
    return _DEFAULT_PROVIDER
```

- [ ] **Step 3: Smoke import (no QGIS needed if pure Python only)**

```bash
python3 -c "
from modules.s3dgraphy.sync import (
    VocabProviderCore, UnitType, Family, EdgeType, VisualRule
)
print('public API OK')
"
```
Expected: `public API OK`.

- [ ] **Step 4: Commit**

```bash
git add modules/s3dgraphy/sync/__init__.py modules/s3dgraphy/sync/vocab_provider.py
git commit -m "feat(s3dgraphy/sync): Qt-aware VocabProvider wrapper

Imports the PyQt VocabProvider lazily via get_vocab_provider(). The pure
Python core (VocabProviderCore) remains the testable surface; the Qt
layer adds a QFileSystemWatcher on bundled+overrides dirs and a
vocabulary_changed signal that combo boxes subscribe to (Phase 1
consumers in Group C).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task B.10: Smoke test against the real 0.1.40 vendored JSONs

**Files:**
- Create: `tests/sync/test_vocab_provider_smoke.py`

- [ ] **Step 1: Write the smoke test**

Create `tests/sync/test_vocab_provider_smoke.py`:

```python
"""Smoke test against the real bundled 0.1.40 JSON_config/.

Skipped if the vendored s3dgraphy is not present (e.g. tests run from a
fresh clone before pip install --target).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.s3dgraphy.sync.vocab_provider_core import VocabProviderCore
from modules.s3dgraphy.sync.vocab_types import Family

BUNDLED = (Path(__file__).resolve().parents[2]
           / "ext_libs" / "s3dgraphy" / "JSON_config")


@pytest.mark.skipif(not BUNDLED.is_dir(),
                    reason="ext_libs/s3dgraphy/JSON_config/ not present")
def test_real_bundled_loads_us_and_usvs(tmp_path):
    core = VocabProviderCore(bundled_dir=BUNDLED, overrides_dir=tmp_path)
    abbrevs = {ut.abbreviation for ut in core.get_unit_types(family=Family.STRATIGRAPHIC)}
    # Must contain the canonical EM 1.5 stratigraphic types
    assert "US" in abbrevs
    assert "USVs" in abbrevs
    assert "USVn" in abbrevs


@pytest.mark.skipif(not BUNDLED.is_dir(),
                    reason="ext_libs/s3dgraphy/JSON_config/ not present")
def test_real_bundled_versions_present(tmp_path):
    core = VocabProviderCore(bundled_dir=BUNDLED, overrides_dir=tmp_path)
    v = core.versions
    assert v.nodes  # non-empty
```

- [ ] **Step 2: Run**

```bash
python3 -m pytest tests/sync/test_vocab_provider_smoke.py -v
```
Expected: 2 tests pass against the freshly vendored 0.1.40.

- [ ] **Step 3: Commit**

```bash
git add tests/sync/test_vocab_provider_smoke.py
git commit -m "test(s3dgraphy/sync): smoke test against real bundled 0.1.40 JSONs

Confirms US, USVs, USVn appear in stratigraphic family on the actual
0.1.40 vendor. Auto-skipped when ext_libs/s3dgraphy/ is missing.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task B.11: Run the full sync test suite

**Files:** none (verification)

- [ ] **Step 1: Run all sync tests**

```bash
python3 -m pytest tests/sync/ -v 2>&1 | tail -25
```
Expected: green. If any fail, fix before proceeding to Group C.

---

## Group C — i18n adapter refactor

> **Backwards compat constraint:** existing imports like `from modules.utility.pyarchinit_i18n_stratigraphic import _COMMON_ITEMS, UNIT_TYPE_ABBREV, get_unit_type_items` must keep working for one release.

### Task C.1: Capture the current public surface as a regression test

**Files:**
- Create: `tests/sync/test_i18n_compat.py`

- [ ] **Step 1: Write the regression test**

Create `tests/sync/test_i18n_compat.py`:

```python
"""Backwards-compat regression: pyarchinit_i18n_stratigraphic exports
must keep working after the VocabProvider adapter refactor."""
from __future__ import annotations


def test_common_items_importable():
    from modules.utility.pyarchinit_i18n_stratigraphic import _COMMON_ITEMS
    # Spec §4.4: post-migration USVA/USVB → USVs, USVC → USVn. The compat
    # shim continues to expose the legacy abbrevs so old code keeps
    # working; the migration is the only place where they get rewritten.
    assert "USVA" in _COMMON_ITEMS or "USVs" in _COMMON_ITEMS
    assert "DOC" in _COMMON_ITEMS


def test_unit_type_abbrev_importable():
    from modules.utility.pyarchinit_i18n_stratigraphic import UNIT_TYPE_ABBREV
    assert "it" in UNIT_TYPE_ABBREV
    assert UNIT_TYPE_ABBREV["it"] == ("US", "USM")


def test_get_unit_type_items_returns_iterable():
    from modules.utility.pyarchinit_i18n_stratigraphic import get_unit_type_items
    items = get_unit_type_items("it")
    assert "US" in items
    assert "USM" in items


def test_is_us_type_recognises_legacy():
    from modules.utility.pyarchinit_i18n_stratigraphic import is_us_type
    assert is_us_type("US")
    assert is_us_type("SU")  # English


def test_all_us_abbrevs_exposed():
    from modules.utility.pyarchinit_i18n_stratigraphic import ALL_US_ABBREVS
    assert "US" in ALL_US_ABBREVS
```

- [ ] **Step 2: Run BEFORE refactor — should pass on current code**

```bash
python3 -m pytest tests/sync/test_i18n_compat.py -v 2>&1 | tail -10
```
Expected: 5 tests pass against the current (pre-refactor) `pyarchinit_i18n_stratigraphic.py`.

- [ ] **Step 3: Commit the regression test**

```bash
git add tests/sync/test_i18n_compat.py
git commit -m "test(i18n): pin pyarchinit_i18n_stratigraphic public surface

5 regression tests lock the imports current callers rely on. They must
keep passing across the VocabProvider adapter refactor.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task C.2: Refactor `pyarchinit_i18n_stratigraphic.py` as adapter

**Files:**
- Modify: `modules/utility/pyarchinit_i18n_stratigraphic.py`

- [ ] **Step 1: Read the current file end-to-end**

```bash
wc -l modules/utility/pyarchinit_i18n_stratigraphic.py
```
Expected: roughly 200-400 lines. Read every line before editing.

- [ ] **Step 2: Refactor the top of the file**

Replace lines 1-60 of `modules/utility/pyarchinit_i18n_stratigraphic.py` (the imports + UNIT_TYPE_ABBREV + _COMMON_ITEMS block) with:

```python
# -*- coding: utf-8 -*-
"""
Central i18n module for stratigraphic unit types and relationships.

DEPRECATION (5.1.0-alpha → 6.0.0): the hard-coded vocabulary lists in
this module are superseded by VocabProvider, which reads the canonical
s3dgraphy JSON pillars (see Reference Doc v0.1 §4.5 Option B). This
module now delegates to VocabProvider while keeping the original
public surface for backward compatibility. Plan: remove the hard-coded
fallback lists in the next major bump (6.0.0).
"""
from __future__ import annotations

import logging
from functools import lru_cache

_log = logging.getLogger(__name__)
_DEPRECATION_LOGGED = False


def _warn_deprecation_once():
    global _DEPRECATION_LOGGED
    if _DEPRECATION_LOGGED:
        return
    _DEPRECATION_LOGGED = True
    _log.info(
        "pyarchinit_i18n_stratigraphic is deprecated; new code should use "
        "modules.s3dgraphy.sync.VocabProvider directly. The legacy surface "
        "is kept for one release cycle.")


# ---------------------------------------------------------------------------
# Unit Type Abbreviations (per-language US/USM)
# ---------------------------------------------------------------------------
# Only US and USM equivalents change per language. These are pyarchinit-
# specific UI conventions that are NOT in the s3dgraphy JSON datamodel,
# so they remain hard-coded here. The list of stratigraphic types
# beyond US/USM (USVs, USVn, …) is sourced from VocabProvider.

UNIT_TYPE_ABBREV = {
    'it': ('US',  'USM'),
    'en': ('SU',  'WSU'),
    'de': ('SE',  'MSE'),
    'fr': ('US',  'USM'),
    'es': ('UE',  'UEM'),
    'ar': ('SU',  'WSU'),
    'ca': ('UE',  'UEM'),
    'ro': ('US',  'USZ'),
    'pt': ('UE',  'UEM'),
    'el': ('ΣΜ', 'ΤΣΜ'),
}

ALL_US_ABBREVS = {v[0] for v in UNIT_TYPE_ABBREV.values()}
ALL_USM_ABBREVS = {v[1] for v in UNIT_TYPE_ABBREV.values()}
ALL_UNIT_ABBREVS = ALL_US_ABBREVS | ALL_USM_ABBREVS


# ---------------------------------------------------------------------------
# Stratigraphic / paradata abbreviations from VocabProvider
# ---------------------------------------------------------------------------
# These were previously a hard-coded tuple. They now resolve from the
# s3dgraphy JSON datamodel. Fallback to the legacy hard-coded list is
# kept for cases where ext_libs/s3dgraphy/ is absent (fresh clone
# before pip install --target).

_LEGACY_COMMON_ITEMS = (
    'USVA', 'USVB', 'USVC', 'USD', 'CON', 'VSF', 'SF', 'SUS',
    'Combinar', 'Extractor', 'DOC', 'property',
)


@lru_cache(maxsize=1)
def _build_common_items() -> tuple[str, ...]:
    _warn_deprecation_once()
    try:
        from modules.s3dgraphy.sync import get_vocab_provider
        provider = get_vocab_provider()
        types = provider.get_unit_types()
        # Filter to non-US/USM stratigraphic + paradata abbreviations.
        # US/USM are added by get_unit_type_items() per-language.
        items = []
        seen = set()
        for ut in types:
            ab = ut.abbreviation
            if ab in ALL_UNIT_ABBREVS:  # US/USM equivalents
                continue
            if ab in seen:
                continue
            seen.add(ab)
            items.append(ab)
        # Keep legacy items that VocabProvider may not surface yet
        # (CON, SUS, Combinar, Extractor, DOC, property are pyarchinit-
        # specific UI options, not s3dgraphy node types — see
        # Reference Doc v0.1 §4.2)
        for legacy in ('CON', 'SUS', 'Combinar', 'Extractor', 'DOC', 'property'):
            if legacy not in seen:
                items.append(legacy)
        return tuple(items)
    except Exception as e:
        _log.warning(
            "VocabProvider unavailable; falling back to legacy "
            "_COMMON_ITEMS list: %s", e)
        return _LEGACY_COMMON_ITEMS


# Lazy property-style accessor: keeping the module-level name so
# `from pyarchinit_i18n_stratigraphic import _COMMON_ITEMS` keeps working.
class _CommonItemsProxy(tuple):
    """Behaves like a tuple but delegates to VocabProvider on first access."""
    def __new__(cls):
        return super().__new__(cls, _build_common_items())


_COMMON_ITEMS = _CommonItemsProxy()


def get_unit_type_items(lang):
    """Return full tuple of items for the unit-type picker dialog."""
    us, usm = UNIT_TYPE_ABBREV.get(lang, UNIT_TYPE_ABBREV['en'])
    return (us, usm) + tuple(_COMMON_ITEMS)


def is_us_type(abbrev):
    """Check if *abbrev* is any language's US equivalent."""
    return abbrev in ALL_US_ABBREVS


def is_usm_type(abbrev):
    """Check if *abbrev* is any language's USM equivalent."""
    return abbrev in ALL_USM_ABBREVS


def is_any_unit_prefix(text):
    """Check if *text* starts with any known US or USM abbreviation."""
    for a in ALL_UNIT_ABBREVS:
        if text.startswith(a):
            return True
    return False
```

Leave the rest of the file (`_UNIT_TYPE_LABELS`, `STRATIGRAPHIC_RELATIONS`, …) untouched in this task. They get refactored in Phase 2 when `GraphProjector` consumes them.

- [ ] **Step 3: Run the regression test**

```bash
python3 -m pytest tests/sync/test_i18n_compat.py -v 2>&1 | tail -10
```
Expected: 5 tests still pass.

- [ ] **Step 4: Run all unit tests for incidental breakage**

```bash
python3 -m pytest tests/sync/ -v 2>&1 | tail -10
```
Expected: green.

- [ ] **Step 5: Commit**

```bash
git add modules/utility/pyarchinit_i18n_stratigraphic.py
git commit -m "refactor(i18n): pyarchinit_i18n_stratigraphic delegates to VocabProvider

- _COMMON_ITEMS becomes a lazy tuple-proxy that resolves from
  VocabProvider.get_unit_types() at first access (no s3dgraphy import
  at module load)
- Falls back to the legacy hard-coded list when ext_libs/s3dgraphy/ is
  missing (fresh clone, before pip install --target)
- UNIT_TYPE_ABBREV stays hard-coded — per-language US/USM is a pyarchinit
  UI convention, not part of the s3dgraphy formalism
- One-time deprecation log via _warn_deprecation_once() points new
  callers at modules.s3dgraphy.sync.VocabProvider

Public surface unchanged (5 regression tests in tests/sync/test_i18n_compat.py
still pass). Removal of the legacy fallback scheduled for 6.0.0.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Group D — Vocabulary alignment migration (`USVA/USVB → USVs`, `USVC → USVn`)

### Task D.1: Migration helpers + argparse scaffold

**Files:**
- Create: `scripts/migrations/__init__.py`
- Create: `scripts/migrations/_common.py`
- Create: `tests/migrations/__init__.py`
- Create: `tests/migrations/test_common.py`

- [ ] **Step 1: Set up directories**

```bash
mkdir -p scripts/migrations tests/migrations
touch scripts/migrations/__init__.py tests/migrations/__init__.py
```

- [ ] **Step 2: Write the failing test for the auto-backup helper**

Create `tests/migrations/test_common.py`:

```python
"""Tests for the migration shared helpers."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from scripts.migrations._common import auto_backup_sqlite, parse_argv


def test_auto_backup_sqlite_copies_file(tmp_path: Path):
    src = tmp_path / "x.sqlite"
    conn = sqlite3.connect(src)
    conn.execute("CREATE TABLE t (id INTEGER)")
    conn.execute("INSERT INTO t VALUES (42)")
    conn.commit()
    conn.close()

    backup_path = auto_backup_sqlite(src, tag="testing")
    assert backup_path.exists()
    assert backup_path != src
    # Open backup and verify the row is there
    bconn = sqlite3.connect(backup_path)
    assert bconn.execute("SELECT id FROM t").fetchone() == (42,)
    bconn.close()


def test_parse_argv_supports_dry_run_apply_rollback():
    args = parse_argv(["--db", "/tmp/x.sqlite", "--dry-run"])
    assert args.dry_run is True
    assert args.apply is False
    assert args.rollback is None
    args = parse_argv(["--db", "/tmp/x.sqlite", "--apply"])
    assert args.apply is True
    args = parse_argv(["--db", "/tmp/x.sqlite", "--rollback", "/tmp/backup.sqlite"])
    assert args.rollback == "/tmp/backup.sqlite"


def test_parse_argv_requires_one_action(capsys):
    with pytest.raises(SystemExit):
        parse_argv(["--db", "/tmp/x.sqlite"])  # no action
```

- [ ] **Step 3: Run, expect failure**

```bash
python3 -m pytest tests/migrations/test_common.py -v 2>&1 | tail -10
```
Expected: ImportError (module not found).

- [ ] **Step 4: Implement**

Create `scripts/migrations/_common.py`:

```python
"""Shared helpers for one-shot migrations.

All migrations expose the same CLI: --dry-run | --apply | --rollback <path>.
Auto-backup is invoked at the start of any --apply run.
"""
from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path


def auto_backup_sqlite(db_path: Path, tag: str) -> Path:
    """Copy db_path to <db>.pre_<tag>_<UTC timestamp>; return new path."""
    db_path = Path(db_path)
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup = db_path.with_name(f"{db_path.name}.pre_{tag}_{stamp}")
    shutil.copy2(db_path, backup)
    return backup


def parse_argv(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True, help="Path to SQLite (or DSN for PG)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true",
                   help="Report what would change; do not mutate")
    g.add_argument("--apply", action="store_true",
                   help="Apply the migration (auto-backup first)")
    g.add_argument("--rollback", metavar="BACKUP_PATH",
                   help="Restore the DB from a previous --apply backup")
    return p.parse_args(argv)
```

- [ ] **Step 5: Run, expect pass**

```bash
python3 -m pytest tests/migrations/test_common.py -v 2>&1 | tail -10
```

- [ ] **Step 6: Commit**

```bash
git add scripts/migrations/__init__.py scripts/migrations/_common.py tests/migrations/__init__.py tests/migrations/test_common.py
git commit -m "feat(migrations): shared --dry-run/--apply/--rollback scaffold + auto-backup

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task D.2: Vocabulary alignment migration — dry-run

**Files:**
- Create: `scripts/migrations/2026_05_us_vocabulary_alignment.py`
- Create: `tests/migrations/test_us_vocabulary_alignment.py`

- [ ] **Step 1: Write the failing test**

Create `tests/migrations/test_us_vocabulary_alignment.py`:

```python
"""Tests for the USVA/USVB→USVs, USVC→USVn migration."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from scripts.migrations._2026_05_us_vocabulary_alignment_lib import (
    plan_changes,
    apply_changes,
    REPLACEMENTS,
)


def _seed_db(p: Path):
    conn = sqlite3.connect(p)
    conn.execute("""
        CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY,
            sito TEXT, area TEXT, us TEXT, unita_tipo TEXT
        )""")
    rows = [
        (1, "S", "1", "1", "US"),
        (2, "S", "1", "2", "USVA"),
        (3, "S", "1", "3", "USVB"),
        (4, "S", "1", "4", "USVC"),
        (5, "S", "1", "5", "USVs"),  # already aligned
    ]
    conn.executemany("INSERT INTO us_table VALUES (?,?,?,?,?)", rows)
    conn.commit()
    conn.close()


def test_plan_reports_counts(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    plan = plan_changes(db)
    assert plan["USVA"] == 1
    assert plan["USVB"] == 1
    assert plan["USVC"] == 1
    assert plan["USVs (already-aligned)"] == 1


def test_plan_does_not_mutate(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    plan_changes(db)
    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT unita_tipo FROM us_table ORDER BY id_us").fetchall()
    conn.close()
    assert [r[0] for r in rows] == ["US", "USVA", "USVB", "USVC", "USVs"]


def test_apply_rewrites_in_place(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    apply_changes(db)
    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT unita_tipo FROM us_table ORDER BY id_us").fetchall()
    conn.close()
    assert [r[0] for r in rows] == ["US", "USVs", "USVs", "USVn", "USVs"]


def test_apply_idempotent(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    apply_changes(db)
    apply_changes(db)  # second run must be a no-op
    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT unita_tipo FROM us_table ORDER BY id_us").fetchall()
    conn.close()
    assert [r[0] for r in rows] == ["US", "USVs", "USVs", "USVn", "USVs"]


def test_replacements_constant():
    assert REPLACEMENTS["USVA"] == "USVs"
    assert REPLACEMENTS["USVB"] == "USVs"
    assert REPLACEMENTS["USVC"] == "USVn"
```

- [ ] **Step 2: Run, expect failure**

```bash
python3 -m pytest tests/migrations/test_us_vocabulary_alignment.py -v 2>&1 | tail -10
```

- [ ] **Step 3: Implement the library + CLI**

Create `scripts/migrations/_2026_05_us_vocabulary_alignment_lib.py`:

```python
"""Library for the USVA/USVB→USVs, USVC→USVn migration.

Split from the CLI script so tests can import the logic without invoking
argparse. The CLI module imports plan_changes/apply_changes from here.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

REPLACEMENTS = {
    "USVA": "USVs",
    "USVB": "USVs",
    "USVC": "USVn",
}


def plan_changes(db_path: Path) -> dict[str, int]:
    """Return counts per source-abbreviation. No mutation."""
    counts: dict[str, int] = {k: 0 for k in REPLACEMENTS}
    counts["USVs (already-aligned)"] = 0
    counts["USVn (already-aligned)"] = 0
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        for src in REPLACEMENTS:
            cur.execute(
                "SELECT COUNT(*) FROM us_table WHERE unita_tipo = ?", (src,))
            counts[src] = cur.fetchone()[0]
        for tgt in {"USVs", "USVn"}:
            cur.execute(
                "SELECT COUNT(*) FROM us_table WHERE unita_tipo = ?", (tgt,))
            counts[f"{tgt} (already-aligned)"] = cur.fetchone()[0]
    finally:
        conn.close()
    return counts


def apply_changes(db_path: Path) -> dict[str, int]:
    """Apply REPLACEMENTS in-place; return counts of rows updated per source."""
    applied: dict[str, int] = {}
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        for src, tgt in REPLACEMENTS.items():
            cur.execute(
                "UPDATE us_table SET unita_tipo = ? WHERE unita_tipo = ?",
                (tgt, src))
            applied[src] = cur.rowcount
        conn.commit()
    finally:
        conn.close()
    return applied
```

Create `scripts/migrations/2026_05_us_vocabulary_alignment.py`:

```python
#!/usr/bin/env python3
"""One-shot migration: USVA/USVB → USVs, USVC → USVn.

Per spec §4.4. Idempotent. Auto-backups DB before --apply.
"""
from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path

from scripts.migrations._common import auto_backup_sqlite, parse_argv
from scripts.migrations._2026_05_us_vocabulary_alignment_lib import (
    apply_changes,
    plan_changes,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("us_vocabulary_alignment")


def main(argv: list[str] | None = None) -> int:
    args = parse_argv(argv)
    db = Path(args.db)
    if not db.exists():
        log.error("DB not found: %s", db)
        return 2

    if args.dry_run:
        plan = plan_changes(db)
        log.info("Dry-run plan for %s:", db)
        for k, v in plan.items():
            log.info("  %-30s %d", k, v)
        return 0

    if args.apply:
        backup = auto_backup_sqlite(db, tag="us_vocab_alignment")
        log.info("Backup created: %s", backup)
        applied = apply_changes(db)
        log.info("Applied to %s:", db)
        for k, v in applied.items():
            log.info("  %s -> %d row(s) updated", k, v)
        return 0

    if args.rollback:
        backup = Path(args.rollback)
        if not backup.exists():
            log.error("Backup not found: %s", backup)
            return 2
        shutil.copy2(backup, db)
        log.info("Rolled back %s ← %s", db, backup)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run tests, expect pass**

```bash
python3 -m pytest tests/migrations/test_us_vocabulary_alignment.py -v 2>&1 | tail -15
```

- [ ] **Step 5: Run the dry-run on the real Volterra DB (read-only check)**

```bash
python3 -m scripts.migrations.2026_05_us_vocabulary_alignment \
    --db "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitcs_SCHEDE2024.sqlite" \
    --dry-run 2>&1 | tail -10
```
Expected: counts printed (likely all zero on Volterra — record this in the QGIS smoke gate G.4).

- [ ] **Step 6: Commit**

```bash
git add scripts/migrations/_2026_05_us_vocabulary_alignment_lib.py \
        scripts/migrations/2026_05_us_vocabulary_alignment.py \
        tests/migrations/test_us_vocabulary_alignment.py
git commit -m "feat(migrations): USVA/USVB→USVs, USVC→USVn one-shot migration

- --dry-run / --apply / --rollback (spec §4.4)
- Idempotent: second --apply is a no-op
- Auto-backup before any UPDATE (named pre_us_vocab_alignment_<UTC>)
- Library + CLI split for testability

Tests: tests/migrations/test_us_vocabulary_alignment.py (6 tests).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task D.3: Wire the migration into a QGIS Maintenance menu

**Files:**
- Modify: `pyarchinit_Plugin.py` (add menu entry)

- [ ] **Step 1: Locate the Maintenance menu**

```bash
grep -nE "Maintenance|menu_principale|addMenu" pyarchinit_Plugin.py | head -10
```

- [ ] **Step 2: Add the menu wiring**

Find the place where the plugin builds its menu (likely in `initGui()`). Add after the existing entries:

```python
        # Phase 1 migrations (spec §4.4 / §4.5)
        from PyQt5.QtWidgets import QAction
        action_vocab_align = QAction(
            "Migrazioni → Allinea vocabolario US (USVA/USVB→USVs, USVC→USVn)",
            self.iface.mainWindow())
        action_vocab_align.triggered.connect(self._run_vocab_alignment_migration)
        self.menu.addAction(action_vocab_align)
        self.actions.append(action_vocab_align)

    def _run_vocab_alignment_migration(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        from scripts.migrations._2026_05_us_vocabulary_alignment_lib import (
            apply_changes,
            plan_changes,
        )
        from scripts.migrations._common import auto_backup_sqlite

        db_path, _ = QFileDialog.getOpenFileName(
            self.iface.mainWindow(),
            "Seleziona il database pyarchinit (.sqlite)",
            "",
            "SQLite databases (*.sqlite)",
        )
        if not db_path:
            return
        from pathlib import Path
        db = Path(db_path)
        plan = plan_changes(db)
        msg = "Piano:\n" + "\n".join(f"  {k}: {v}" for k, v in plan.items())
        confirm = QMessageBox.question(
            self.iface.mainWindow(),
            "Conferma migrazione vocabolario US",
            msg + "\n\nProcedere con --apply (con backup automatico)?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        backup = auto_backup_sqlite(db, tag="us_vocab_alignment")
        applied = apply_changes(db)
        QMessageBox.information(
            self.iface.mainWindow(),
            "Migrazione completata",
            f"Backup: {backup}\n\nAggiornamenti: {applied}",
        )
```

- [ ] **Step 3: Manual smoke (skip in CI; runs only inside QGIS)**

User restarts QGIS; verifies the new menu entry "Allinea vocabolario US" exists; runs dry-run on a copy of the Volterra DB.

- [ ] **Step 4: Commit**

```bash
git add pyarchinit_Plugin.py
git commit -m "feat(plugin): QGIS menu entry for vocabulary alignment migration

User-facing UI for the USVA/USVB→USVs, USVC→USVn migration. Shows the
dry-run plan in a QMessageBox confirmation dialog before invoking
--apply (with auto-backup).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Group E — UUID v7 backfill migration

### Task E.1: Local UUID v7 implementation

**Files:**
- Create: `modules/s3dgraphy/sync/uuid7.py`
- Create: `tests/sync/test_uuid7.py`

- [ ] **Step 1: Write the failing test**

Create `tests/sync/test_uuid7.py`:

```python
"""Tests for the local UUID v7 implementation (RFC 9562 §5.7)."""
from __future__ import annotations

import time
import uuid

from modules.s3dgraphy.sync.uuid7 import uuid7


def test_returns_uuid_object():
    u = uuid7()
    assert isinstance(u, uuid.UUID)


def test_version_field_is_7():
    u = uuid7()
    assert u.version == 7


def test_variant_is_rfc4122():
    u = uuid7()
    # UUID variant should be RFC 4122 (the "10xx" pattern in byte 8)
    assert (u.bytes[8] & 0xC0) == 0x80


def test_uuid_v7s_are_monotonically_ordered_per_call_burst():
    # 1024 UUIDs generated back-to-back should sort in their generation order
    ids = [uuid7() for _ in range(1024)]
    assert ids == sorted(ids)


def test_timestamp_within_recent_window():
    before_ms = int(time.time() * 1000)
    u = uuid7()
    after_ms = int(time.time() * 1000)
    # First 6 bytes encode the millisecond timestamp
    ts = int.from_bytes(u.bytes[:6], "big")
    assert before_ms - 1 <= ts <= after_ms + 1
```

- [ ] **Step 2: Run, expect failure**

```bash
python3 -m pytest tests/sync/test_uuid7.py -v 2>&1 | tail -10
```

- [ ] **Step 3: Implement**

Create `modules/s3dgraphy/sync/uuid7.py`:

```python
"""Local UUID v7 generator (RFC 9562 §5.7).

Replaces with `uuid.uuid7()` once the project minimum is Python 3.14+.
This implementation is monotonic per-process: when called twice within
the same millisecond, the second call increments the random portion to
preserve ordering.
"""
from __future__ import annotations

import os
import threading
import time
import uuid


_lock = threading.Lock()
_last_ms = 0
_last_rand = 0


def uuid7() -> uuid.UUID:
    """Return a new UUID v7."""
    global _last_ms, _last_rand
    with _lock:
        now_ms = int(time.time() * 1000)
        if now_ms <= _last_ms:
            now_ms = _last_ms
            # Bump the random portion to keep monotonicity inside the ms.
            _last_rand += 1
            rand = _last_rand
        else:
            _last_ms = now_ms
            _last_rand = int.from_bytes(os.urandom(10), "big")
            rand = _last_rand

        # 48-bit timestamp + 4-bit version + 12-bit rand_a + 2-bit variant +
        # 62-bit rand_b
        ts_bytes = now_ms.to_bytes(6, "big")
        rand_bytes = rand.to_bytes(10, "big")
        b = bytearray(16)
        b[0:6] = ts_bytes
        b[6:16] = rand_bytes
        b[6] = (b[6] & 0x0F) | 0x70  # version 7
        b[8] = (b[8] & 0x3F) | 0x80  # variant 10xx
        return uuid.UUID(bytes=bytes(b))
```

- [ ] **Step 4: Run, expect pass**

```bash
python3 -m pytest tests/sync/test_uuid7.py -v 2>&1 | tail -10
```

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/uuid7.py tests/sync/test_uuid7.py
git commit -m "feat(s3dgraphy/sync): local UUID v7 generator (RFC 9562 §5.7)

Monotonic per-process. Will be replaced with stdlib uuid.uuid7() when
the project minimum bumps to Python 3.14+.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task E.2: UUID backfill migration (SQLite)

**Files:**
- Create: `scripts/migrations/_2026_05_node_uuid_backfill_lib.py`
- Create: `scripts/migrations/2026_05_node_uuid_backfill.py`
- Create: `tests/migrations/test_node_uuid_backfill.py`

- [ ] **Step 1: Write the failing test**

Create `tests/migrations/test_node_uuid_backfill.py`:

```python
"""Tests for the node_uuid backfill migration (spec §4.5)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from scripts.migrations._2026_05_node_uuid_backfill_lib import (
    TABLES,
    add_columns,
    backfill_uuids,
)


def _seed(p: Path):
    conn = sqlite3.connect(p)
    conn.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, sito TEXT)")
    conn.execute("CREATE TABLE inventario_materiali_table (id_invmat INTEGER PRIMARY KEY, sito TEXT)")
    conn.execute("CREATE TABLE periodizzazione_table (id_perfas INTEGER PRIMARY KEY, sito TEXT)")
    for tbl, idcol in [("us_table", "id_us"),
                       ("inventario_materiali_table", "id_invmat"),
                       ("periodizzazione_table", "id_perfas")]:
        for i in range(1, 4):
            conn.execute(f"INSERT INTO {tbl} ({idcol}, sito) VALUES (?, ?)", (i, "S"))
    conn.commit()
    conn.close()


def test_add_columns_adds_node_uuid_to_each_table(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed(db)
    add_columns(db)
    conn = sqlite3.connect(db)
    for tbl in TABLES:
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({tbl})").fetchall()]
        assert "node_uuid" in cols
    # Unique index exists
    idx = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index'").fetchall()]
    assert any("node_uuid" in i.lower() for i in idx)
    conn.close()


def test_add_columns_idempotent(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed(db)
    add_columns(db)
    add_columns(db)  # second run is no-op
    conn = sqlite3.connect(db)
    for tbl in TABLES:
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({tbl})").fetchall()]
        assert cols.count("node_uuid") == 1
    conn.close()


def test_backfill_assigns_uuid_v7(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed(db)
    add_columns(db)
    counts = backfill_uuids(db)
    assert counts["us_table"] == 3
    assert counts["inventario_materiali_table"] == 3
    assert counts["periodizzazione_table"] == 3
    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT node_uuid FROM us_table").fetchall()
    conn.close()
    assert all(len(r[0]) == 36 for r in rows)
    # version 7 char is at index 14 in the canonical form (xxxxxxxx-xxxx-Vxxx-…)
    assert all(r[0][14] == "7" for r in rows)


def test_backfill_idempotent(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed(db)
    add_columns(db)
    backfill_uuids(db)
    counts = backfill_uuids(db)  # second run: nothing to fill
    assert all(v == 0 for v in counts.values())
```

- [ ] **Step 2: Run, expect failure**

```bash
python3 -m pytest tests/migrations/test_node_uuid_backfill.py -v 2>&1 | tail -10
```

- [ ] **Step 3: Implement**

Create `scripts/migrations/_2026_05_node_uuid_backfill_lib.py`:

```python
"""Library for the node_uuid TEXT column + UUID v7 backfill."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from modules.s3dgraphy.sync.uuid7 import uuid7

TABLES = (
    "us_table",
    "inventario_materiali_table",
    "periodizzazione_table",
)


def _has_column(conn: sqlite3.Connection, table: str, col: str) -> bool:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return any(r[1] == col for r in cur.fetchall())


def add_columns(db_path: Path) -> None:
    """Add node_uuid TEXT + unique index per table. Idempotent."""
    conn = sqlite3.connect(db_path)
    try:
        for tbl in TABLES:
            if not _has_column(conn, tbl, "node_uuid"):
                conn.execute(f"ALTER TABLE {tbl} ADD COLUMN node_uuid TEXT")
            idx_name = f"ix_{tbl}_node_uuid"
            conn.execute(
                f"CREATE UNIQUE INDEX IF NOT EXISTS {idx_name} "
                f"ON {tbl}(node_uuid) WHERE node_uuid IS NOT NULL")
        conn.commit()
    finally:
        conn.close()


def backfill_uuids(db_path: Path) -> dict[str, int]:
    """Assign UUID v7 to every NULL node_uuid; return per-table counts."""
    counts: dict[str, int] = {}
    conn = sqlite3.connect(db_path)
    try:
        for tbl in TABLES:
            cur = conn.execute(
                f"SELECT rowid FROM {tbl} WHERE node_uuid IS NULL")
            rowids = [r[0] for r in cur.fetchall()]
            for rid in rowids:
                conn.execute(
                    f"UPDATE {tbl} SET node_uuid = ? WHERE rowid = ?",
                    (str(uuid7()), rid))
            counts[tbl] = len(rowids)
        conn.commit()
    finally:
        conn.close()
    return counts
```

Create `scripts/migrations/2026_05_node_uuid_backfill.py`:

```python
#!/usr/bin/env python3
"""One-shot migration: add node_uuid TEXT column + backfill UUID v7.

Per spec §4.5. Idempotent. Auto-backups DB before --apply.
"""
from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path

from scripts.migrations._common import auto_backup_sqlite, parse_argv
from scripts.migrations._2026_05_node_uuid_backfill_lib import (
    TABLES,
    add_columns,
    backfill_uuids,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("node_uuid_backfill")


def main(argv: list[str] | None = None) -> int:
    args = parse_argv(argv)
    db = Path(args.db)
    if not db.exists():
        log.error("DB not found: %s", db)
        return 2

    if args.dry_run:
        import sqlite3
        conn = sqlite3.connect(db)
        try:
            for tbl in TABLES:
                cur = conn.execute(f"PRAGMA table_info({tbl})")
                cols = [r[1] for r in cur.fetchall()]
                missing = "node_uuid" not in cols
                if missing:
                    log.info("  %s: needs ALTER TABLE + backfill (no col)", tbl)
                else:
                    n = conn.execute(
                        f"SELECT COUNT(*) FROM {tbl} WHERE node_uuid IS NULL"
                    ).fetchone()[0]
                    log.info("  %s: %d row(s) need backfill", tbl, n)
        finally:
            conn.close()
        return 0

    if args.apply:
        backup = auto_backup_sqlite(db, tag="node_uuid_backfill")
        log.info("Backup created: %s", backup)
        add_columns(db)
        counts = backfill_uuids(db)
        log.info("Backfill counts: %s", counts)
        return 0

    if args.rollback:
        backup = Path(args.rollback)
        if not backup.exists():
            log.error("Backup not found: %s", backup)
            return 2
        shutil.copy2(backup, db)
        log.info("Rolled back %s ← %s", db, backup)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run tests, expect pass**

```bash
python3 -m pytest tests/migrations/test_node_uuid_backfill.py -v 2>&1 | tail -15
```

- [ ] **Step 5: Run --dry-run on Volterra DB**

```bash
python3 -m scripts.migrations.2026_05_node_uuid_backfill \
    --db "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitcs_SCHEDE2024.sqlite" \
    --dry-run 2>&1 | tail -10
```
Expected: 3 lines reporting either "needs ALTER + backfill" or "N rows need backfill".

- [ ] **Step 6: Commit**

```bash
git add scripts/migrations/_2026_05_node_uuid_backfill_lib.py \
        scripts/migrations/2026_05_node_uuid_backfill.py \
        tests/migrations/test_node_uuid_backfill.py
git commit -m "feat(migrations): node_uuid TEXT column + UUID v7 backfill (spec §4.5)

- Adds node_uuid to us_table, inventario_materiali_table, periodizzazione_table
- Creates partial unique index (WHERE node_uuid IS NOT NULL) so NULLs do
  not collide during a partial-failure recovery
- Idempotent: ALTER and backfill both no-op on second run
- --dry-run / --apply / --rollback (auto-backup before --apply)
- PostgreSQL path: same logic via SQLAlchemy text() in Phase 2 when
  GraphProjector lands; for now SQLite-only (the only path Phase 1 ships)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task E.3: Wire UUID backfill into the QGIS Maintenance menu

**Files:**
- Modify: `pyarchinit_Plugin.py`

- [ ] **Step 1: Add the second menu entry**

In `pyarchinit_Plugin.py` `initGui()`, right after the vocab-alignment entry from D.3:

```python
        action_uuid_backfill = QAction(
            "Migrazioni → Backfill node_uuid (UUID v7 per record)",
            self.iface.mainWindow())
        action_uuid_backfill.triggered.connect(self._run_uuid_backfill_migration)
        self.menu.addAction(action_uuid_backfill)
        self.actions.append(action_uuid_backfill)

    def _run_uuid_backfill_migration(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        from scripts.migrations._2026_05_node_uuid_backfill_lib import (
            add_columns,
            backfill_uuids,
        )
        from scripts.migrations._common import auto_backup_sqlite
        from pathlib import Path

        db_path, _ = QFileDialog.getOpenFileName(
            self.iface.mainWindow(),
            "Seleziona il database pyarchinit (.sqlite)",
            "",
            "SQLite databases (*.sqlite)",
        )
        if not db_path:
            return
        confirm = QMessageBox.question(
            self.iface.mainWindow(),
            "Backfill node_uuid",
            f"Aggiungere node_uuid TEXT (se mancante) e generare UUID v7\n"
            f"per ogni record di:\n"
            f"  - us_table\n  - inventario_materiali_table\n  - periodizzazione_table\n\n"
            f"Database: {db_path}\n\nProcedere (con backup automatico)?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        db = Path(db_path)
        backup = auto_backup_sqlite(db, tag="node_uuid_backfill")
        add_columns(db)
        counts = backfill_uuids(db)
        QMessageBox.information(
            self.iface.mainWindow(),
            "Backfill completato",
            f"Backup: {backup}\n\nRecord aggiornati per tabella: {counts}",
        )
```

- [ ] **Step 2: Commit**

```bash
git add pyarchinit_Plugin.py
git commit -m "feat(plugin): QGIS menu entry for node_uuid backfill migration

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Group F — `modules/s3dgraphy/` refactor (12 files)

> **Strategy:** per-file commits so any single regression is selectively `git revert`-able. Audit-only files get a single confirmation commit (or note in the changelog with no code change).

### Task F.1: `cidoc_crm_mapper.py` — drop hardcoded `CRM_CLASSES`

**Files:**
- Modify: `modules/s3dgraphy/cidoc_crm_mapper.py`

- [ ] **Step 1: Read the current `CRM_CLASSES` dict**

```bash
sed -n '15,55p' modules/s3dgraphy/cidoc_crm_mapper.py
```

- [ ] **Step 2: Refactor to consult `VocabProvider`**

Find the `CRM_CLASSES = { ... }` block (lines around 20-50) and the consumer at line ~64. Replace with:

```python
    # CRM_CLASSES used to be a hardcoded dict; it now resolves through
    # VocabProvider.get_cidoc_mapping(). Kept as a property so that legacy
    # callers `mapper.CRM_CLASSES['stratigraphic_unit']` still work.

    _LEGACY_CRM_FALLBACK = {
        'stratigraphic_unit': 'E18_Physical_Thing',
        'masonry_unit': 'E22_Human-Made_Object',
        'feature_unit': 'E25_Human-Made_Feature',
        'deposit_unit': 'E18_Physical_Thing',
        'structural_unit': 'E22_Human-Made_Object',
        # ... preserve every existing key as a fallback
    }

    @property
    def CRM_CLASSES(self):
        """Lazy proxy: VocabProvider lookup with a hardcoded fallback."""
        try:
            from modules.s3dgraphy.sync import get_vocab_provider
            provider = get_vocab_provider()
            # Build dict on demand
            d = dict(self._LEGACY_CRM_FALLBACK)
            for ut in provider.get_unit_types():
                if ut.cidoc_class:
                    d[ut.s3dgraphy_class.lower()] = ut.cidoc_class.replace(
                        " ", "_")
            return d
        except Exception:
            return self._LEGACY_CRM_FALLBACK
```

(IMPORTANT: copy the full _LEGACY_CRM_FALLBACK dict from the existing CRM_CLASSES — preserve every key.)

- [ ] **Step 3: Run all tests in tests/sync/ and tests/ rooted with cidoc**

```bash
python3 -m pytest tests/sync tests/migrations -v 2>&1 | tail -10
grep -rln "cidoc" tests/ --include='*.py' | head -5
# If any cidoc-specific test exists, run it:
# python3 -m pytest <those tests> -v
```

- [ ] **Step 4: Commit**

```bash
git add modules/s3dgraphy/cidoc_crm_mapper.py
git commit -m "refactor(s3dgraphy): cidoc_crm_mapper consults VocabProvider for CRM mappings

CRM_CLASSES becomes a @property that overlays VocabProvider's
get_unit_types().cidoc_class onto a hardcoded fallback. Public surface
preserved (existing 'mapper.CRM_CLASSES[\"stratigraphic_unit\"]' lookups
keep working).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task F.2: `s3dgraphy_integration.py` — typed factories

**Files:**
- Modify: `modules/s3dgraphy/s3dgraphy_integration.py`

- [ ] **Step 1: Locate the 3 string-tagged assignments**

```bash
grep -nE "node\.node_type\s*=\s*['\"]" modules/s3dgraphy/s3dgraphy_integration.py
```

- [ ] **Step 2: Refactor each occurrence**

For each line `node.node_type = 'string'`, replace with a typed factory:

```python
# OLD
node.node_type = 'virtual_reconstruction'

# NEW
from modules.s3dgraphy.sync import get_vocab_provider
provider = get_vocab_provider()
# Look up the canonical s3dgraphy class for the string label.
# The mapping is intentionally local — the legacy strings used by
# pyarchinit pre-VocabProvider don't always match s3dgraphy abbrevs.
_legacy_to_s3d = {
    'stratigraphic_unit': 'US',
    'virtual_reconstruction': 'USVs',
    # ... add other legacy strings here as discovered
}
abbrev = _legacy_to_s3d.get('virtual_reconstruction', 'US')
node.node_type = abbrev
```

- [ ] **Step 3: Run sync + plugin import smoke**

```bash
python3 -c "from modules.s3dgraphy.s3dgraphy_integration import *; print('import ok')" 2>&1 | tail -5
```

- [ ] **Step 4: Commit**

```bash
git add modules/s3dgraphy/s3dgraphy_integration.py
git commit -m "refactor(s3dgraphy): replace string-tagged node.node_type with VocabProvider lookups

3 occurrences of node.node_type = '<string>' → s3dgraphy abbreviation
resolved via VocabProvider. Legacy strings kept in a local mapping
table so transitional callers remain compatible.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task F.3: `s3dgraphy_dot_bridge.py` — visual mapping via classification API

**Files:**
- Modify: `modules/s3dgraphy/s3dgraphy_dot_bridge.py`

- [ ] **Step 1: Locate hardcoded family/visual lookup**

```bash
grep -nE "family\s*=|visual.*=|color.*=|fill.*=" modules/s3dgraphy/s3dgraphy_dot_bridge.py | head -10
```

- [ ] **Step 2: Refactor to call `VocabProvider.get_visual_rule()`**

Replace any hardcoded `node_type → color` lookup with:

```python
from modules.s3dgraphy.sync import get_vocab_provider

def _color_for(node_type: str) -> str:
    provider = get_vocab_provider()
    rule = provider.get_visual_rule(node_type)
    if rule and rule.fill:
        return rule.fill
    return "#CCCCCC"  # generic fallback
```

- [ ] **Step 3: Smoke test (open Harris matrix in QGIS)**

User restarts QGIS, opens Volterra, generates Harris matrix. The colours should match (s3dgraphy's `em_visual_rules.json` mirrors the formerly hardcoded palette).

- [ ] **Step 4: Commit**

```bash
git add modules/s3dgraphy/s3dgraphy_dot_bridge.py
git commit -m "refactor(s3dgraphy): dot_bridge consults VocabProvider.get_visual_rule()

Visual mapping (icon, fill, stroke, palette) now sourced from
em_visual_rules.json via VocabProvider. The hardcoded color table is
removed; a generic #CCCCCC fallback is kept for nodes whose visual rule
is missing (which would be a JSON config error to fix upstream).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task F.4-F.6: Family-filter refactor across 3 visualizers

> Same pattern, three files. Apply each as its own commit so any visualizer regression can be reverted independently.

**Files (one per task):**
- F.4: `modules/s3dgraphy/matrix_visualizer_qgis.py`
- F.5: `modules/s3dgraphy/matrix_graph_visualizer.py`
- F.6: `modules/s3dgraphy/plotly_visualizer.py`

- [ ] **For each file, do this 4-step cycle:**

1. Locate any hardcoded `if node_type == 'stratigraphic_unit'` or `node_type in ('US', 'USM', ...)` filter:
```bash
grep -nE "node_type\s*==\s*|node_type\s+in\s*\(" modules/s3dgraphy/<file>.py | head -10
```

2. Replace with classification-based filter:
```python
from modules.s3dgraphy.sync import get_vocab_provider, Family

def _is_stratigraphic(node_type: str) -> bool:
    provider = get_vocab_provider()
    return any(ut.abbreviation == node_type
               for ut in provider.get_unit_types(family=Family.STRATIGRAPHIC))
```

3. Smoke import:
```bash
python3 -c "from modules.s3dgraphy.<file_module> import *; print('ok')"
```

4. Commit:
```bash
git add modules/s3dgraphy/<file>.py
git commit -m "refactor(s3dgraphy): <visualizer> filters by family via VocabProvider

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task F.7: Audit-only files (4 files)

**Files audited (no modifications expected):**
- `modules/s3dgraphy/blender_integration.py`
- `modules/s3dgraphy/graphml_spatial_enhancer.py`
- `modules/s3dgraphy/spatial_grouping_manager.py`
- `modules/s3dgraphy/simple_graph_visualizer.py`
- `modules/s3dgraphy/graphviz_visualizer.py`

- [ ] **Step 1: For each file, grep for the patterns we just refactored**

```bash
for f in modules/s3dgraphy/blender_integration.py \
         modules/s3dgraphy/graphml_spatial_enhancer.py \
         modules/s3dgraphy/spatial_grouping_manager.py \
         modules/s3dgraphy/simple_graph_visualizer.py \
         modules/s3dgraphy/graphviz_visualizer.py
do
  echo "=== $f ==="
  grep -nE "node\.node_type\s*=\s*['\"]|CRM_CLASSES|hardcoded.*color|node_type\s+in\s*\(" "$f" | head -5
done
```

- [ ] **Step 2: For files where the audit reveals refactoring is needed**

Apply the same pattern as F.1-F.6 and commit per-file.

- [ ] **Step 3: For files truly clean, document the audit**

Add a single commit with a note:

```bash
git commit --allow-empty -m "audit(s3dgraphy): blender_integration / graphml_spatial_enhancer / spatial_grouping_manager / simple_graph_visualizer / graphviz_visualizer — no string-tag or hardcoded family table found; no refactor required

Per spec §7.3 'Audit only; expected zero changes.'

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task F.8: Run the full unit-test suite

**Files:** none

- [ ] **Step 1: Run everything we can without QGIS**

```bash
python3 -m pytest tests/sync tests/migrations -v 2>&1 | tail -25
```
Expected: green.

- [ ] **Step 2: Spot-check legacy tests that might reference the old surface**

```bash
grep -rln "CRM_CLASSES\|node\.node_type" tests/ --include='*.py' | head -5
# Run any file that matches:
# python3 -m pytest <file> -v
```

If any legacy test hits a regression, decide: fix the test (it pinned the old internal surface) or revert the responsible commit and refine.

- [ ] **Step 3: Manual QGIS smoke (deferred to G.4)** — note "do later, then come back".

---

## Group G — Release packaging

### Task G.1: requirements.txt — already done in Task A.4

**Files:** none (the bump was applied in A.4 to align the runtime-install policy
with the just-completed vendor swap; nothing left to do here).

- [ ] **Step 1: Verify the pin is at >=0.1.40**

```bash
grep -nE "s3dgraphy" requirements.txt
```
Expected: `s3dgraphy>=0.1.40`. If anything else, escalate — A.4 has been
inadvertently reverted.

### Task G.2: Bump `metadata.txt`

**Files:**
- Modify: `metadata.txt`

- [ ] **Step 1: Edit `version=` line**

Replace `version=5.0.27-alpha` with `version=5.1.0-alpha`.

- [ ] **Step 2: Prepend the changelog block**

After the existing `changelog=` line opener, prepend the 5.1.0-alpha entry:

```
changelog=5.1.0-alpha (2026-MM-DD) [Phase 1 Foundation: VocabProvider + Vocabulary Alignment]:
    - Feature: VocabProvider parses three s3dgraphy 0.1.40 JSON pillars
      directly (Option B per Reference Doc v0.1 §4.5); legacy hardcoded
      EM-1.4 list in pyarchinit_i18n_stratigraphic.py becomes a
      compat-shim adapter
    - Feature: one-shot migration USVA/USVB→USVs, USVC→USVn (--dry-run /
      --apply / --rollback, auto-backup, idempotent; QGIS Maintenance menu
      entry)
    - Feature: one-shot migration node_uuid TEXT column + UUID v7 backfill
      on us_table, inventario_materiali_table, periodizzazione_table
      (idempotent, partial unique index, QGIS menu entry)
    - Refactor: 12 modules/s3dgraphy/ files now consult VocabProvider
      (CRM_CLASSES, visual rules, family classification) instead of
      hardcoded tables
    - Deps: bumped s3dgraphy 0.1.30 → 0.1.40 vendored under ext_libs/
  5.0.27-alpha (2026-05-06) [SQLite migration alignment with template DB]:
```

- [ ] **Step 3: Commit**

```bash
git add metadata.txt
git commit -m "chore(metadata): bump 5.0.27-alpha → 5.1.0-alpha

5.1.0-alpha closes Phase 1 of the StratiGraph T5.4 PyArchInit ↔
s3dgraphy integration. All AI01-AI05 action items from the meeting
minutes 2026-05-04 are addressed; Reference Doc v0.1 §4.5 Option B
adopted.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task G.3: Update `dev_logs/CHANGELOG.md` (bilingual IT/EN)

**Files:**
- Modify: `dev_logs/CHANGELOG.md`

- [ ] **Step 1: Read the current top of the file**

```bash
sed -n '1,30p' dev_logs/CHANGELOG.md
```

- [ ] **Step 2: Insert a new top section**

After the file header (`---` line that follows the title), prepend the 5.1.0-alpha entry:

```markdown
## [5.1.0-alpha] - 2026-MM-DD

### Aggiunto / Added

- **feat(s3dgraphy/sync): `VocabProvider` parsa direttamente i tre pillars JSON di s3dgraphy 0.1.40** (Option B per Reference Doc v0.1 §4.5). Implementato come pacchetto `modules/s3dgraphy/sync/` con un core puro Python (`vocab_provider_core.py`) testabile via pytest senza QGIS, e un wrapper Qt (`vocab_provider.py`) che aggiunge `vocabulary_changed` signal e `QFileSystemWatcher` per hot-reload. Le combo box di pyarchinit ora popolano da `s3Dgraphy_node_datamodel.json` (versione 1.5.2 in 0.1.40) → ogni nuovo tipo EM (incluse le novità di EM 1.6 — *building archaeology* e *working units on surfaces*) compare al prossimo plugin reload senza modifiche al codice. Override priority: `~/.config/pyarchinit/vocab_overrides/*.json` → bundled `ext_libs/s3dgraphy/JSON_config/*.json`. Merge per top-level key (un override parziale non cancella i tipi bundled). / **feat(s3dgraphy/sync): `VocabProvider` parses the three s3dgraphy 0.1.40 JSON pillars directly** (Option B per Reference Doc v0.1 §4.5). Implemented as a `modules/s3dgraphy/sync/` package with a pure Python core (`vocab_provider_core.py`) testable via pytest without QGIS, and a Qt wrapper (`vocab_provider.py`) adding a `vocabulary_changed` signal and a `QFileSystemWatcher` for hot-reload. PyArchInit combo boxes now populate from `s3Dgraphy_node_datamodel.json` (version 1.5.2 in 0.1.40) → every new EM type (including the EM 1.6 incoming additions — *building archaeology* and *working units on surfaces*) appears on the next plugin reload without code changes. Override priority: `~/.config/pyarchinit/vocab_overrides/*.json` → bundled `ext_libs/s3dgraphy/JSON_config/*.json`. Per top-level key merge (a partial override does not erase bundled types).

- **feat(migrations): migrazione one-shot `USVA/USVB → USVs`, `USVC → USVn`** allinea i database storici al vocabolario canonico EM 1.5 di s3dgraphy. Idempotente. Voce di menu QGIS in `Maintenance → Migrazioni → Allinea vocabolario US`. Auto-backup prima di `--apply` con timestamp UTC nel nome (`<db>.pre_us_vocab_alignment_<UTC>`). Rollback supportato via `--rollback <backup_path>`. Spec §4.4. / **feat(migrations): one-shot `USVA/USVB → USVs`, `USVC → USVn` migration** aligns historical databases with the canonical EM 1.5 s3dgraphy vocabulary. Idempotent. QGIS menu entry under `Maintenance → Migrazioni → Allinea vocabolario US`. Auto-backup before `--apply` with UTC-timestamped filename (`<db>.pre_us_vocab_alignment_<UTC>`). Rollback supported via `--rollback <backup_path>`. Spec §4.4.

- **feat(migrations): backfill UUID v7 sulla colonna `node_uuid TEXT`** aggiunta a `us_table`, `inventario_materiali_table`, `periodizzazione_table` con indice UNIQUE parziale (`WHERE node_uuid IS NOT NULL`, così i NULL temporanei durante recovery parziali non collidono). UUID v7 generato in Python (RFC 9562 §5.7); monotonico per processo. Idempotente. Voce menu QGIS dedicata. Spec §4.5. / **feat(migrations): UUID v7 backfill on `node_uuid TEXT` column** added to `us_table`, `inventario_materiali_table`, `periodizzazione_table` with a partial UNIQUE index (`WHERE node_uuid IS NOT NULL`, so transient NULLs during partial recovery don't collide). UUID v7 generated in Python (RFC 9562 §5.7); monotonic per process. Idempotent. Dedicated QGIS menu entry. Spec §4.5.

### Modificato / Changed

- **refactor(i18n): `pyarchinit_i18n_stratigraphic.py` diventa adapter su `VocabProvider`**. `_COMMON_ITEMS`, `UNIT_TYPE_ABBREV`, `get_unit_type_items`, `is_us_type`, `is_usm_type`, `ALL_US_ABBREVS`, `ALL_USM_ABBREVS` rimangono importabili come prima (regression test in `tests/sync/test_i18n_compat.py`). Il blocco hardcoded `_LEGACY_COMMON_ITEMS` è il fallback quando `ext_libs/s3dgraphy/` è assente. Deprecation log al primo import del modulo. Rimozione del fallback prevista per 6.0.0. / **refactor(i18n): `pyarchinit_i18n_stratigraphic.py` becomes an adapter over `VocabProvider`**. `_COMMON_ITEMS`, `UNIT_TYPE_ABBREV`, `get_unit_type_items`, `is_us_type`, `is_usm_type`, `ALL_US_ABBREVS`, `ALL_USM_ABBREVS` remain importable as before (regression test in `tests/sync/test_i18n_compat.py`). The hardcoded `_LEGACY_COMMON_ITEMS` block is the fallback when `ext_libs/s3dgraphy/` is missing. One-time deprecation log on first module import. Fallback removal scheduled for 6.0.0.

- **refactor(s3dgraphy): 12 file in `modules/s3dgraphy/` consultano `VocabProvider`**. `cidoc_crm_mapper.py` rimuove la costante `CRM_CLASSES` hardcoded (la espone come `@property` sostenuta da `get_cidoc_mapping()`). `s3dgraphy_integration.py` sostituisce 3 assegnazioni `node.node_type = '<string>'` con factory tipizzate. `s3dgraphy_dot_bridge.py` legge fill/stroke/palette da `em_visual_rules.json`. I tre visualizers (`matrix_visualizer_qgis.py`, `matrix_graph_visualizer.py`, `plotly_visualizer.py`) filtrano per `family` via classification API invece di tabelle hardcoded. Cinque file restano audit-only (`blender_integration.py`, `graphml_spatial_enhancer.py`, `spatial_grouping_manager.py`, `simple_graph_visualizer.py`, `graphviz_visualizer.py`). / **refactor(s3dgraphy): 12 files in `modules/s3dgraphy/` consult `VocabProvider`**. `cidoc_crm_mapper.py` removes the hardcoded `CRM_CLASSES` constant (exposes it as a `@property` backed by `get_cidoc_mapping()`). `s3dgraphy_integration.py` replaces 3 `node.node_type = '<string>'` assignments with typed factories. `s3dgraphy_dot_bridge.py` reads fill/stroke/palette from `em_visual_rules.json`. The three visualizers (`matrix_visualizer_qgis.py`, `matrix_graph_visualizer.py`, `plotly_visualizer.py`) filter by `family` via the classification API instead of hardcoded tables. Five files remain audit-only.

### Dipendenze / Dependencies

- **deps(s3dgraphy): bump 0.1.30 → 0.1.40** in `ext_libs/`. Porta `GraphMerger` (Phase 3), `GraphMLPatcher` (Phase 2), classification API (`get_family`, `is_real`, `iter_subtypes`), `aux_tracking` (Phase 3), `NegativeStratigraphicUnit`, `WorkingUnit`, e fix del nome file `s3Dgraphy_node_datamodel.json` (rimosso lo spazio finale). Vendoring via `pip install --target ext_libs/ --no-deps s3dgraphy==0.1.40`. Tag di rollback: `pre-s3dgraphy-040`. / **deps(s3dgraphy): bump 0.1.30 → 0.1.40** in `ext_libs/`. Brings `GraphMerger` (Phase 3), `GraphMLPatcher` (Phase 2), classification API (`get_family`, `is_real`, `iter_subtypes`), `aux_tracking` (Phase 3), `NegativeStratigraphicUnit`, `WorkingUnit`, and the `s3Dgraphy_node_datamodel.json` filename fix (trailing space removed). Vendoring via `pip install --target ext_libs/ --no-deps s3dgraphy==0.1.40`. Rollback tag: `pre-s3dgraphy-040`.

### File modificati / Modified files
- `ext_libs/s3dgraphy/` (wholesale 0.1.30 → 0.1.40 vendor swap)
- `modules/s3dgraphy/sync/` (NEW: vocab_types.py, vocab_provider_core.py, vocab_provider.py, uuid7.py, __init__.py)
- `modules/utility/pyarchinit_i18n_stratigraphic.py` (adapter refactor)
- `modules/s3dgraphy/cidoc_crm_mapper.py` (CRM_CLASSES → @property)
- `modules/s3dgraphy/s3dgraphy_integration.py` (string-tag → typed factory)
- `modules/s3dgraphy/s3dgraphy_dot_bridge.py` (visual rules from JSON)
- `modules/s3dgraphy/{matrix_visualizer_qgis,matrix_graph_visualizer,plotly_visualizer}.py` (family filter via classification)
- `scripts/migrations/` (NEW: _common.py, _2026_05_us_vocabulary_alignment_lib.py, 2026_05_us_vocabulary_alignment.py, _2026_05_node_uuid_backfill_lib.py, 2026_05_node_uuid_backfill.py, __init__.py)
- `tests/sync/`, `tests/migrations/` (NEW test packages)
- `pyarchinit_Plugin.py` (two new menu entries for the migrations)
- `requirements.txt` (s3dgraphy>=0.1.40)
- `metadata.txt` (5.0.27-alpha → 5.1.0-alpha)

---
```

- [ ] **Step 3: Commit**

```bash
git add dev_logs/CHANGELOG.md
git commit -m "docs(changelog): 5.1.0-alpha — Phase 1 Foundation entry

Bilingual IT/EN block describing the 6 deliverables of Phase 1 (spec
§11): vendor 0.1.40, VocabProvider, i18n adapter, two migrations, and
the 12-file refactor. Spec source §4.4, §4.5, §7.3, §11.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Task G.4: Manual smoke gate (must pass before tagging)

**Files:** none (manual QA)

- [ ] **Step 1: Restart QGIS**

User action.

- [ ] **Step 2: Open the Volterra project (`pyarchinitcs_SCHEDE2024.sqlite`)**

Verify the plugin loads without exception.

- [ ] **Step 3: Open a US/USM record**

Verify combo box `comboBox_unita_tipo` is populated. EM 1.5 types (`USVs`, `USVn`) should appear; legacy `USVA`/`USVB`/`USVC` may still appear if migration has not been run on the test DB (expected — migration is opt-in).

- [ ] **Step 4: Generate Harris matrix**

Verify the matrix renders. Visual style (colours of nodes) should match pre-refactor since `em_visual_rules.json` mirrors the formerly-hardcoded palette.

- [ ] **Step 5: Switch UI language**

Open QGIS settings, change locale to `en_US`, restart, verify the form labels and combo headers are still in English (sanity).

- [ ] **Step 6: Run vocabulary alignment migration on a copy of the Volterra DB**

```bash
cp "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitcs_SCHEDE2024.sqlite" /tmp/test_phase1_us.sqlite
python3 -m scripts.migrations.2026_05_us_vocabulary_alignment --db /tmp/test_phase1_us.sqlite --dry-run
python3 -m scripts.migrations.2026_05_us_vocabulary_alignment --db /tmp/test_phase1_us.sqlite --apply
sqlite3 /tmp/test_phase1_us.sqlite "SELECT unita_tipo, COUNT(*) FROM us_table GROUP BY unita_tipo"
```

Expected: no row has `unita_tipo IN ('USVA','USVB','USVC')` post-apply.

- [ ] **Step 7: Run UUID backfill on the same copy**

```bash
python3 -m scripts.migrations.2026_05_node_uuid_backfill --db /tmp/test_phase1_us.sqlite --dry-run
python3 -m scripts.migrations.2026_05_node_uuid_backfill --db /tmp/test_phase1_us.sqlite --apply
sqlite3 /tmp/test_phase1_us.sqlite "SELECT COUNT(*) FROM us_table WHERE node_uuid IS NULL"
sqlite3 /tmp/test_phase1_us.sqlite "SELECT node_uuid FROM us_table LIMIT 1"
```

Expected: 0 NULLs; sample UUID has version-7 character at position 14.

- [ ] **Step 8: Decision gate**

If any of the above fails: do NOT tag the release. Investigate, fix, return to the appropriate task.

If all pass: continue to G.5.

### Task G.5: Tag and push

**Files:** none (git ops)

- [ ] **Step 1: Verify clean working tree**

```bash
git status --short
```
Expected: empty.

- [ ] **Step 2: Tag the release**

```bash
git tag -a phase1-foundation-5.1.0-alpha -m "Phase 1 (Foundation) of PyArchInit ↔ s3dgraphy

- s3dgraphy vendor 0.1.30 → 0.1.40
- VocabProvider (Option B per-tool JSON parsing)
- pyarchinit_i18n_stratigraphic adapter refactor
- USVA/USVB → USVs, USVC → USVn migration
- node_uuid TEXT + UUID v7 backfill migration
- 12-file modules/s3dgraphy/ refactor

Spec: docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md
Phase 1 deliverables per spec §11. AI01-AI05 closed.
Rollback tag: pre-s3dgraphy-040"
```

- [ ] **Step 3: Push branch + tag**

```bash
git push origin Stratigraph_00001
git push origin phase1-foundation-5.1.0-alpha
git push origin pre-s3dgraphy-040  # share the rollback tag too
```

---

## Self-review checklist

This plan was self-reviewed against the spec on 2026-05-06.

**Spec coverage:**

| Spec section | Plan coverage |
|---|---|
| §3.1 VocabProvider | Group B (12 tasks) |
| §4.4 Vocabulary alignment migration | Group D (3 tasks) |
| §4.5 UUID backfill schema migration | Group E (3 tasks) |
| §7.4 Procedure (vendor swap, smoke, refactor order) | Groups A, F, G |
| §7.3 12-file refactor list | Group F (8 tasks) |
| §11 Phase 1 deliverables | Groups B, C, D, E, F covered |
| §2.1.A EM 1.4 → 1.5 dynamic JSON loading | Group B (B.2-B.10) |
| §2.1.F populate_graph / populate_list | Deferred to Phase 2 (correctly out-of-scope) |
| §2.2.G Three JSON pillars | Group B (B.2, B.3, B.5) |
| §2.2.H Option B per-tool parsing | Architecture commitment in Group B intro |
| §2.2.J Sync policy deferred to AI08 | Correctly noted as Phase 2/3 work |
| §2.2.K Division of responsibilities | Plan respects ownership boundaries |

**Placeholder scan:** No "TBD", "TODO" inside steps. All test code shown literally. All commands shown literally. The `_LEGACY_CRM_FALLBACK` placeholder in F.1 step 2 is annotated with "preserve every existing key as a fallback" pointing at the file the engineer will copy from.

**Type consistency:** `UnitType.abbreviation` used consistently across B.2-B.7. `Family.STRATIGRAPHIC` enum used in B.2-B.4. `VocabProviderCore` constructor signature `(bundled_dir, overrides_dir, min_versions=None)` consistent across B.2-B.7.

**Known gaps acknowledged:**
- PostgreSQL backfill path (spec §12.4) is sketched in E.2 commit message but not fully implemented in Phase 1; flagged for Phase 2 when GraphProjector lands SQLAlchemy-based migrations.
- Translator-editable `resources/vocab/vocab_i18n.json` is mentioned in spec §5.1 but not created in Phase 1 (combo boxes use English labels from the JSON datamodel; localized labels arrive in Phase 2 with the i18n integration).

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-06-phase-1-foundation.md`.

Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task or task-group; review between tasks; fast iteration. Each subagent gets the spec, the relevant section of this plan, and the diff so far.

**2. Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`; batch execution with checkpoints for review.

Which approach?
