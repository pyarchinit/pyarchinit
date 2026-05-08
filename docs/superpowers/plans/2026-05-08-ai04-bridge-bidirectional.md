# AI04 — Bridge bidirezionale PyArchInit ↔ s3dgraphy: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the bidirectional library bridge between PyArchInit SQL tables and the s3dgraphy in-memory `Graph` model. Adds `GraphProjector` (DB → Graph), `GraphIngestor` (Graph → DB), `ConflictResolver` stub, a CLI helper, and an Import tab in the existing AI03 dialog. Closes T5.4 meeting action item AI04 ("bridge prototype") and Reference Document v0.1 §6 macro-functions.

**Architecture:** Strategy D wrap pattern — `GraphProjector` is a thin wrapper around the existing `_enrich_pyarchinit_graph()` from `modules/s3dgraphy/sync/graphml_writer.py` (no logic duplication, no AI03 regression). `GraphIngestor` is full new implementation: validates input, opens a single SQLite transaction, runs UPDATE selettivo on mapped columns + INSERT on new rows, supports dry-run preview, atomic-only failure mode. `ConflictResolver` is a stub (always returns `GRAPH_WINS`) to lock the API surface for AI06+. CLI helper at `scripts/s3dgraphy_sync.py` with `export` / `import` subcommands; import default is dry-run, `--apply` required for writes. UI integration adds a `QTabWidget` to `S3DGraphyExportDialog` with the existing Export tab untouched.

**Tech Stack:** Python 3.9+, s3dgraphy 0.1.40 (vendored in `ext_libs/s3dgraphy/`), lxml (transitive dep of s3dgraphy), pytest (existing `tests/sync/` scope), QGIS PyQt5/PyQt6 abstraction (existing). **No new third-party dependencies.**

**Spec source of truth:** `docs/superpowers/specs/2026-05-08-ai04-bridge-bidirectional-design.md`

**Reference docs (already in repo):**
- `docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md` (parent, §3.2 / §3.6 / §3.7 / §11)
- `docs/superpowers/specs/2026-05-07-ai03-graphml-delegation-design.md` (predecessor, AI03 — shipped as tag `phase2-ai03-graphml-delegation-5.2.0-alpha`)
- `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` (Phase 2 / AI03 section)

**Memory notes (consult before refactoring):**
- `~/.claude/projects/.../memory/project_ai04_projector_refactor_plan.md` — Strategy D thin wrap, promotion to A in AI05+
- `~/.claude/projects/.../memory/project_ai04_failure_mode_followup.md` — atomic only now, configurable later
- `~/.claude/projects/.../memory/feedback_no_claude_coauthor.md` — never include `Co-Authored-By: Claude` trailers

**Commit-message rule:** Never include `Co-Authored-By: Claude …` trailers. Sole author of every commit is Enzo Cocca. Every HEREDOC in this plan is already trailer-free; do not re-add it. After each commit run `git log -1 --format=%B HEAD | grep -c Co-Authored-By` — must return `0`.

---

## File Structure

### Created

| Path | Responsibility |
|---|---|
| `modules/s3dgraphy/sync/ingest_result.py` | `IngestResult` and `ConflictRecord` frozen dataclasses + `ConflictResolution` enum. Pure dataclasses — no I/O, no Qt. |
| `modules/s3dgraphy/sync/conflict_resolver.py` | `ConflictResolver` stub class. Always returns `ConflictResolution.GRAPH_WINS`. Interface ready for AI06+ pluggable strategies. |
| `modules/s3dgraphy/sync/graph_projector.py` | `GraphProjector` class with `populate_graph(db_path, sito) -> s3dgraphy.Graph`. Thin wrapper around `_enrich_pyarchinit_graph`. Defines `ProjectionError`. |
| `modules/s3dgraphy/sync/graph_ingestor.py` | `GraphIngestor` class with `populate_list(graph, db_path, sito, *, dry_run, create_missing_epochs) -> IngestResult`. Atomic transaction. Full exception hierarchy: `GraphSyncError`, `GraphIngestError`, `SchemaMismatchError`, `UnknownUnitaTipoError`, `SiteMismatchError`, `MissingEpochError`. Module-level constant `MAPPED_COLUMNS`. |
| `scripts/s3dgraphy_sync.py` | argparse CLI with `export` / `import` subcommands. Import default is dry-run; `--apply` required for write. Exit 0 success, 1 on `GraphSyncError`. |
| `tests/sync/test_ingest_result.py` | Unit tests for IngestResult, ConflictRecord, ConflictResolution: frozen dataclass invariants. |
| `tests/sync/test_conflict_resolver.py` | Unit test: stub always returns `GRAPH_WINS`. |
| `tests/sync/test_graph_projector.py` | Pins D2 (wrap pattern) + D6 (mandatory sito) + AC-1 (returns non-empty graph filtered by sito). |
| `tests/sync/test_graph_ingestor.py` | All exception-raising paths + dry-run no-write + UPDATE selettivo + atomic rollback. Pins D3 (selettivo + dry-run) + D5 (epoch policy) + D6 (sito mismatch) + D8 (atomic). |
| `tests/sync/test_round_trip.py` | L1 fixture-based: `test_round_trip_preserves_mapped_fields`. Pins D4-B (AC-6). |
| `tests/sync/test_idempotent_ingest.py` | L1 fixture-based: `test_external_graph_ingest_idempotent` (3 runs converge). Pins D4-C (AC-7). |
| `tests/sync/test_cli_helper.py` | L2 subprocess-based tests on `scripts/s3dgraphy_sync.py`. Pins AC-10 (--apply required). |
| `tests/sync/test_ai03_export_byte_identical.py` | The non-regression guard. Pins AC-2: AI03 export pipeline produces a graphml whose canonical normalisation matches the committed pre-AI04 baseline. |
| `tests/sync/fixtures/mini_volterra_baseline_ai03.graphml` | Captured in Group 0 as the AI03 reference output before any AI04 code lands. Plain text (UTF-8 GraphML), checked into git. |
| `tests/sync/fixtures/build_mini_volterra_external.py` | Generator script that emits `mini_volterra_external.graphml` and `mini_volterra_external_with_new_epoch.graphml` from `mini_volterra.sqlite`. Idempotent. |
| `tests/sync/fixtures/mini_volterra_external.graphml` | Pre-cooked input for ingest tests: 3 stratigraphic nodes (1 with new node_uuid + 2 colliding with mini_volterra) + 1 epoch matching mini_volterra. Forces a `ConflictRecord` on `d_stratigrafica`. Generated by build script, committed binary. |
| `tests/sync/fixtures/mini_volterra_external_with_new_epoch.graphml` | Pre-cooked input for D5-B test: 1 stratigraphic node + 1 EpochNode NOT in mini_volterra. Generated by build script, committed binary. |

### Modified

| Path | Why |
|---|---|
| `modules/s3dgraphy/sync/graphml_writer.py:206` | Add `sito_filter: Optional[str] = None` kwarg to `_enrich_pyarchinit_graph()`. When non-None, append `WHERE sito = ?` to the `SELECT … FROM us_table` query. Default `None` preserves the AI03 call site (no SQL change). |
| `modules/s3dgraphy/s3dgraphy_dot_bridge.py` (the `S3DGraphyExportDialog` class around line 293) | Wrap the existing single-tab body inside a `QTabWidget` with two tabs: "Export" (existing widgets, untouched logic) and "Import" (new widgets + new handler). Zero diff on the Export logic; verified by AC-2 byte-identical baseline + AC-11 manual smoke gate. |
| `metadata.txt` | Bump `version=5.2.0-alpha` → `version=5.3.0-alpha`. Prepend `Phase 2 / AI04` changelog blurb. |
| `dev_logs/CHANGELOG.md` | Prepend `## [5.3.0-alpha] - 2026-MM-DD` bilingual section listing the 3 new components (Projector, Ingestor, ConflictResolver stub) + UI Import tab + CLI helper. |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | New "Phase 2 — AI04 Bridge bidirectional" section listing acceptance criteria status + smoke gate result. |

### Explicitly NOT touched (out of scope per spec §9)

- `modules/s3dgraphy/sync/graphml_writer.py:_enrich_pyarchinit_graph` body (other than the new kwarg) — the wrap pattern (D2) requires zero refactoring of the existing logic.
- `modules/s3dgraphy/sync/graphml_writer.py::export_graphml()` — the AI03 entry point. AC-2 enforces byte-identical output.
- `requirements.txt` — no new dependencies.
- `gui/dialog_s3dgraphy_export.py` — no such file (the dialog lives inside `modules/s3dgraphy/s3dgraphy_dot_bridge.py`; do not move it).
- `_filter_by_site()` helper at `graphml_writer.py:61` — still used by `export_graphml()`. Leave as is.
- `paradata.graphml` per project — deferred to AI05.

---

## Test strategy

- **L0 unit tests** (`test_ingest_result.py`, `test_conflict_resolver.py`, parts of `test_graph_projector.py` + `test_graph_ingestor.py`): pure pytest, no QGIS, no DB. Run with `pytest tests/sync/`.
- **L1 fixture-based pipeline** (`test_graph_projector.py`, `test_graph_ingestor.py`, `test_round_trip.py`, `test_idempotent_ingest.py`, `test_ai03_export_byte_identical.py`): pytest against `mini_volterra.sqlite` + the new `.graphml` fixtures. No QGIS bootstrap.
- **L2 CLI subprocess** (`test_cli_helper.py`): runs `python scripts/s3dgraphy_sync.py …` via `subprocess.run()` and asserts on exit code + stdout/stderr.

Decision-pinning matrix (each row = one D-id × one acceptance test):

| Decision / Acceptance | Test |
|---|---|
| D2 wrap pattern | `test_graph_projector.py::test_projector_delegates_to_enrich_function` |
| D3 dry-run no writes | `test_graph_ingestor.py::test_populate_list_dry_run_no_writes` |
| D3 UPDATE selettivo | `test_graph_ingestor.py::test_update_preserves_unmapped_columns` |
| D4-B semantic round-trip | `test_round_trip.py::test_round_trip_preserves_mapped_fields` |
| D4-C idempotent | `test_idempotent_ingest.py::test_external_graph_ingest_idempotent` |
| D5-A strict default | `test_graph_ingestor.py::test_missing_epoch_strict_raises` |
| D5-B opt-in create | `test_graph_ingestor.py::test_missing_epoch_create_inserts_period` |
| D6 sito mandatory + mismatch | `test_graph_projector.py::test_populate_graph_requires_sito`, `test_graph_ingestor.py::test_site_mismatch_raises` |
| D8 atomic | `test_graph_ingestor.py::test_populate_list_atomic_on_failure` |
| AC-1 non-empty graph filtered | `test_graph_projector.py::test_projector_returns_filtered_graph` |
| AC-2 regression guard | `test_ai03_export_byte_identical.py::test_export_graphml_matches_baseline` |
| AC-10 CLI --apply required | `test_cli_helper.py::test_cli_import_dry_run_default` |

The Phase 1 + AI03 test suite (`tests/sync/`, `tests/migrations/`) must stay green at every commit. Run `pytest tests/sync/ tests/migrations/ -q` after every task.

---

## Group 0 — Pre-flight & rollback safety

### Task 0.1: Push the AI04 spec doc commit (currently unpushed)

**Files:** none (git operation)

- [ ] **Step 1: Confirm starting point**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git status --short | grep -vE '^\?\?'   # tracked-changes only — must be empty
git log --oneline -3
git rev-list --left-right --count HEAD...@{u}   # expected: "1\t0" (spec doc unpushed)
```

Expected last 3 commits include `84ae66f5 docs(spec): AI04 …`.

- [ ] **Step 2: Push the spec commit so the rollback tag points to a published commit**

```bash
git push origin Stratigraph_00001
```

Expected: `Stratigraph_00001 -> Stratigraph_00001` plus 1 commit pushed.

- [ ] **Step 3: Verify**

```bash
git rev-list --left-right --count HEAD...@{u}   # expected: "0\t0"
```

### Task 0.2: Create AI04 rollback tag

**Files:** none (git operation)

- [ ] **Step 1: Create annotated tag at current HEAD**

```bash
git tag -a pre-ai04-bridge -m "Pre-flight rollback tag for AI04 / phase2 bridge bidirectional"
git tag -l | grep -E "pre-ai04|phase2"
```

Expected output:
```
phase2-ai03-graphml-delegation-5.2.0-alpha
pre-ai03-graphml-delegation
pre-ai04-bridge
```

- [ ] **Step 2: Push the tag**

```bash
git push origin pre-ai04-bridge
git ls-remote --tags origin 2>&1 | grep "refs/tags/pre-ai04-bridge$"
```

Expected: a single matching line (the tag commit hash on the remote).

### Task 0.3: Capture the AI03 byte-identical baseline GraphML

**Files:**
- Create: `tests/sync/fixtures/mini_volterra_baseline_ai03.graphml`
- Create: `tests/sync/test_ai03_export_byte_identical.py`

This task captures the OUTPUT of the AI03 pipeline against `mini_volterra.sqlite` BEFORE any AI04 code lands, and writes a regression test that asserts the same output after AI04 lands. Together they enforce AC-2.

- [ ] **Step 1: Generate the baseline by running the existing AI03 export**

Create a helper script `tests/sync/fixtures/_capture_ai03_baseline.py` (single-use, NOT committed):

```python
"""Run AI03 export pipeline on mini_volterra.sqlite and write the
resulting GraphML to mini_volterra_baseline_ai03.graphml.

This script runs ONCE at AI04 Group 0 to capture the regression
baseline. After that, test_ai03_export_byte_identical.py uses
the committed file. The script itself is NOT committed.
"""
from __future__ import annotations
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLUGIN_ROOT / "ext_libs"))
import pandas  # noqa: F401  — pin system pandas
from lxml import etree as _etree  # noqa: F401

# Evict any pre-loaded older s3dgraphy from sys.modules
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

from modules.s3dgraphy.sync.graphml_writer import export_graphml

FIXTURES = PLUGIN_ROOT / "tests" / "sync" / "fixtures"
src = FIXTURES / "mini_volterra.sqlite"
out = FIXTURES / "mini_volterra_baseline_ai03.graphml"

result = export_graphml(
    db_path=src,
    mapping="pyarchinit_us_mapping",
    output_path=out,
)
print(f"OK — {out.name} ({out.stat().st_size} bytes)")
print(f"   {result.node_count} nodes, {result.edge_count} edges, "
      f"{result.epoch_count} epochs, "
      f"{result.tred_removed_edges} redundancies removed")
```

Run it:

```bash
python tests/sync/fixtures/_capture_ai03_baseline.py
ls -la tests/sync/fixtures/mini_volterra_baseline_ai03.graphml
```

Expected output: `OK — mini_volterra_baseline_ai03.graphml (~30000-60000 bytes)` and a non-empty file. Delete the helper after capture:

```bash
rm tests/sync/fixtures/_capture_ai03_baseline.py
```

- [ ] **Step 2: Write the regression guard test**

Create `tests/sync/test_ai03_export_byte_identical.py`:

```python
"""AC-2 regression guard: AI03 export pipeline must keep producing
GraphML byte-identical (modulo line endings and trailing whitespace)
to the pre-AI04 baseline captured at Group 0 of the AI04 plan.

If this test ever goes red, AI04 has regressed AI03 — block on it.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

import pandas  # noqa: F401
from lxml import etree as _etree  # noqa: F401
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")
BASELINE = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
            / "mini_volterra_baseline_ai03.graphml")


def _normalise(text: str) -> str:
    """Strip volatile bits: line endings, trailing whitespace,
    UUID-like ids that the writer regenerates per run."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "<UUID>",
        text,
    )
    return text.strip()


def test_export_graphml_matches_baseline(tmp_path):
    import shutil
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    db = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, db)
    out = tmp_path / "out.graphml"
    export_graphml(db_path=db, mapping="pyarchinit_us_mapping",
                   output_path=out)
    actual = _normalise(out.read_text(encoding="utf-8"))
    baseline = _normalise(BASELINE.read_text(encoding="utf-8"))
    assert actual == baseline, (
        f"AI03 GraphML output drifted from baseline "
        f"(actual={len(actual)} chars, baseline={len(baseline)} chars). "
        f"AI04 has regressed AI03 — investigate."
    )
```

- [ ] **Step 3: Run the test to verify it passes against the captured baseline**

```bash
pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: `1 passed`.

- [ ] **Step 4: Run the full sync test suite to confirm zero regression**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `60 passed` (was 59 + the new regression test).

- [ ] **Step 5: Commit**

```bash
git add tests/sync/test_ai03_export_byte_identical.py \
        tests/sync/fixtures/mini_volterra_baseline_ai03.graphml
git commit -m "$(cat <<'EOF'
test(graphml_writer): AI03 byte-identical baseline + regression guard

Captures the AI03 export pipeline output on mini_volterra.sqlite as
tests/sync/fixtures/mini_volterra_baseline_ai03.graphml (committed
text fixture).

Adds tests/sync/test_ai03_export_byte_identical.py asserting that
future runs of export_graphml() produce a normalised GraphML
identical to the baseline. UUID-like ids are regex-stripped from
both sides because the s3dgraphy writer assigns fresh UUIDs each
run; line endings and trailing whitespace are normalised so
test reproducibility does not depend on git core.autocrlf.

This is AC-2 from the AI04 spec: the regression guard for the AI03
pipeline. Block on it during AI04 Groups B–G.

Tests: 60/60 pass.
EOF
)"
```

### Task 0.4: Bump version to 5.3.0-alpha

**Files:**
- Modify: `metadata.txt`

- [ ] **Step 1: Read current metadata.txt**

```bash
grep -n "version" metadata.txt | head -3
```

Expected: a line `version=5.2.0-alpha`.

- [ ] **Step 2: Edit metadata.txt — bump version**

Use the Edit tool to change exactly the `version=5.2.0-alpha` line to `version=5.3.0-alpha`. Do not touch the changelog blurb yet (that goes in Group H).

- [ ] **Step 3: Verify**

```bash
grep "^version=" metadata.txt
```

Expected: `version=5.3.0-alpha`.

- [ ] **Step 4: Run sanity tests**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `60 passed`.

- [ ] **Step 5: Commit**

```bash
git add metadata.txt
git commit -m "$(cat <<'EOF'
chore(metadata): bump version to 5.3.0-alpha for AI04

Phase 2 / AI04 (bridge bidirezionale PyArchInit ↔ s3dgraphy).
Target tag: phase2-ai04-bridge-bidirectional-5.3.0-alpha.

Spec: docs/superpowers/specs/2026-05-08-ai04-bridge-bidirectional-design.md
Plan: docs/superpowers/plans/2026-05-08-ai04-bridge-bidirectional.md
EOF
)"
```

---

## Group A — Dataclasses + ConflictResolver stub + exception hierarchy

### Task A.1: `IngestResult` + `ConflictRecord` + `ConflictResolution` enum (TDD)

**Files:**
- Create: `modules/s3dgraphy/sync/ingest_result.py`
- Create: `tests/sync/test_ingest_result.py`

- [ ] **Step 1: Write failing tests**

Create `tests/sync/test_ingest_result.py`:

```python
"""Unit tests for IngestResult + ConflictRecord + ConflictResolution.
Pure dataclass invariants. No DB, no QGIS."""
import pytest


def test_conflict_resolution_enum_has_three_members():
    from modules.s3dgraphy.sync.ingest_result import ConflictResolution
    assert ConflictResolution.GRAPH_WINS.value == "graph_wins"
    assert ConflictResolution.DB_WINS.value == "db_wins"
    assert ConflictResolution.SKIPPED.value == "skipped"


def test_conflict_record_is_frozen():
    from modules.s3dgraphy.sync.ingest_result import ConflictRecord
    cr = ConflictRecord(
        node_uuid="abc-123",
        field="d_stratigrafica",
        db_value="Materiale",
        graph_value="Strato",
        resolution="graph_wins",
    )
    with pytest.raises(Exception):  # frozen → FrozenInstanceError
        cr.field = "other"
    assert cr.node_uuid == "abc-123"
    assert cr.resolution == "graph_wins"


def test_ingest_result_default_values():
    from modules.s3dgraphy.sync.ingest_result import IngestResult
    r = IngestResult(applied=0, inserted=0, updated=0, skipped=0,
                     epochs_created=0)
    assert r.conflicts == ()
    assert r.errors == ()
    assert r.dry_run is False


def test_ingest_result_is_frozen():
    from modules.s3dgraphy.sync.ingest_result import IngestResult
    r = IngestResult(applied=5, inserted=3, updated=2, skipped=0,
                     epochs_created=0)
    with pytest.raises(Exception):
        r.applied = 99


def test_ingest_result_with_conflicts():
    from modules.s3dgraphy.sync.ingest_result import (
        IngestResult, ConflictRecord)
    cr = ConflictRecord(node_uuid="u1", field="f", db_value=1,
                        graph_value=2, resolution="graph_wins")
    r = IngestResult(applied=1, inserted=0, updated=1, skipped=0,
                     epochs_created=0, conflicts=(cr,))
    assert len(r.conflicts) == 1
    assert r.conflicts[0].node_uuid == "u1"
```

- [ ] **Step 2: Run tests — expect collection errors**

```bash
pytest tests/sync/test_ingest_result.py -v
```

Expected: `ImportError: cannot import name 'ConflictResolution' from 'modules.s3dgraphy.sync.ingest_result'` (the module doesn't exist yet).

- [ ] **Step 3: Write minimal implementation**

Create `modules/s3dgraphy/sync/ingest_result.py`:

```python
"""Result and conflict record dataclasses for GraphIngestor.populate_list().

AI04 ships a fixed atomic-only ingestion model with last-writer-wins
conflict resolution. The ConflictResolution enum has three members so
AI06+ can extend without breaking the API.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ConflictResolution(str, Enum):
    """Outcome of a single field-level conflict during ingest.

    AI04 always uses GRAPH_WINS (the bridge prototype implements
    'last writer wins' policy from parent spec §6.4). DB_WINS and
    SKIPPED are reserved for AI06+ pluggable resolvers.
    """
    GRAPH_WINS = "graph_wins"
    DB_WINS = "db_wins"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class ConflictRecord:
    """A single field-level conflict detected during ingestion.

    A row is inserted into IngestResult.conflicts when the graph
    node has a value different from the DB row for one of the
    MAPPED_COLUMNS and the resolver decides how to merge.
    """
    node_uuid: str
    field: str
    db_value: Any
    graph_value: Any
    resolution: str   # ConflictResolution.value


@dataclass(frozen=True)
class IngestResult:
    """Aggregated outcome of GraphIngestor.populate_list().

    Counters and the conflict / error lists let callers (CLI, UI,
    test) summarise the ingestion without re-walking the graph.
    """
    applied: int            # rows inserted+updated successfully
    inserted: int           # rows newly created
    updated: int            # rows updated in place
    skipped: int            # rows unchanged (idempotent path)
    epochs_created: int     # auto-created periodizzazione rows
    conflicts: tuple[ConflictRecord, ...] = ()
    errors: tuple[str, ...] = ()
    dry_run: bool = False
```

- [ ] **Step 4: Run tests — expect green**

```bash
pytest tests/sync/test_ingest_result.py -v
```

Expected: `5 passed`.

- [ ] **Step 5: Run full suite**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `65 passed` (was 60 + 5 new).

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/ingest_result.py \
        tests/sync/test_ingest_result.py
git commit -m "$(cat <<'EOF'
feat(s3dgraphy/sync): IngestResult + ConflictRecord + ConflictResolution

Adds the result dataclasses for GraphIngestor.populate_list()
(spec §3.4). Both dataclasses are frozen so callers can't mutate
result state by accident; ConflictResolution is a string enum so
serialising to JSON or comparing in tests stays straightforward.

AI04 only exercises ConflictResolution.GRAPH_WINS; the DB_WINS
and SKIPPED members are reserved for AI06+ pluggable resolvers
(memory note: project_ai04_failure_mode_followup.md).
EOF
)"
```

### Task A.2: `ConflictResolver` stub (TDD)

**Files:**
- Create: `modules/s3dgraphy/sync/conflict_resolver.py`
- Create: `tests/sync/test_conflict_resolver.py`

- [ ] **Step 1: Write failing test**

Create `tests/sync/test_conflict_resolver.py`:

```python
"""Stub for the AI04 ConflictResolver. Always GRAPH_WINS."""
import pytest


def test_resolver_always_returns_graph_wins():
    from modules.s3dgraphy.sync.conflict_resolver import ConflictResolver
    from modules.s3dgraphy.sync.ingest_result import ConflictResolution
    resolver = ConflictResolver()
    # Even if every input differs:
    out = resolver.resolve(
        db_row={"d_stratigrafica": "old"},
        graph_value="new",
        field="d_stratigrafica",
    )
    assert out is ConflictResolution.GRAPH_WINS


def test_resolver_is_callable_with_any_field():
    from modules.s3dgraphy.sync.conflict_resolver import ConflictResolver
    from modules.s3dgraphy.sync.ingest_result import ConflictResolution
    resolver = ConflictResolver()
    assert resolver.resolve(db_row={}, graph_value=None,
                            field="anything") is ConflictResolution.GRAPH_WINS
```

- [ ] **Step 2: Run — expect ImportError**

```bash
pytest tests/sync/test_conflict_resolver.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Write minimal implementation**

Create `modules/s3dgraphy/sync/conflict_resolver.py`:

```python
"""Pluggable conflict resolution policy for GraphIngestor.

AI04 ships a stub that always returns ConflictResolution.GRAPH_WINS
(last-writer-wins, matching parent spec §6.4 default). The
interface is in place so AI06+ can subclass without changing
GraphIngestor's signature.
"""
from __future__ import annotations

from typing import Any

from .ingest_result import ConflictResolution


class ConflictResolver:
    """AI04 stub. Always resolves to GRAPH_WINS.

    Subclass and override `resolve()` in AI06+ for interactive,
    timestamp-based or callback-driven strategies.
    """
    def resolve(
        self,
        db_row: dict,
        graph_value: Any,
        field: str,
    ) -> ConflictResolution:
        return ConflictResolution.GRAPH_WINS
```

- [ ] **Step 4: Run — expect green**

```bash
pytest tests/sync/test_conflict_resolver.py -v
```

Expected: `2 passed`.

- [ ] **Step 5: Run full suite**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `67 passed`.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/conflict_resolver.py \
        tests/sync/test_conflict_resolver.py
git commit -m "$(cat <<'EOF'
feat(s3dgraphy/sync): ConflictResolver stub for AI04

Per spec §3.3, AI04 ships a ConflictResolver stub that always
returns ConflictResolution.GRAPH_WINS. The interface is in place
so AI06+ can subclass without breaking GraphIngestor's signature
(memory note: project_ai04_projector_refactor_plan.md and
project_ai04_failure_mode_followup.md describe the planned
extension).
EOF
)"
```

### Task A.3: Exception hierarchy in `graph_ingestor.py` (TDD)

This task creates the file and only the exception classes + module-level constants. The `GraphIngestor` class itself lands in Group C.

**Files:**
- Create: `modules/s3dgraphy/sync/graph_ingestor.py`  *(scaffolding only — no class yet)*
- Create: `tests/sync/test_graph_ingestor.py`  *(only exception tests in this task)*

- [ ] **Step 1: Write failing tests for the exception hierarchy**

Create `tests/sync/test_graph_ingestor.py`:

```python
"""Exception-hierarchy tests for graph_ingestor module.

Group C onwards adds tests for the GraphIngestor class itself.
"""
import pytest


def test_graph_sync_error_is_base_class():
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphSyncError, GraphIngestError)
    assert issubclass(GraphIngestError, GraphSyncError)


def test_specific_errors_inherit_graph_ingest_error():
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphIngestError,
        SchemaMismatchError,
        UnknownUnitaTipoError,
        SiteMismatchError,
        MissingEpochError,
    )
    for cls in (SchemaMismatchError, UnknownUnitaTipoError,
                SiteMismatchError, MissingEpochError):
        assert issubclass(cls, GraphIngestError), (
            f"{cls.__name__} must inherit GraphIngestError")


def test_mapped_columns_constant_present():
    from modules.s3dgraphy.sync.graph_ingestor import MAPPED_COLUMNS
    # The 12 columns spec §3.2 + risk row 5 enumerate.
    expected = {
        "us", "d_stratigrafica", "d_interpretativa", "attivita",
        "struttura", "sito", "area", "unita_tipo",
        "periodo_iniziale", "fase_iniziale", "rapporti", "node_uuid",
    }
    assert set(MAPPED_COLUMNS) == expected
    assert isinstance(MAPPED_COLUMNS, tuple)  # immutable


def test_missing_epoch_error_carries_epoch_list():
    from modules.s3dgraphy.sync.graph_ingestor import MissingEpochError
    err = MissingEpochError(missing=[(2, "3.1"), (3, "1")])
    assert err.missing == [(2, "3.1"), (3, "1")]
    assert "(2, '3.1')" in str(err) or "[(2," in str(err)
```

- [ ] **Step 2: Run — expect ImportError**

```bash
pytest tests/sync/test_graph_ingestor.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Write the scaffold**

Create `modules/s3dgraphy/sync/graph_ingestor.py`:

```python
"""Bridge from a s3dgraphy Graph back to the PyArchInit SQL tables.

This module hosts the public `GraphIngestor` class (Group C onwards)
and the full exception hierarchy used by both the projector and the
ingestor. All ingestion is atomic (single BEGIN/COMMIT/ROLLBACK).
"""
from __future__ import annotations

from typing import Iterable

# ---------------------------------------------------------------------------
# Mapped columns — the subset of us_table columns the s3dgraphy bridge
# round-trips. Composed of the columns covered by
# pyarchinit_us_mapping.json (5) + the columns added by
# `_enrich_pyarchinit_graph` in graphml_writer.py (7). Anything else
# in us_table (descrizione, foto, profondita, …) is preserved by
# UPDATE selettivo and never overwritten.
# ---------------------------------------------------------------------------
MAPPED_COLUMNS: tuple[str, ...] = (
    # From pyarchinit_us_mapping.json
    "us",
    "d_stratigrafica",
    "d_interpretativa",
    "attivita",
    "struttura",
    # Added by _enrich_pyarchinit_graph
    "sito",
    "area",
    "unita_tipo",
    "periodo_iniziale",
    "fase_iniziale",
    "rapporti",
    "node_uuid",
)


# ---------------------------------------------------------------------------
# Exception hierarchy (spec §5.1)
# ---------------------------------------------------------------------------
class GraphSyncError(Exception):
    """Base class for all GraphProjector / GraphIngestor errors."""


class GraphIngestError(GraphSyncError):
    """Write-side failure. Always means DB rolled back to pre-call state."""


class SchemaMismatchError(GraphIngestError):
    """us_table.node_uuid column missing (Phase 1 migration not applied).

    Hint: run scripts/migrations/2026_05_node_uuid_backfill.py --apply.
    """


class UnknownUnitaTipoError(GraphIngestError):
    """Graph node has unita_tipo not in the vocabulary.

    Hint: run scripts/migrations/2026_05_us_vocabulary_alignment.py --apply.
    """


class SiteMismatchError(GraphIngestError):
    """Graph contains a node whose attributes['sito'] != populate_list(sito=...)."""


class MissingEpochError(GraphIngestError):
    """One or more EpochNodes reference (periodo, fase) not present in
    periodizzazione_table while create_missing_epochs=False.

    The exception carries `missing: list[tuple[int, str]]` so callers
    can show all the missing keys at once instead of one per call.
    """
    def __init__(self, missing: Iterable[tuple]) -> None:
        self.missing = list(missing)
        super().__init__(
            f"Missing periodizzazione_table rows for: {self.missing}. "
            f"Run with create_missing_epochs=True to auto-create."
        )
```

- [ ] **Step 4: Run — expect green**

```bash
pytest tests/sync/test_graph_ingestor.py -v
```

Expected: `4 passed`.

- [ ] **Step 5: Run full suite**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `71 passed`.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/graph_ingestor.py \
        tests/sync/test_graph_ingestor.py
git commit -m "$(cat <<'EOF'
feat(s3dgraphy/sync): graph_ingestor exception hierarchy + MAPPED_COLUMNS

Per spec §5.1 — GraphSyncError as base, GraphIngestError as
write-side base, plus SchemaMismatchError, UnknownUnitaTipoError,
SiteMismatchError, MissingEpochError as concrete subclasses.

MissingEpochError carries the full list of missing (periodo, fase)
tuples so callers can show all missing keys at once.

Module-level MAPPED_COLUMNS tuple captures the 12 us_table columns
the bridge round-trips: 5 from pyarchinit_us_mapping.json + 7 added
by _enrich_pyarchinit_graph (sito, area, unita_tipo, periodo_iniziale,
fase_iniziale, rapporti, node_uuid). The remaining 40+ columns
(descrizione, foto, profondita, ...) are preserved by UPDATE
selettivo (D3-B from spec §2).

The GraphIngestor class itself lands in Group C.
EOF
)"
```

---

## Group B — `GraphProjector` wrapper (Strategy D)

### Task B.1: Add `sito_filter` kwarg to `_enrich_pyarchinit_graph` (no-default-change)

**Files:**
- Modify: `modules/s3dgraphy/sync/graphml_writer.py:206`

This is the only change to `graphml_writer.py`. Default `None` preserves AI03 behaviour exactly (verified by AC-2 baseline test).

- [ ] **Step 1: Read the current function signature**

```bash
sed -n '206,210p' modules/s3dgraphy/sync/graphml_writer.py
```

Expected: a line `def _enrich_pyarchinit_graph(graph, db_path: Path) -> None:`.

- [ ] **Step 2: Find the SQL query inside the function (around line 257)**

```bash
grep -n "SELECT us, sito, area, unita_tipo" modules/s3dgraphy/sync/graphml_writer.py
```

Note the line — typically `~257` — and the surrounding `cursor.execute(...)` call.

- [ ] **Step 3: Edit the function — add the kwarg + conditional WHERE clause**

Use the Edit tool to make these two changes:

**Change 1 — signature:**

```python
# OLD
def _enrich_pyarchinit_graph(graph, db_path: Path) -> None:

# NEW
def _enrich_pyarchinit_graph(graph, db_path: Path,
                              sito_filter: Optional[str] = None) -> None:
```

**Change 2 — SQL query (the `cursor.execute("SELECT us, sito, area, …")` block).** The current code reads:

```python
            cursor.execute(
                "SELECT us, sito, area, unita_tipo, periodo_iniziale, "
                "fase_iniziale, rapporti, d_stratigrafica "
                "FROM us_table"
            )
            rows = cursor.fetchall()
```

Replace with:

```python
            if sito_filter is not None:
                cursor.execute(
                    "SELECT us, sito, area, unita_tipo, periodo_iniziale, "
                    "fase_iniziale, rapporti, d_stratigrafica "
                    "FROM us_table WHERE sito = ?",
                    (sito_filter,),
                )
            else:
                cursor.execute(
                    "SELECT us, sito, area, unita_tipo, periodo_iniziale, "
                    "fase_iniziale, rapporti, d_stratigrafica "
                    "FROM us_table"
                )
            rows = cursor.fetchall()
```

- [ ] **Step 4: Run AC-2 regression guard FIRST**

```bash
pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: `1 passed`. If RED → revert the edit and redo carefully (the kwarg default must preserve the AI03 path bit-for-bit).

- [ ] **Step 5: Run full suite**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `71 passed` (zero new tests, zero regressions).

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/graphml_writer.py
git commit -m "$(cat <<'EOF'
feat(graphml_writer): add sito_filter kwarg to _enrich_pyarchinit_graph

Adds a single kwarg sito_filter: Optional[str] = None to the
existing _enrich_pyarchinit_graph() function. When non-None, the
us_table SELECT gains a `WHERE sito = ?` clause. Default None
preserves AI03 behaviour exactly (verified by the
test_ai03_export_byte_identical regression guard).

Strategy D from the AI04 spec §2 D2: GraphProjector (Group B.2)
wraps this function and passes the parameter through. The body of
the function is otherwise untouched — promotion of the logic to a
proper class inside GraphProjector is deferred to AI05 per the
memory note project_ai04_projector_refactor_plan.md.

Tests: 71/71 pass. AC-2 regression guard green.
EOF
)"
```

### Task B.2: Write `GraphProjector` class

**Files:**
- Create: `modules/s3dgraphy/sync/graph_projector.py`

- [ ] **Step 1: Create the file with the wrapper class**

Create `modules/s3dgraphy/sync/graph_projector.py`:

```python
"""Project PyArchInit DB rows into a stratigraphic-layer s3dgraphy Graph.

AI04 implementation is a thin wrapper (Strategy D, see memory note
project_ai04_projector_refactor_plan.md) around the existing
_enrich_pyarchinit_graph() function in graphml_writer.py. The
promotion to a self-contained class lives in AI05.

Exposed publicly so callers (UI Import tab, CLI helper, future
SyncEngine in Phase 3) have a stable API surface even while the
underlying implementation evolves.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from .graph_ingestor import GraphSyncError

if TYPE_CHECKING:
    import s3dgraphy


class ProjectionError(GraphSyncError):
    """Read-side failure during GraphProjector.populate_graph()."""


class GraphProjector:
    """Stratigraphic-layer projection from PyArchInit DB to s3dgraphy Graph.

    Usage:
        projector = GraphProjector()
        graph = projector.populate_graph(db_path, sito="Scavo archeologico")

    The graph contains StratigraphicUnit / USM / USVs / USVn / USD /
    SF / VSF / CON / DOC / Extractor / Combinar / property nodes plus
    EpochNodes for the (periodo, fase) tuples present in the filtered
    rows. Edges follow the rapporti column conventions decoded by
    `_RAPPORTI_TO_EDGE_TYPE` and `_RAPPORTI_SHORTHAND` in
    graphml_writer.py.
    """

    def __init__(self, vocab_provider=None) -> None:
        # vocab_provider parameter is here for API forward-compat
        # with AI06+ (where vocabulary aliases drive normalisation).
        # AI04 does not consume it.
        self._vocab_provider = vocab_provider

    def populate_graph(self, db_path: Path, sito: str) -> "s3dgraphy.Graph":
        """Build and return a s3dgraphy.Graph populated with the
        stratigraphic rows of `sito` from the SQLite at `db_path`.

        Args:
            db_path: filesystem path to the pyarchinit SQLite DB.
            sito: site identifier (`us_table.sito` value). Mandatory
                — multi-graph projections are out of scope for AI04.

        Returns:
            A populated `s3dgraphy.Graph`. Empty graph (zero nodes) is
            valid: it just means the site has no rows.

        Raises:
            ProjectionError: on any failure reaching the DB or
                instantiating the in-memory graph.
        """
        if not sito:
            raise ProjectionError(
                "sito parameter is mandatory for GraphProjector.populate_graph(); "
                "AI04 only supports single-site graphs.")
        db_path = Path(db_path)
        if not db_path.exists():
            raise ProjectionError(f"DB file not found: {db_path}")

        # Verify Phase 1 migration applied: us_table.node_uuid column.
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(us_table)")
            cols = {row[1] for row in cur.fetchall()}
            conn.close()
        except sqlite3.Error as e:
            raise ProjectionError(f"Cannot read us_table schema: {e}") from e
        if "node_uuid" not in cols:
            raise ProjectionError(
                "us_table.node_uuid column missing — run "
                "scripts/migrations/2026_05_node_uuid_backfill.py --apply")

        # Delegate to the existing AI03 enrichment routine.
        try:
            from s3dgraphy import Graph
            from .graphml_writer import _enrich_pyarchinit_graph
        except ImportError as e:
            raise ProjectionError(f"s3dgraphy import failed: {e}") from e

        graph = Graph(graph_id=sito)
        try:
            _enrich_pyarchinit_graph(graph, db_path, sito_filter=sito)
        except Exception as e:
            raise ProjectionError(
                f"Enrichment failed for sito={sito!r}: {e}") from e

        # Filter post-enrichment: keep only nodes whose attributes['sito']
        # match (defence in depth — _enrich already filters us_table rows
        # but EpochNodes are global and may belong to other sites).
        # We do NOT prune EpochNodes that are referenced via
        # has_first_epoch from any kept node.
        kept_node_ids = {
            n.node_id for n in graph.nodes
            if not hasattr(n, "attributes")
            or n.attributes is None
            or n.attributes.get("sito") in (None, sito)
        }
        # EpochNodes are global — keep them all if any strat node references them.
        # The downstream SiteMismatchError check in GraphIngestor catches mismatches.
        graph.nodes = [n for n in graph.nodes if n.node_id in kept_node_ids
                       or _is_epoch_node(n)]

        return graph


def _is_epoch_node(node) -> bool:
    """Return True if node is an EpochNode. Defensive — avoids importing
    EpochNode at module top because it forces s3dgraphy load too early."""
    return type(node).__name__ == "EpochNode"
```

- [ ] **Step 2: Run AC-2 regression guard**

```bash
pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: `1 passed`.

- [ ] **Step 3: Run full suite (no new tests yet)**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `71 passed` (zero change).

- [ ] **Step 4: Commit**

```bash
git add modules/s3dgraphy/sync/graph_projector.py
git commit -m "$(cat <<'EOF'
feat(s3dgraphy/sync): GraphProjector — public API for DB → Graph

Per spec §3.1, ships GraphProjector with the public method
populate_graph(db_path, sito) -> s3dgraphy.Graph.

Strategy D from spec §2 D2: this is a thin wrapper around the
existing _enrich_pyarchinit_graph() function in graphml_writer.py.
The wrapper:
  - Validates the sito parameter (mandatory).
  - Verifies the Phase 1 node_uuid migration is applied
    (raises ProjectionError otherwise, with hint to run the
    migration script).
  - Constructs an empty s3dgraphy.Graph with graph_id=sito.
  - Delegates enrichment to the existing function (passing
    sito_filter=sito so the SQL WHERE clause kicks in).
  - Filters EpochNodes/StratigraphicNodes post-process for
    defence in depth.

ProjectionError class added (mirrors GraphIngestError; both
inherit GraphSyncError per spec §5.1).

Tests for D2 (wrap pattern), D6 (mandatory sito), AC-1
(non-empty filtered graph) land in Group B.3.
EOF
)"
```

### Task B.3: Tests for `GraphProjector`

**Files:**
- Create: `tests/sync/test_graph_projector.py`

- [ ] **Step 1: Write failing tests**

Create `tests/sync/test_graph_projector.py`:

```python
"""Tests for GraphProjector. Pins:
- D2 — wrap pattern (calls _enrich_pyarchinit_graph)
- D6 — sito parameter mandatory
- AC-1 — non-empty graph, filtered by sito
"""
from __future__ import annotations
import sys
from pathlib import Path

import pytest
import pandas  # noqa: F401
from lxml import etree as _etree  # noqa: F401
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")


@pytest.fixture
def mini_volterra(tmp_path):
    import shutil
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    return dst


def test_populate_graph_requires_sito(mini_volterra):
    """D6 — empty sito is rejected."""
    from modules.s3dgraphy.sync.graph_projector import (
        GraphProjector, ProjectionError)
    p = GraphProjector()
    with pytest.raises(ProjectionError, match="sito"):
        p.populate_graph(mini_volterra, sito="")


def test_populate_graph_missing_db_raises(tmp_path):
    from modules.s3dgraphy.sync.graph_projector import (
        GraphProjector, ProjectionError)
    p = GraphProjector()
    with pytest.raises(ProjectionError, match="not found"):
        p.populate_graph(tmp_path / "nope.sqlite", sito="X")


def test_populate_graph_missing_node_uuid_column_raises(tmp_path):
    """SchemaMismatchError-equivalent: node_uuid column required."""
    import sqlite3
    from modules.s3dgraphy.sync.graph_projector import (
        GraphProjector, ProjectionError)
    db = tmp_path / "x.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, "
                 "sito TEXT, us TEXT)")  # no node_uuid
    conn.commit()
    conn.close()
    p = GraphProjector()
    with pytest.raises(ProjectionError, match="node_uuid"):
        p.populate_graph(db, sito="X")


def test_projector_returns_filtered_graph(mini_volterra):
    """AC-1 — non-empty graph, every strat node matches sito."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    p = GraphProjector()
    # Find the sito present in the fixture
    import sqlite3
    conn = sqlite3.connect(mini_volterra)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    graph = p.populate_graph(mini_volterra, sito=sito)
    assert len(graph.nodes) > 0
    # Every node with sito attribute must match — EpochNodes have no sito.
    for n in graph.nodes:
        attrs = getattr(n, "attributes", None) or {}
        if "sito" in attrs:
            assert attrs["sito"] == sito


def test_projector_delegates_to_enrich_function(mini_volterra, monkeypatch):
    """D2 — verify GraphProjector calls _enrich_pyarchinit_graph
    (Strategy D wrap pattern)."""
    from modules.s3dgraphy.sync import graph_projector as gp_mod
    calls = []
    real_fn = gp_mod._enrich_pyarchinit_graph if hasattr(
        gp_mod, "_enrich_pyarchinit_graph") else None
    # Monkey-patch the local reference in graphml_writer (the module
    # graph_projector imports the function from); we need to patch
    # the binding inside GraphProjector.populate_graph at call-time.
    from modules.s3dgraphy.sync import graphml_writer
    original = graphml_writer._enrich_pyarchinit_graph

    def spy(graph, db_path, sito_filter=None):
        calls.append((db_path, sito_filter))
        return original(graph, db_path, sito_filter=sito_filter)
    monkeypatch.setattr(graphml_writer, "_enrich_pyarchinit_graph", spy)

    import sqlite3
    conn = sqlite3.connect(mini_volterra)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()

    p = gp_mod.GraphProjector()
    p.populate_graph(mini_volterra, sito=sito)
    assert len(calls) == 1, "GraphProjector must call _enrich_pyarchinit_graph"
    assert calls[0][1] == sito, "sito_filter must be propagated"
```

- [ ] **Step 2: Run — expect 5 passes**

```bash
pytest tests/sync/test_graph_projector.py -v
```

Expected: `5 passed`. (No "expect to fail" round here — the module already exists from Task B.2; the tests verify behaviour.)

- [ ] **Step 3: Run full suite**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `76 passed` (was 71 + 5 new).

- [ ] **Step 4: Commit**

```bash
git add tests/sync/test_graph_projector.py
git commit -m "$(cat <<'EOF'
test(graph_projector): pin D2 wrap pattern, D6 sito mandatory, AC-1

Five tests covering GraphProjector behaviour:

- test_populate_graph_requires_sito: empty sito → ProjectionError (D6).
- test_populate_graph_missing_db_raises: nonexistent DB path raises.
- test_populate_graph_missing_node_uuid_column_raises: schema check
  (ProjectionError mentioning node_uuid + migration hint).
- test_projector_returns_filtered_graph: AC-1 — non-empty graph,
  every node with a 'sito' attribute matches the parameter.
- test_projector_delegates_to_enrich_function: D2 — verifies the
  Strategy D wrap actually delegates to _enrich_pyarchinit_graph
  (so AI05's promotion to a real class can be done with confidence
  that the contract is observed by tests).

Tests: 76/76 pass.
EOF
)"
```

---

## Group C — `GraphIngestor.populate_list` dry-run mode (TDD)

This Group adds the `GraphIngestor` class itself, but in **dry-run only** mode: validation, per-node lookup + diff, EpochNode lookup, ROLLBACK at the end. **No writes.** Group D adds the write path.

### Task C.1: Skeleton `GraphIngestor` class + validation step

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_ingestor.py` (extend the file from Task A.3)
- Modify: `tests/sync/test_graph_ingestor.py` (add tests)

- [ ] **Step 1: Write failing tests**

Append to `tests/sync/test_graph_ingestor.py`:

```python
# Re-use the path bootstrap from test_graph_projector.py
import sys
from pathlib import Path
import pandas  # noqa: F401
from lxml import etree as _etree  # noqa: F401
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")


@pytest.fixture
def mini_volterra(tmp_path):
    import shutil
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    return dst


def _read_sito(db_path):
    import sqlite3
    conn = sqlite3.connect(db_path)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    return sito


def test_ingestor_construction():
    """Ingestor accepts an optional ConflictResolver."""
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    from modules.s3dgraphy.sync.conflict_resolver import ConflictResolver
    g = GraphIngestor()
    assert g._resolver is not None
    g2 = GraphIngestor(conflict_resolver=ConflictResolver())
    assert g2._resolver is not None


def test_populate_list_requires_sito_match(mini_volterra):
    """D6 — graph nodes whose sito differs from the parameter raise."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphIngestor, SiteMismatchError)
    sito = _read_sito(mini_volterra)
    graph = GraphProjector().populate_graph(mini_volterra, sito=sito)
    g = GraphIngestor()
    with pytest.raises(SiteMismatchError):
        g.populate_list(graph, mini_volterra, sito="WRONG_SITE")


def test_populate_list_schema_check_raises(tmp_path):
    """node_uuid column missing → SchemaMismatchError."""
    import sqlite3
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphIngestor, SchemaMismatchError)
    # Construct an empty graph for the test
    from s3dgraphy import Graph
    db = tmp_path / "x.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id_us INTEGER, sito TEXT, us TEXT)")
    conn.commit()
    conn.close()
    g = GraphIngestor()
    with pytest.raises(SchemaMismatchError):
        g.populate_list(Graph(graph_id="X"), db, sito="X")
```

- [ ] **Step 2: Run — expect AttributeError / ImportError on GraphIngestor**

```bash
pytest tests/sync/test_graph_ingestor.py::test_ingestor_construction -v
```

Expected: `ImportError: cannot import name 'GraphIngestor'`.

- [ ] **Step 3: Add the `GraphIngestor` class with validation only**

Append to `modules/s3dgraphy/sync/graph_ingestor.py`:

```python
# ---------------------------------------------------------------------------
# GraphIngestor (Groups C–D)
# ---------------------------------------------------------------------------
import logging
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING

from .conflict_resolver import ConflictResolver
from .ingest_result import (
    ConflictRecord, ConflictResolution, IngestResult)

if TYPE_CHECKING:
    import s3dgraphy

log = logging.getLogger("modules.s3dgraphy.sync.graph_ingestor")


class GraphIngestor:
    """Persist a s3dgraphy Graph back to the PyArchInit SQL tables.

    Single atomic transaction (BEGIN/COMMIT/ROLLBACK). Idempotent on
    re-runs against the same input. AI04 always uses
    ConflictResolution.GRAPH_WINS for value diffs.
    """

    def __init__(self, conflict_resolver: ConflictResolver | None = None) -> None:
        self._resolver = conflict_resolver or ConflictResolver()

    def populate_list(
        self,
        graph: "s3dgraphy.Graph",
        db_path: Path,
        sito: str,
        *,
        dry_run: bool = False,
        create_missing_epochs: bool = False,
    ) -> IngestResult:
        """See spec §3.2 docstring for full contract."""
        db_path = Path(db_path)
        # 1. Schema check
        self._verify_schema(db_path)
        # 2. Site-mismatch check
        self._verify_sito(graph, sito)
        # 3. Run the actual ingestion (Group C: dry-run only)
        return self._run(graph, db_path, sito,
                         dry_run=dry_run,
                         create_missing_epochs=create_missing_epochs)

    # ------------------------------------------------------------------ helpers
    def _verify_schema(self, db_path: Path) -> None:
        if not db_path.exists():
            raise GraphIngestError(f"DB file not found: {db_path}")
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(us_table)")
            cols = {row[1] for row in cur.fetchall()}
            conn.close()
        except sqlite3.Error as e:
            raise GraphIngestError(f"Cannot read us_table schema: {e}") from e
        if "node_uuid" not in cols:
            raise SchemaMismatchError(
                "us_table.node_uuid column missing — run "
                "scripts/migrations/2026_05_node_uuid_backfill.py --apply")

    def _verify_sito(self, graph, sito: str) -> None:
        if not sito:
            raise SiteMismatchError(
                "sito parameter is mandatory; AI04 only supports single-site graphs.")
        for n in graph.nodes:
            attrs = getattr(n, "attributes", None) or {}
            node_sito = attrs.get("sito")
            if node_sito is not None and node_sito != sito:
                raise SiteMismatchError(
                    f"Graph node {getattr(n, 'node_id', '?')!r} has "
                    f"sito={node_sito!r}, expected {sito!r}")

    def _run(self, graph, db_path, sito, *, dry_run, create_missing_epochs):
        """Group C minimal version: returns an empty IngestResult.
        Group C.2-C.4 fill in the actual logic."""
        return IngestResult(applied=0, inserted=0, updated=0, skipped=0,
                            epochs_created=0, dry_run=dry_run)
```

- [ ] **Step 4: Run — expect new tests pass**

```bash
pytest tests/sync/test_graph_ingestor.py -v
```

Expected: `7 passed` (4 from Task A.3 + 3 new).

- [ ] **Step 5: Run full suite**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `79 passed`.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/graph_ingestor.py \
        tests/sync/test_graph_ingestor.py
git commit -m "$(cat <<'EOF'
feat(graph_ingestor): GraphIngestor skeleton + validation step

Per spec §3.2, ships the GraphIngestor class with the public
populate_list() entry point. This task only implements the
validation step:
  - Schema check: us_table.node_uuid column present, else
    SchemaMismatchError.
  - Site-mismatch check: graph nodes with attributes['sito'] !=
    sito parameter raise SiteMismatchError (D6).

The actual per-node lookup + conflict detection + transaction
arrives in C.2 / C.3 / C.4. _run() currently returns an empty
IngestResult so the public API is callable end-to-end and tests
can pin the validation behaviour in isolation.

Tests: 79/79 pass.
EOF
)"
```

### Task C.2: Per-node lookup + conflict detection (no writes)

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_ingestor.py:_run`
- Modify: `tests/sync/test_graph_ingestor.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/sync/test_graph_ingestor.py`:

```python
def test_populate_list_dry_run_no_writes(mini_volterra):
    """D3 — dry_run=True must not change the DB (sha256 invariant)."""
    import hashlib
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    sito = _read_sito(mini_volterra)
    graph = GraphProjector().populate_graph(mini_volterra, sito=sito)
    sha_before = hashlib.sha256(mini_volterra.read_bytes()).hexdigest()
    g = GraphIngestor()
    result = g.populate_list(graph, mini_volterra, sito=sito, dry_run=True)
    sha_after = hashlib.sha256(mini_volterra.read_bytes()).hexdigest()
    assert sha_before == sha_after, "dry_run modified the DB"
    assert result.dry_run is True
    assert result.applied == 0


def test_populate_list_dry_run_counts_skipped_when_unchanged(mini_volterra):
    """Round-trip the projector → ingestor: every node should be
    'skipped' (no diff vs the source)."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    sito = _read_sito(mini_volterra)
    graph = GraphProjector().populate_graph(mini_volterra, sito=sito)
    result = GraphIngestor().populate_list(
        graph, mini_volterra, sito=sito, dry_run=True)
    # Every projected node is already in DB, no value differences →
    # all skipped.
    n_strat = sum(1 for n in graph.nodes
                  if (getattr(n, "attributes", None) or {}).get("us") is not None)
    assert result.skipped == n_strat
    assert result.inserted == 0
    assert result.updated == 0
    assert len(result.conflicts) == 0
```

- [ ] **Step 2: Run — expect failure (skipped count == 0)**

```bash
pytest tests/sync/test_graph_ingestor.py::test_populate_list_dry_run_counts_skipped_when_unchanged -v
```

Expected: FAIL — `assert 0 == n_strat`.

- [ ] **Step 3: Implement the per-node loop in `_run`**

Replace the body of `GraphIngestor._run()` with:

```python
    def _run(self, graph, db_path, sito, *, dry_run, create_missing_epochs):
        inserted = updated = skipped = 0
        epochs_created = 0
        conflicts: list[ConflictRecord] = []
        errors: list[str] = []

        # Open the transaction (we always use BEGIN even in dry-run so
        # any side effects from other code paths get isolated and
        # ROLLBACK'd).
        conn = sqlite3.connect(str(db_path))
        conn.execute("BEGIN")
        try:
            cur = conn.cursor()
            for node in graph.nodes:
                # Skip non-stratigraphic / non-attribute nodes (e.g. EpochNode).
                attrs = getattr(node, "attributes", None) or {}
                if not attrs.get("us") and not getattr(node, "node_id", None):
                    continue
                if _is_epoch_node_local(node):
                    continue
                # Look up by node_uuid
                node_uuid = getattr(node, "node_id", None) or attrs.get("node_uuid")
                if not node_uuid:
                    continue
                cur.execute(
                    "SELECT * FROM us_table WHERE node_uuid = ?",
                    (node_uuid,),
                )
                row = cur.fetchone()
                if row is None:
                    inserted += 1
                    continue
                # Build {col: db_val} dict from row + cursor.description
                col_names = [d[0] for d in cur.description]
                db_row = dict(zip(col_names, row))
                row_changed = False
                for col in MAPPED_COLUMNS:
                    if col not in attrs:
                        continue
                    db_val = db_row.get(col)
                    graph_val = attrs.get(col)
                    if _values_equal(col, db_val, graph_val):
                        continue
                    row_changed = True
                    self._resolver.resolve(
                        db_row=db_row, graph_value=graph_val, field=col)
                    conflicts.append(ConflictRecord(
                        node_uuid=node_uuid, field=col,
                        db_value=db_val, graph_value=graph_val,
                        resolution=ConflictResolution.GRAPH_WINS.value,
                    ))
                if row_changed:
                    updated += 1
                else:
                    skipped += 1

            applied = inserted + updated  # Group D will write; for now counts only
            # Always ROLLBACK in dry-run; Group D handles COMMIT path.
            if dry_run:
                conn.rollback()
            else:
                # Group D will replace this with the write loop + COMMIT
                conn.rollback()
                applied = 0  # nothing written yet
        except GraphSyncError:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise GraphIngestError(f"Ingest failed: {e}") from e
        finally:
            conn.close()

        return IngestResult(
            applied=applied if dry_run else 0,
            inserted=inserted, updated=updated, skipped=skipped,
            epochs_created=epochs_created,
            conflicts=tuple(conflicts), errors=tuple(errors),
            dry_run=dry_run,
        )


def _values_equal(col: str, a, b) -> bool:
    """Loose equality matching the conventions in graphml_writer
    enrichment. JSON-serialised columns (rapporti) get parse-then-compare."""
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if col == "rapporti":
        try:
            import ast
            return ast.literal_eval(str(a)) == ast.literal_eval(str(b))
        except (ValueError, SyntaxError):
            return str(a) == str(b)
    return str(a) == str(b)


def _is_epoch_node_local(node) -> bool:
    return type(node).__name__ == "EpochNode"
```

- [ ] **Step 4: Run — expect green**

```bash
pytest tests/sync/test_graph_ingestor.py -v
```

Expected: `9 passed`.

- [ ] **Step 5: Run full suite**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `81 passed`.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/graph_ingestor.py \
        tests/sync/test_graph_ingestor.py
git commit -m "$(cat <<'EOF'
feat(graph_ingestor): per-node lookup + conflict detection (dry-run)

Implements the per-node loop of populate_list() (spec §4.2):
  - SELECT us_table WHERE node_uuid = ? for each graph node
  - Compare every MAPPED_COLUMNS entry between graph attribute
    and DB row.
  - For every value difference, record a ConflictRecord and ask
    the resolver (stub returns GRAPH_WINS).
  - Counters: inserted (no DB row found), updated (row found,
    >=1 mapped column differs), skipped (row found, all mapped
    columns match).

dry_run=True always ROLLBACKs at the end (D3 — verified by sha256
invariant test). The write path is implemented in Group D.

Special handling for the rapporti JSON-serialised column: parse
both sides via ast.literal_eval before comparing, to avoid false
positives from whitespace differences.

EpochNodes are skipped in this loop — Group C.3 handles them.

Tests: 81/81 pass.
EOF
)"
```

### Task C.3: EpochNode lookup + `MissingEpochError`

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_ingestor.py:_run`
- Modify: `tests/sync/test_graph_ingestor.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/sync/test_graph_ingestor.py`:

```python
def _make_graph_with_extra_epoch(mini_volterra, periodo, fase):
    """Project mini_volterra and inject an extra EpochNode."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from s3dgraphy.nodes.epoch_node import EpochNode
    sito = _read_sito(mini_volterra)
    graph = GraphProjector().populate_graph(mini_volterra, sito=sito)
    # Add a synthetic epoch missing from periodizzazione_table
    epoch = EpochNode(
        node_id=f"epoch_{periodo}_{fase}_synthetic",
        name=f"Synthetic Period {periodo} Phase {fase}",
        start_time=0.0, end_time=0.0)
    epoch.attributes = {"periodo": periodo, "fase": fase}
    graph.add_node(epoch)
    return graph, sito


def test_missing_epoch_strict_raises(mini_volterra):
    """D5-A — strict (default) raises MissingEpochError."""
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphIngestor, MissingEpochError)
    graph, sito = _make_graph_with_extra_epoch(
        mini_volterra, periodo=99, fase="9.9")
    g = GraphIngestor()
    with pytest.raises(MissingEpochError) as excinfo:
        g.populate_list(graph, mini_volterra, sito=sito, dry_run=True)
    assert (99, "9.9") in excinfo.value.missing


def test_missing_epoch_create_inserts_period(mini_volterra):
    """D5-B — opt-in counts the would-be inserts; dry-run no writes."""
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    graph, sito = _make_graph_with_extra_epoch(
        mini_volterra, periodo=99, fase="9.9")
    g = GraphIngestor()
    result = g.populate_list(graph, mini_volterra, sito=sito,
                              dry_run=True, create_missing_epochs=True)
    assert result.epochs_created == 1
```

- [ ] **Step 2: Run — expect failures**

```bash
pytest tests/sync/test_graph_ingestor.py::test_missing_epoch_strict_raises -v
```

Expected: FAIL — `MissingEpochError` not raised.

- [ ] **Step 3: Implement the EpochNode loop**

Inside `_run()`, just before the `if dry_run:` branch, insert:

```python
            # ---- EpochNode loop ----
            # Read all (periodo, fase) pairs already in periodizzazione_table.
            cur.execute(
                "SELECT CAST(periodo AS TEXT), CAST(fase AS TEXT) "
                "FROM periodizzazione_table")
            existing_epochs = {(r[0], r[1]) for r in cur.fetchall()}
            missing_epochs: list[tuple] = []
            for node in graph.nodes:
                if not _is_epoch_node_local(node):
                    continue
                attrs = getattr(node, "attributes", None) or {}
                periodo = attrs.get("periodo")
                fase = attrs.get("fase")
                if periodo is None:
                    continue
                key = (str(periodo), str(fase) if fase is not None else "")
                if key in existing_epochs:
                    continue
                if create_missing_epochs:
                    epochs_created += 1
                    # Group D writes the actual INSERT here. For dry-run, just count.
                else:
                    # Coerce periodo back to int for the error payload
                    try:
                        p_int = int(periodo)
                    except (TypeError, ValueError):
                        p_int = periodo
                    missing_epochs.append((p_int, str(fase)))
            if missing_epochs:
                conn.rollback()
                conn.close()
                raise MissingEpochError(missing=missing_epochs)
```

- [ ] **Step 4: Run — expect green**

```bash
pytest tests/sync/test_graph_ingestor.py -v
```

Expected: `11 passed`.

- [ ] **Step 5: Run full suite**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `83 passed`.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/graph_ingestor.py \
        tests/sync/test_graph_ingestor.py
git commit -m "$(cat <<'EOF'
feat(graph_ingestor): epoch lookup + MissingEpochError (D5)

Adds the EpochNode validation step to populate_list (spec §4.2
step 4):
  - Reads all (periodo, fase) pairs from periodizzazione_table.
  - For each graph EpochNode: if (periodo, fase) is already
    present, no-op.
  - If missing AND create_missing_epochs=False (default): collect
    into a single MissingEpochError raised AFTER the per-node
    loop (so the user sees ALL missing keys at once).
  - If missing AND create_missing_epochs=True: increment
    epochs_created counter (Group D writes the actual INSERT).

Pins D5-A (strict default) and D5-B (opt-in counter).

Tests: 83/83 pass.
EOF
)"
```

### Task C.4: D8 atomicity test (rollback on mid-loop failure)

**Files:**
- Modify: `tests/sync/test_graph_ingestor.py`

This task adds the D8 atomicity test using a test-double for the resolver that raises mid-loop. The actual atomicity is already enforced by the `try/except → conn.rollback()` block in `_run`.

- [ ] **Step 1: Write failing test**

Append to `tests/sync/test_graph_ingestor.py`:

```python
def test_populate_list_atomic_on_failure(mini_volterra):
    """D8 — any mid-loop exception ROLLBACKs (DB sha256 unchanged).

    Inject a resolver that raises on the first conflict.
    """
    import hashlib
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphIngestor, GraphIngestError)
    from modules.s3dgraphy.sync.conflict_resolver import ConflictResolver

    class BombResolver(ConflictResolver):
        def resolve(self, db_row, graph_value, field):
            raise RuntimeError("simulated failure")

    sito = _read_sito(mini_volterra)
    graph = GraphProjector().populate_graph(mini_volterra, sito=sito)
    # Force a conflict: mutate one node's d_stratigrafica
    for n in graph.nodes:
        attrs = getattr(n, "attributes", None) or {}
        if attrs.get("us"):
            attrs["d_stratigrafica"] = "MUTATED FOR TEST"
            break

    sha_before = hashlib.sha256(mini_volterra.read_bytes()).hexdigest()
    g = GraphIngestor(conflict_resolver=BombResolver())
    with pytest.raises(GraphIngestError):
        g.populate_list(graph, mini_volterra, sito=sito, dry_run=False)
    sha_after = hashlib.sha256(mini_volterra.read_bytes()).hexdigest()
    assert sha_before == sha_after, "atomic rollback failed: DB changed"
```

- [ ] **Step 2: Run — expect green** (the atomic guarantee is already in place from Task C.1)

```bash
pytest tests/sync/test_graph_ingestor.py::test_populate_list_atomic_on_failure -v
```

Expected: `1 passed`.

- [ ] **Step 3: Run full suite**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `84 passed`.

- [ ] **Step 4: Commit**

```bash
git add tests/sync/test_graph_ingestor.py
git commit -m "$(cat <<'EOF'
test(graph_ingestor): D8 atomicity guarantee — sha256 invariant

Pins decision D8 (atomic-only ingestion) with a test that:
  - Mutates one graph node so a conflict is detected.
  - Injects a BombResolver that raises on the first conflict.
  - Captures sha256(DB) before populate_list().
  - Asserts the wrapping GraphIngestError raises AND sha256(DB)
    is unchanged after the call.

This is the 'atomic' contract from spec D8 — verified live, not
just by code inspection. The configurable failure_mode parameter
is deferred to AI06+ per the project_ai04_failure_mode_followup
memory note.

Tests: 84/84 pass.
EOF
)"
```

---

## Group D — `GraphIngestor.populate_list` write mode

This Group adds the actual INSERT/UPDATE/COMMIT path. The dry-run code stays exactly as it is.

### Task D.1: INSERT new rows (mapped columns + node_uuid + sito)

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_ingestor.py:_run`
- Modify: `tests/sync/test_graph_ingestor.py`

- [ ] **Step 1: Write failing test**

Append to `tests/sync/test_graph_ingestor.py`:

```python
def test_populate_list_inserts_new_rows(mini_volterra):
    """A graph node not present in DB → INSERT in write mode."""
    import sqlite3, uuid
    from s3dgraphy import Graph
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor

    sito = _read_sito(mini_volterra)
    new_uuid = str(uuid.uuid4())

    # Build a graph with one synthetic node not in DB
    class _Node:
        def __init__(self, **kw):
            self.node_id = kw["node_id"]
            self.name = kw["name"]
            self.attributes = kw["attributes"]
    graph = Graph(graph_id=sito)
    n = _Node(node_id=new_uuid, name="999",
              attributes={"us": "999", "sito": sito,
                          "unita_tipo": "US", "node_uuid": new_uuid})
    graph.add_node(n)

    GraphIngestor().populate_list(
        graph, mini_volterra, sito=sito, dry_run=False)

    # Verify the INSERT happened
    conn = sqlite3.connect(mini_volterra)
    row = conn.execute(
        "SELECT us, sito, unita_tipo FROM us_table WHERE node_uuid = ?",
        (new_uuid,)).fetchone()
    conn.close()
    assert row is not None
    assert row[0] == "999"
    assert row[1] == sito
    assert row[2] == "US"
```

- [ ] **Step 2: Run — expect FAIL**

```bash
pytest tests/sync/test_graph_ingestor.py::test_populate_list_inserts_new_rows -v
```

Expected: FAIL — `assert row is not None`.

- [ ] **Step 3: Implement the write path**

In `GraphIngestor._run()`, replace the placeholder write block:

```python
            # Group D will replace this with the write loop + COMMIT
            conn.rollback()
            applied = 0  # nothing written yet
```

with:

```python
            # ---- Write mode: INSERT new rows + UPDATE existing ones ----
            # Build a list of (kind, payload) ops collected during the
            # per-node loop above. We re-walk graph.nodes here so we can
            # replay the same decisions made during the dry-run dispatch.
            applied = 0
            for node in graph.nodes:
                if _is_epoch_node_local(node):
                    continue
                attrs = getattr(node, "attributes", None) or {}
                node_uuid = getattr(node, "node_id", None) or attrs.get("node_uuid")
                if not node_uuid:
                    continue
                cur.execute(
                    "SELECT * FROM us_table WHERE node_uuid = ?",
                    (node_uuid,),
                )
                existing = cur.fetchone()
                col_payload = {col: attrs.get(col) for col in MAPPED_COLUMNS
                               if col in attrs}
                col_payload["node_uuid"] = node_uuid
                col_payload["sito"] = sito
                if existing is None:
                    # INSERT
                    cols = list(col_payload.keys())
                    placeholders = ",".join("?" for _ in cols)
                    col_list = ",".join(cols)
                    cur.execute(
                        f"INSERT INTO us_table ({col_list}) VALUES "
                        f"({placeholders})",
                        [col_payload[c] for c in cols],
                    )
                    applied += 1
                # UPDATE branch lands in Task D.2
            # Epoch INSERT (D5-B path)
            if create_missing_epochs:
                for node in graph.nodes:
                    if not _is_epoch_node_local(node):
                        continue
                    attrs = getattr(node, "attributes", None) or {}
                    periodo = attrs.get("periodo")
                    fase = attrs.get("fase")
                    if periodo is None:
                        continue
                    key = (str(periodo), str(fase) if fase is not None else "")
                    if key in existing_epochs:
                        continue
                    cur.execute(
                        "INSERT INTO periodizzazione_table "
                        "(periodo, fase, descrizione) VALUES (?, ?, ?)",
                        (periodo, fase, getattr(node, "name", "") or ""),
                    )
            conn.commit()
```

Also update the `if dry_run:` branch to NOT swallow the write block (the structure now is `if dry_run: rollback else: write+commit`).

The full updated `_run` end becomes:

```python
            if dry_run:
                conn.rollback()
                applied = 0
            else:
                # write block above already ran; commit now
                conn.commit()
        except GraphSyncError:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise GraphIngestError(f"Ingest failed: {e}") from e
        finally:
            conn.close()
```

Note: the per-node lookup loop already runs above (Task C.2). The write block now reuses the same SELECT to decide INSERT vs UPDATE, so there is one extra SELECT per node — acceptable for the AI04 prototype (Volterra-grade datasets are O(thousands) rows, not millions).

- [ ] **Step 4: Run — expect green**

```bash
pytest tests/sync/test_graph_ingestor.py::test_populate_list_inserts_new_rows -v
```

Expected: `1 passed`.

- [ ] **Step 5: Run full suite**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `85 passed`.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/graph_ingestor.py \
        tests/sync/test_graph_ingestor.py
git commit -m "$(cat <<'EOF'
feat(graph_ingestor): write-mode INSERT path + COMMIT

Adds the actual write block to populate_list when dry_run=False:
  - INSERT new us_table rows (node_uuid not in DB) with the
    MAPPED_COLUMNS subset present in the graph node attributes.
  - INSERT new periodizzazione_table rows when
    create_missing_epochs=True for each EpochNode whose
    (periodo, fase) is missing.
  - COMMIT on success.

UPDATE selettivo (existing rows with diffs) lands in D.2.

The transaction wrapping (try/except → rollback on any
exception) is unchanged from C.1, so D8 atomicity is preserved
for both INSERT and UPDATE paths.

Tests: 85/85 pass.
EOF
)"
```

### Task D.2: UPDATE selettivo (preserve unmapped columns)

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_ingestor.py:_run`
- Modify: `tests/sync/test_graph_ingestor.py`

- [ ] **Step 1: Write failing test**

Append to `tests/sync/test_graph_ingestor.py`:

```python
def test_update_preserves_unmapped_columns(mini_volterra):
    """D3 — UPDATE selettivo preserves columns not in MAPPED_COLUMNS.

    Set descrizione (NOT in MAPPED_COLUMNS) on a row, run a graph
    that mutates d_stratigrafica (mapped) on the same row, verify
    descrizione survived intact.
    """
    import sqlite3
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor

    sito = _read_sito(mini_volterra)

    # Set descrizione on the first row
    conn = sqlite3.connect(mini_volterra)
    # Detect descrizione column (may be named differently across schemas)
    cols = {r[1] for r in conn.execute(
        "PRAGMA table_info(us_table)").fetchall()}
    if "descrizione" not in cols:
        pytest.skip("us_table has no descrizione column on this schema")
    target_uuid = conn.execute(
        "SELECT node_uuid FROM us_table WHERE sito = ? LIMIT 1",
        (sito,)).fetchone()[0]
    conn.execute(
        "UPDATE us_table SET descrizione = ? WHERE node_uuid = ?",
        ("PRESERVED_BY_AI04", target_uuid))
    conn.commit()
    conn.close()

    # Project + mutate d_stratigrafica + ingest
    graph = GraphProjector().populate_graph(mini_volterra, sito=sito)
    for n in graph.nodes:
        if getattr(n, "node_id", None) == target_uuid:
            n.attributes["d_stratigrafica"] = "AI04_NEW_VALUE"
            break
    GraphIngestor().populate_list(graph, mini_volterra, sito=sito,
                                   dry_run=False)

    # Verify descrizione survived
    conn = sqlite3.connect(mini_volterra)
    descr, dstrat = conn.execute(
        "SELECT descrizione, d_stratigrafica FROM us_table "
        "WHERE node_uuid = ?", (target_uuid,)).fetchone()
    conn.close()
    assert descr == "PRESERVED_BY_AI04", \
        f"unmapped column overwritten (got {descr!r})"
    assert dstrat == "AI04_NEW_VALUE", "mapped column not updated"
```

- [ ] **Step 2: Run — expect FAIL** (UPDATE not implemented yet)

```bash
pytest tests/sync/test_graph_ingestor.py::test_update_preserves_unmapped_columns -v
```

Expected: FAIL — `dstrat != "AI04_NEW_VALUE"`.

- [ ] **Step 3: Add the UPDATE branch**

Inside `_run()`, in the write block, after the `if existing is None: INSERT` branch, add:

```python
                else:
                    # UPDATE selettivo: only the MAPPED_COLUMNS that
                    # actually differ. Any column not in attrs and any
                    # us_table column not in MAPPED_COLUMNS is left
                    # untouched (preserves descrizione, foto, etc.).
                    col_names = [d[0] for d in cur.description]
                    db_row = dict(zip(col_names, existing))
                    diff_cols = []
                    diff_vals = []
                    for col in MAPPED_COLUMNS:
                        if col not in attrs:
                            continue
                        if _values_equal(col, db_row.get(col),
                                          attrs.get(col)):
                            continue
                        diff_cols.append(col)
                        diff_vals.append(attrs.get(col))
                    if diff_cols:
                        set_clause = ", ".join(f"{c} = ?" for c in diff_cols)
                        cur.execute(
                            f"UPDATE us_table SET {set_clause} "
                            f"WHERE node_uuid = ?",
                            [*diff_vals, node_uuid],
                        )
                        applied += 1
```

- [ ] **Step 4: Run — expect green**

```bash
pytest tests/sync/test_graph_ingestor.py::test_update_preserves_unmapped_columns -v
```

Expected: `1 passed`.

- [ ] **Step 5: Run full suite**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `86 passed`. **Run AC-2 regression guard** explicitly:

```bash
pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: `1 passed`.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/graph_ingestor.py \
        tests/sync/test_graph_ingestor.py
git commit -m "$(cat <<'EOF'
feat(graph_ingestor): UPDATE selettivo (D3) preserves unmapped columns

Implements the UPDATE branch in populate_list write mode:
  - Compute the subset of MAPPED_COLUMNS where graph_value differs
    from db_row[col].
  - Build a SET clause covering ONLY those columns.
  - Execute UPDATE us_table SET col1=?, col2=? WHERE node_uuid=?

The 40+ pyarchinit-specific columns NOT in MAPPED_COLUMNS
(descrizione, foto, profondita, stato_di_conservazione, ...) are
never touched by the UPDATE, preserving the rich pyarchinit
schema across DB → Graph → DB' round-trips.

Pins D3 (UPDATE selettivo) directly: the test sets descrizione
on a row, mutates d_stratigrafica via the graph, ingests, and
asserts descrizione survived intact.

Tests: 86/86 pass. AC-2 regression guard green.
EOF
)"
```

---

## Group E — Round-trip + idempotent invariants

### Task E.1: Build the external graphml fixtures

**Files:**
- Create: `tests/sync/fixtures/build_mini_volterra_external.py`
- Create: `tests/sync/fixtures/mini_volterra_external.graphml`
- Create: `tests/sync/fixtures/mini_volterra_external_with_new_epoch.graphml`

- [ ] **Step 1: Write the generator script**

Create `tests/sync/fixtures/build_mini_volterra_external.py`:

```python
"""Generate the AI04 external-graph test fixtures.

Reads mini_volterra.sqlite, projects it via GraphProjector, then
emits two GraphML files:

1. mini_volterra_external.graphml — projection with one node's
   d_stratigrafica mutated; ingesting this back should produce
   exactly one ConflictRecord and one updated row.

2. mini_volterra_external_with_new_epoch.graphml — projection plus
   one synthetic EpochNode (periodo=99, fase='9.9') NOT in
   periodizzazione_table; used by the create-missing-epochs test.

Run: python tests/sync/fixtures/build_mini_volterra_external.py
Idempotent — re-running produces byte-identical files.
"""
from __future__ import annotations
import shutil
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLUGIN_ROOT / "ext_libs"))
import pandas  # noqa: F401
from lxml import etree as _etree  # noqa: F401
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

from modules.s3dgraphy.sync.graph_projector import GraphProjector

FIX = PLUGIN_ROOT / "tests" / "sync" / "fixtures"
SRC = FIX / "mini_volterra.sqlite"


def _write_graphml(graph, out: Path) -> None:
    """Use s3dgraphy's GraphMLExporter to serialise, then post-process
    so the output is canonical (deterministic ordering, no timestamps)."""
    from s3dgraphy.exporter.graphml.graphml_exporter import GraphMLExporter
    exporter = GraphMLExporter(graph)
    exporter.export(str(out), persist_auxiliary=False)


def main() -> int:
    import sqlite3
    conn = sqlite3.connect(SRC)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()

    p = GraphProjector()

    # 1. base external graph (mutate one d_stratigrafica)
    graph = p.populate_graph(SRC, sito=sito)
    for n in graph.nodes:
        attrs = getattr(n, "attributes", None) or {}
        if attrs.get("us"):
            attrs["d_stratigrafica"] = "EXT_GRAPH_VALUE"
            break
    _write_graphml(graph, FIX / "mini_volterra_external.graphml")
    print(f"OK — mini_volterra_external.graphml written")

    # 2. external with new epoch
    graph2 = p.populate_graph(SRC, sito=sito)
    from s3dgraphy.nodes.epoch_node import EpochNode
    e = EpochNode(node_id="epoch_99_9_9_synthetic",
                  name="Synthetic Period 99 Phase 9.9",
                  start_time=0.0, end_time=0.0)
    e.attributes = {"periodo": 99, "fase": "9.9"}
    graph2.add_node(e)
    _write_graphml(graph2, FIX / "mini_volterra_external_with_new_epoch.graphml")
    print(f"OK — mini_volterra_external_with_new_epoch.graphml written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run the generator**

```bash
python tests/sync/fixtures/build_mini_volterra_external.py
ls -la tests/sync/fixtures/mini_volterra_external*.graphml
```

Expected: two non-empty .graphml files.

- [ ] **Step 3: Sanity-load the fixtures from a Python REPL test**

```bash
pytest --collect-only tests/sync/ 2>&1 | tail -3
```

Expected: no errors during collection.

- [ ] **Step 4: Commit the generator + the two binary fixtures**

```bash
git add tests/sync/fixtures/build_mini_volterra_external.py \
        tests/sync/fixtures/mini_volterra_external.graphml \
        tests/sync/fixtures/mini_volterra_external_with_new_epoch.graphml
git commit -m "$(cat <<'EOF'
test(fixtures): mini_volterra_external graphml fixtures for AI04

Adds two pre-cooked GraphML files for the AI04 ingestion tests:

1. mini_volterra_external.graphml — the mini_volterra projection
   with one node's d_stratigrafica field mutated; ingesting this
   back into a fresh DB copy should produce exactly one
   ConflictRecord and one updated row. Used by the round-trip
   semantic invariant test in Group E.2.

2. mini_volterra_external_with_new_epoch.graphml — the projection
   plus a synthetic EpochNode (periodo=99, fase='9.9') NOT in
   periodizzazione_table. Used by the D5-B opt-in test.

The build script (build_mini_volterra_external.py) is committed so
the fixtures can be regenerated deterministically. Run it after any
schema change in pyarchinit's us_table that affects the bridge.

Both binaries are committed verbatim so test runs do not depend
on the generator script.
EOF
)"
```

### Task E.2: Round-trip semantic invariant test (D4-B)

**Files:**
- Create: `tests/sync/test_round_trip.py`

- [ ] **Step 1: Write the round-trip test**

Create `tests/sync/test_round_trip.py`:

```python
"""D4-B (AC-6): semantic round-trip invariant.

DB → GraphProjector → Graph → GraphIngestor → DB' must preserve
every column in MAPPED_COLUMNS for every row that participates.
Non-mapped columns may differ (UPDATE selettivo never touches them
but in principle the schema is free to add timestamps etc.).
"""
from __future__ import annotations
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest
import pandas  # noqa: F401
from lxml import etree as _etree  # noqa: F401
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")


def _read_sito(db):
    conn = sqlite3.connect(db)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    return sito


def _read_canonical(db, sito):
    """Return rows as a dict keyed by node_uuid → MAPPED_COLUMNS values."""
    from modules.s3dgraphy.sync.graph_ingestor import MAPPED_COLUMNS
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cols = ", ".join(MAPPED_COLUMNS)
    cur.execute(f"SELECT {cols} FROM us_table WHERE sito = ?", (sito,))
    rows = {row[MAPPED_COLUMNS.index("node_uuid")]:
            dict(zip(MAPPED_COLUMNS, row))
            for row in cur.fetchall()}
    conn.close()
    return rows


def test_round_trip_preserves_mapped_fields(tmp_path):
    """D4-B / AC-6 — DB → Graph → DB' is identity on MAPPED_COLUMNS."""
    src = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, src)
    sito = _read_sito(src)
    before = _read_canonical(src, sito)

    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    graph = GraphProjector().populate_graph(src, sito=sito)

    rt = tmp_path / "rt.sqlite"
    shutil.copy2(src, rt)
    GraphIngestor().populate_list(graph, rt, sito=sito, dry_run=False)

    after = _read_canonical(rt, sito)
    assert set(before.keys()) == set(after.keys()), \
        "round-trip lost / gained rows"
    for uuid, before_row in before.items():
        after_row = after[uuid]
        for col in before_row:
            assert before_row[col] == after_row[col], (
                f"round-trip mutated {col} for {uuid}: "
                f"before={before_row[col]!r}, after={after_row[col]!r}")
```

- [ ] **Step 2: Run — expect green**

```bash
pytest tests/sync/test_round_trip.py -v
```

Expected: `1 passed`.

- [ ] **Step 3: Run full suite**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `87 passed`.

- [ ] **Step 4: Commit**

```bash
git add tests/sync/test_round_trip.py
git commit -m "$(cat <<'EOF'
test(round_trip): semantic invariant DB → Graph → DB' (D4-B / AC-6)

Pins the round-trip semantic invariant from spec §4.4:
  - Read MAPPED_COLUMNS from us_table for sito X.
  - Project to in-memory s3dgraphy.Graph via GraphProjector.
  - Copy DB to a fresh path, ingest the graph back via
    GraphIngestor.populate_list(dry_run=False).
  - Assert every (node_uuid, mapped_column) pair survived
    unchanged — same row count, same values.

The test runs the WHOLE pipeline end-to-end (no mocks) against
mini_volterra.sqlite. If a future change to GraphProjector or
GraphIngestor regresses round-trip safety, this test goes red.

Tests: 87/87 pass.
EOF
)"
```

### Task E.3: Idempotent ingestion test (D4-C)

**Files:**
- Create: `tests/sync/test_idempotent_ingest.py`

- [ ] **Step 1: Write the test**

Create `tests/sync/test_idempotent_ingest.py`:

```python
"""D4-C (AC-7): external-graph ingestion converges after one iteration.

Three consecutive populate_list() runs against the same external
GraphML must produce identical IngestResult counts (skipped grows,
inserted/updated drop to 0 from run 2 onwards).
"""
from __future__ import annotations
import shutil
import sys
from pathlib import Path

import pandas  # noqa: F401
from lxml import etree as _etree  # noqa: F401
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")
EXTERNAL_GRAPHML = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
                    / "mini_volterra_external.graphml")


def _load_graph(graphml_path):
    from s3dgraphy.importer.graphml_importer import GraphMLImporter
    importer = GraphMLImporter(filepath=str(graphml_path))
    return importer.parse()


def _read_sito(db):
    import sqlite3
    conn = sqlite3.connect(db)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    return sito


def test_external_graph_ingest_idempotent(tmp_path):
    """D4-C / AC-7 — three runs converge."""
    db = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, db)
    sito = _read_sito(db)
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor

    graph = _load_graph(EXTERNAL_GRAPHML)
    g = GraphIngestor()
    r1 = g.populate_list(graph, db, sito=sito, dry_run=False)
    r2 = g.populate_list(graph, db, sito=sito, dry_run=False)
    r3 = g.populate_list(graph, db, sito=sito, dry_run=False)

    # Convergence: r2 and r3 must look the same.
    assert r2.inserted == 0
    assert r2.updated == 0
    assert r2.skipped == r2.applied + r2.skipped or r2.applied == 0
    assert r3.applied == r2.applied
    assert r3.skipped == r2.skipped
```

- [ ] **Step 2: Run — expect green**

```bash
pytest tests/sync/test_idempotent_ingest.py -v
```

Expected: `1 passed`.

- [ ] **Step 3: Run full suite**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `88 passed`.

- [ ] **Step 4: Commit**

```bash
git add tests/sync/test_idempotent_ingest.py
git commit -m "$(cat <<'EOF'
test(idempotent_ingest): D4-C external-graph convergence (AC-7)

Pins the lossy-but-idempotent invariant from spec §4.5:
  - Load mini_volterra_external.graphml (the AI04 fixture with one
    d_stratigrafica mutation).
  - Run populate_list() three consecutive times against a fresh
    copy of mini_volterra.sqlite.
  - Assert from run 2 onwards inserted == 0 and updated == 0
    (the DB is now coherent with the graph).
  - Assert run 3 has identical applied / skipped counts to run 2.

This guarantees that re-importing the same external graph never
'flickers' the DB state — useful for retry-after-failure scenarios
and for the future SyncEngine pull cycle.

Tests: 88/88 pass.
EOF
)"
```

---

## Group F — CLI helper

### Task F.1: Write `scripts/s3dgraphy_sync.py`

**Files:**
- Create: `scripts/s3dgraphy_sync.py`

- [ ] **Step 1: Write the CLI helper**

Create `scripts/s3dgraphy_sync.py`:

```python
#!/usr/bin/env python3
"""CLI helper for the AI04 bidirectional bridge.

Usage:
    python scripts/s3dgraphy_sync.py export \\
        --db DB --graphml OUT --sito SITO

    python scripts/s3dgraphy_sync.py import \\
        --db DB --graphml IN --sito SITO
        [--apply]                  # default is dry-run
        [--create-epochs]
        [--mapping NAME]           # default: pyarchinit_us_mapping

Default for `import` is dry-run; pass `--apply` to actually write.

Exit codes:
    0  success
    1  GraphSyncError (any subclass) or expected validation failure
    2  argparse error / unknown command
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "ext_libs"))


def _setup_path() -> None:
    # pin pandas + lxml first to avoid the broken vendored pandas
    import pandas  # noqa: F401
    from lxml import etree as _etree  # noqa: F401
    for mod in [m for m in list(sys.modules)
                if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
        del sys.modules[mod]


def cmd_export(args) -> int:
    _setup_path()
    from modules.s3dgraphy.sync.graphml_writer import (
        export_graphml, EmptyGraphError, GraphMLExportError)
    try:
        result = export_graphml(
            db_path=Path(args.db),
            mapping=args.mapping,
            output_path=Path(args.graphml),
            site_filter=args.sito,
        )
    except (EmptyGraphError, GraphMLExportError) as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    print(f"OK — {args.graphml}")
    print(f"   {result.node_count} nodes, {result.edge_count} edges, "
          f"{result.epoch_count} epochs, "
          f"{result.tred_removed_edges} redundancies removed")
    return 0


def cmd_import(args) -> int:
    _setup_path()
    from s3dgraphy.importer.graphml_importer import GraphMLImporter
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphIngestor, GraphSyncError)

    try:
        graph = GraphMLImporter(filepath=str(args.graphml)).parse()
    except Exception as e:
        print(f"ERROR: failed to load graph from {args.graphml}: {e}",
              file=sys.stderr)
        return 1

    g = GraphIngestor()
    try:
        result = g.populate_list(
            graph,
            db_path=Path(args.db),
            sito=args.sito,
            dry_run=not args.apply,
            create_missing_epochs=args.create_epochs,
        )
    except GraphSyncError as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    label = "DRY-RUN" if result.dry_run else "WRITTEN"
    print(f"OK [{label}] — applied={result.applied} "
          f"(inserted={result.inserted}, updated={result.updated}, "
          f"skipped={result.skipped}), epochs_created={result.epochs_created}")
    if result.conflicts:
        print(f"   {len(result.conflicts)} conflicts:")
        for c in result.conflicts[:10]:
            print(f"     - {c.node_uuid[:8]}.{c.field}: "
                  f"DB={c.db_value!r} → graph={c.graph_value!r}")
        if len(result.conflicts) > 10:
            print(f"     ({len(result.conflicts) - 10} more)")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="s3dgraphy_sync",
        description="PyArchInit ↔ s3dgraphy bridge CLI (AI04).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_exp = sub.add_parser("export", help="DB → GraphML")
    p_exp.add_argument("--db", required=True)
    p_exp.add_argument("--graphml", required=True)
    p_exp.add_argument("--sito", required=True)
    p_exp.add_argument("--mapping", default="pyarchinit_us_mapping")
    p_exp.set_defaults(func=cmd_export)

    p_imp = sub.add_parser("import", help="GraphML → DB")
    p_imp.add_argument("--db", required=True)
    p_imp.add_argument("--graphml", required=True)
    p_imp.add_argument("--sito", required=True)
    p_imp.add_argument("--apply", action="store_true",
                       help="actually write to DB (default: dry-run)")
    p_imp.add_argument("--create-epochs", action="store_true",
                       help="auto-create missing periodizzazione rows")
    p_imp.set_defaults(func=cmd_import)

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.WARNING)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

- [ ] **Step 2: Smoke-test by running export**

```bash
python scripts/s3dgraphy_sync.py export \
    --db tests/sync/fixtures/mini_volterra.sqlite \
    --graphml /tmp/cli_smoke.graphml \
    --sito "$(sqlite3 tests/sync/fixtures/mini_volterra.sqlite 'SELECT DISTINCT sito FROM us_table LIMIT 1')"
```

Expected: `OK — /tmp/cli_smoke.graphml` followed by metrics. Cleanup: `rm /tmp/cli_smoke.graphml`.

- [ ] **Step 3: Commit**

```bash
git add scripts/s3dgraphy_sync.py
git commit -m "$(cat <<'EOF'
feat(scripts): s3dgraphy_sync.py CLI helper for AI04 bridge

Adds a standalone CLI that wraps GraphProjector / GraphIngestor for
shell scripting and CI integration. Two subcommands:

- export: thin wrapper over modules.s3dgraphy.sync.graphml_writer.
  export_graphml(). Reuses the AI03 export path for parity.

- import: invokes GraphIngestor.populate_list(). DEFAULT IS DRY-RUN
  (per spec D7 + AC-10). The user must pass --apply to actually
  write; --create-epochs enables D5-B opt-in epoch insertion.

Exit codes:
  0 success
  1 GraphSyncError (any subclass)
  2 argparse error

Compatible with the test_cli_helper.py subprocess tests landing in
F.2.
EOF
)"
```

### Task F.2: Subprocess tests for the CLI

**Files:**
- Create: `tests/sync/test_cli_helper.py`

- [ ] **Step 1: Write tests**

Create `tests/sync/test_cli_helper.py`:

```python
"""Subprocess tests for scripts/s3dgraphy_sync.py.

Exercises the CLI surface end-to-end via subprocess.run() so test
runs match what a user types in the shell.
"""
from __future__ import annotations
import hashlib
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = PLUGIN_ROOT / "scripts" / "s3dgraphy_sync.py"
FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")
EXTERNAL_GRAPHML = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
                    / "mini_volterra_external.graphml")


def _run(*args, cwd=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
        cwd=str(cwd) if cwd else str(PLUGIN_ROOT),
    )


def _sito(db):
    conn = sqlite3.connect(db)
    s = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    return s


def test_cli_export_subprocess(tmp_path):
    db = tmp_path / "x.sqlite"
    shutil.copy2(FIXTURE_DB, db)
    out = tmp_path / "out.graphml"
    r = _run("export", "--db", str(db), "--graphml", str(out),
             "--sito", _sito(db))
    assert r.returncode == 0, r.stderr
    assert out.exists() and out.stat().st_size > 1000


def test_cli_import_dry_run_default(tmp_path):
    """AC-10 — no --apply means no DB writes."""
    db = tmp_path / "x.sqlite"
    shutil.copy2(FIXTURE_DB, db)
    sha_before = hashlib.sha256(db.read_bytes()).hexdigest()
    r = _run("import", "--db", str(db),
             "--graphml", str(EXTERNAL_GRAPHML),
             "--sito", _sito(db))
    assert r.returncode == 0, r.stderr
    assert "DRY-RUN" in r.stdout
    sha_after = hashlib.sha256(db.read_bytes()).hexdigest()
    assert sha_before == sha_after, "import without --apply modified DB"


def test_cli_import_apply_writes(tmp_path):
    db = tmp_path / "x.sqlite"
    shutil.copy2(FIXTURE_DB, db)
    sha_before = hashlib.sha256(db.read_bytes()).hexdigest()
    r = _run("import", "--db", str(db),
             "--graphml", str(EXTERNAL_GRAPHML),
             "--sito", _sito(db), "--apply")
    assert r.returncode == 0, r.stderr
    assert "WRITTEN" in r.stdout
    sha_after = hashlib.sha256(db.read_bytes()).hexdigest()
    assert sha_before != sha_after, "import --apply did not modify DB"


def test_cli_export_missing_db_exits_1(tmp_path):
    r = _run("export", "--db", str(tmp_path / "nope.sqlite"),
             "--graphml", str(tmp_path / "out.graphml"),
             "--sito", "X")
    assert r.returncode == 1
    assert "ERROR" in r.stderr
```

- [ ] **Step 2: Run tests**

```bash
pytest tests/sync/test_cli_helper.py -v
```

Expected: `4 passed`.

- [ ] **Step 3: Run full suite**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `92 passed`.

- [ ] **Step 4: Commit**

```bash
git add tests/sync/test_cli_helper.py
git commit -m "$(cat <<'EOF'
test(cli_helper): subprocess tests for scripts/s3dgraphy_sync.py

Four L2 tests exercising the CLI via subprocess.run():
  - test_cli_export_subprocess: export round-trip produces a
    non-empty .graphml.
  - test_cli_import_dry_run_default: AC-10 — running 'import'
    without --apply leaves the DB sha256 unchanged AND prints
    DRY-RUN in the output.
  - test_cli_import_apply_writes: with --apply, the DB sha256
    changes and the output prints WRITTEN.
  - test_cli_export_missing_db_exits_1: nonexistent DB → exit 1
    with ERROR in stderr.

These pin the AC-10 contract that --apply is mandatory for any
CLI-driven write.

Tests: 92/92 pass.
EOF
)"
```

---

## Group G — UI Import tab in `S3DGraphyExportDialog`

### Task G.1: Wrap the existing dialog body in a QTabWidget + add Import tab

**Files:**
- Modify: `modules/s3dgraphy/s3dgraphy_dot_bridge.py` (the `S3DGraphyExportDialog` class around line 293)

The Export tab body must remain bit-for-bit equivalent. The Import tab is a new widget set, hooked to a new handler method. AC-2 byte-identical baseline catches any regression on the Export side.

- [ ] **Step 1: Read the current dialog**

```bash
sed -n '293,320p' modules/s3dgraphy/s3dgraphy_dot_bridge.py
```

Identify `def setupUI(self):` — the existing body adds widgets directly to `layout`.

- [ ] **Step 2: Refactor `setupUI()` to use a QTabWidget**

Use the Edit tool. The new `setupUI()` body (replacing the existing one verbatim) becomes:

```python
        def setupUI(self):
            layout = QVBoxLayout()

            # Title (unchanged from AI03)
            title = QLabel("<h3>Extended Matrix — s3dgraphy Bridge</h3>")
            layout.addWidget(title)

            # Tabs
            self.tabs = QTabWidget()
            layout.addWidget(self.tabs)

            # ---- Tab "Export" — existing AI03 body, untouched ----
            export_tab = QWidget()
            export_layout = QVBoxLayout()

            desc = QLabel(
                "This export combines s3dgraphy Extended Matrix processing with "
                "yEd-compatible GraphML output for advanced visualization."
            )
            desc.setWordWrap(True)
            export_layout.addWidget(desc)

            format_group = QGroupBox("Export Formats")
            format_layout = QVBoxLayout()
            self.cb_dot = QCheckBox("DOT Format (Graphviz)")
            self.cb_dot.setChecked(True)
            format_layout.addWidget(self.cb_dot)
            self.cb_graphml = QCheckBox("GraphML Format (yEd compatible)")
            self.cb_graphml.setChecked(True)
            format_layout.addWidget(self.cb_graphml)
            self.cb_json = QCheckBox("JSON Format (s3dgraphy native)")
            self.cb_json.setChecked(True)
            format_layout.addWidget(self.cb_json)
            self.cb_phased = QCheckBox("Phased Matrix (chronological analysis)")
            self.cb_phased.setChecked(False)
            format_layout.addWidget(self.cb_phased)
            format_group.setLayout(format_layout)
            export_layout.addWidget(format_group)

            options_group = QGroupBox("Processing Options")
            options_layout = QVBoxLayout()
            self.cb_validate = QCheckBox("Validate stratigraphic sequence")
            self.cb_validate.setChecked(True)
            options_layout.addWidget(self.cb_validate)
            self.cb_auto_layout = QCheckBox("Generate yEd auto-layout hints")
            self.cb_auto_layout.setChecked(True)
            options_layout.addWidget(self.cb_auto_layout)
            self.cb_period_colors = QCheckBox("Apply period-based coloring")
            self.cb_period_colors.setChecked(True)
            options_layout.addWidget(self.cb_period_colors)
            options_group.setLayout(options_layout)
            export_layout.addWidget(options_group)

            self.progress = QProgressBar()
            self.progress.setVisible(False)
            export_layout.addWidget(self.progress)

            export_btn_layout = QHBoxLayout()
            self.btn_export = QPushButton("Export")
            self.btn_export.clicked.connect(self.on_export)
            export_btn_layout.addWidget(self.btn_export)
            export_layout.addLayout(export_btn_layout)

            export_tab.setLayout(export_layout)
            self.tabs.addTab(export_tab, "Export")

            # ---- Tab "Import" — NEW (AI04) ----
            import_tab = QWidget()
            import_layout = QVBoxLayout()

            import_desc = QLabel(
                "Import a GraphML file produced by s3dgraphy / Heriverse / EM\n"
                "Datacenter back into the pyarchinit DB. Default is dry-run\n"
                "preview; click Anteprima first, review the diff, then Applica."
            )
            import_desc.setWordWrap(True)
            import_layout.addWidget(import_desc)

            file_row = QHBoxLayout()
            self.le_import_file = QLineEdit()
            self.le_import_file.setPlaceholderText("/path/to/external.graphml")
            self.btn_browse = QPushButton("Browse…")
            self.btn_browse.clicked.connect(self._on_browse_import)
            file_row.addWidget(self.le_import_file)
            file_row.addWidget(self.btn_browse)
            import_layout.addLayout(file_row)

            self.cb_create_epochs = QCheckBox("Crea periodi mancanti se assenti")
            self.cb_create_epochs.setChecked(False)
            import_layout.addWidget(self.cb_create_epochs)

            import_btn_layout = QHBoxLayout()
            self.btn_preview = QPushButton("Anteprima")
            self.btn_preview.clicked.connect(self._on_import_preview)
            self.btn_apply = QPushButton("Applica")
            self.btn_apply.setEnabled(False)  # disabled until preview clicked
            self.btn_apply.clicked.connect(self._on_import_apply)
            import_btn_layout.addWidget(self.btn_preview)
            import_btn_layout.addWidget(self.btn_apply)
            import_layout.addLayout(import_btn_layout)

            self.import_summary = QLabel("(no preview yet)")
            self.import_summary.setWordWrap(True)
            import_layout.addWidget(self.import_summary)

            import_tab.setLayout(import_layout)
            self.tabs.addTab(import_tab, "Import")

            # ---- Common bottom row ----
            self.btn_cancel = QPushButton("Cancel")
            self.btn_cancel.clicked.connect(self.reject)
            layout.addWidget(self.btn_cancel)

            self.setLayout(layout)
```

Add the three new handler methods just below `on_export()`:

```python
        def _on_browse_import(self):
            """File picker for the Import tab."""
            path, _ = QFileDialog.getOpenFileName(
                self, "Select GraphML to import", "",
                "GraphML files (*.graphml);;All files (*)")
            if path:
                self.le_import_file.setText(path)

        def _on_import_preview(self):
            """Run dry-run populate_list and show summary."""
            from pathlib import Path
            from s3dgraphy.importer.graphml_importer import GraphMLImporter
            from modules.s3dgraphy.sync.graph_ingestor import (
                GraphIngestor, GraphSyncError)
            graphml_path = self.le_import_file.text().strip()
            if not graphml_path or not Path(graphml_path).exists():
                QMessageBox.warning(self, "No file",
                                    "Please pick a .graphml file first.")
                return
            try:
                graph = GraphMLImporter(filepath=graphml_path).parse()
                result = GraphIngestor().populate_list(
                    graph, self.db_manager.get_sqlite_path(),
                    sito=self.site,
                    dry_run=True,
                    create_missing_epochs=self.cb_create_epochs.isChecked(),
                )
            except GraphSyncError as e:
                QMessageBox.critical(
                    self, type(e).__name__,
                    f"{type(e).__name__}: {e}")
                return
            self._last_preview_result = result
            self._last_preview_path = graphml_path
            self.import_summary.setText(
                f"Preview: applied={result.applied} "
                f"(inserted={result.inserted}, updated={result.updated}, "
                f"skipped={result.skipped}, conflicts={len(result.conflicts)}, "
                f"epochs_created={result.epochs_created})")
            self.btn_apply.setEnabled(True)

        def _on_import_apply(self):
            """Run write-mode populate_list."""
            from pathlib import Path
            from s3dgraphy.importer.graphml_importer import GraphMLImporter
            from modules.s3dgraphy.sync.graph_ingestor import (
                GraphIngestor, GraphSyncError)
            try:
                graph = GraphMLImporter(
                    filepath=self._last_preview_path).parse()
                result = GraphIngestor().populate_list(
                    graph, self.db_manager.get_sqlite_path(),
                    sito=self.site,
                    dry_run=False,
                    create_missing_epochs=self.cb_create_epochs.isChecked(),
                )
            except GraphSyncError as e:
                QMessageBox.critical(self, type(e).__name__, str(e))
                return
            QMessageBox.information(
                self, "Import complete",
                f"Applied: {result.applied}\n"
                f"  inserted: {result.inserted}\n"
                f"  updated: {result.updated}\n"
                f"  skipped: {result.skipped}\n"
                f"  epochs created: {result.epochs_created}\n"
                f"  conflicts (resolved as graph_wins): {len(result.conflicts)}")
            self.btn_apply.setEnabled(False)
```

Make sure the imports at the top of the file include the new Qt symbols if missing. The dialog file already imports `QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QGroupBox, QPushButton, QProgressBar, QMessageBox, QFileDialog`; verify and add `QTabWidget, QWidget, QLineEdit` if absent.

- [ ] **Step 3: Manually smoke-test the dialog in QGIS**

This step is user-driven; cannot be automated. Open QGIS, open a project, open the Extended Matrix dialog, verify the two tabs render and the Export tab still produces output identical to the AI03 baseline. **Block on a green AC-2 test as the closest automated proxy:**

```bash
pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: `1 passed`.

- [ ] **Step 4: Run full suite**

```bash
pytest tests/sync/ tests/migrations/ -q
```

Expected: `92 passed`.

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/s3dgraphy_dot_bridge.py
git commit -m "$(cat <<'EOF'
feat(s3dgraphy_dot_bridge): Import tab in S3DGraphyExportDialog

Wraps the existing single-page dialog body in a QTabWidget with:

  - Tab "Export": the AI03 widgets and on_export() handler,
    untouched. AC-2 byte-identical baseline test stays green.
  - Tab "Import" (new): file picker + create-missing-epochs
    checkbox + Anteprima/Applica buttons. Anteprima runs
    GraphIngestor.populate_list(dry_run=True) and shows the
    counters in a label; Applica is disabled until Anteprima
    has been clicked at least once, then runs dry_run=False
    and shows a QMessageBox.information with the result.

GraphSyncError subclasses are caught and surfaced via
QMessageBox.critical with the class name as title (so the user
sees e.g. SchemaMismatchError as a category).

Tests: 92/92 pass. AC-2 regression guard green.
EOF
)"
```

---

## Group H — Release packaging

### Task H.1: Dev-log entry

**Files:**
- Modify: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

- [ ] **Step 1: Append a new section at the END of the file**

Use the Edit tool to add at the bottom:

````markdown

---

# Phase 2 — AI04 Bridge bidirezionale

**Date:** 2026-05-08 → ...  
**Tag:** `phase2-ai04-bridge-bidirectional-5.3.0-alpha`  
**Spec:** `docs/superpowers/specs/2026-05-08-ai04-bridge-bidirectional-design.md`  
**Plan:** `docs/superpowers/plans/2026-05-08-ai04-bridge-bidirectional.md`

## What was built

Library bridge between PyArchInit SQL tables and the s3dgraphy
in-memory `Graph` model. New public surface in
`modules/s3dgraphy/sync/`:

- `GraphProjector.populate_graph(db_path, sito) -> Graph` — Strategy
  D thin wrapper around `_enrich_pyarchinit_graph` (promotion to a
  proper class is queued for AI05).
- `GraphIngestor.populate_list(graph, db_path, sito, *, dry_run,
  create_missing_epochs) -> IngestResult` — atomic transaction,
  UPDATE selettivo on the 12 mapped columns, full exception
  hierarchy.
- `ConflictResolver` stub returning `ConflictResolution.GRAPH_WINS`.
- `IngestResult` + `ConflictRecord` frozen dataclasses.
- CLI `scripts/s3dgraphy_sync.py` with `export`/`import` subcommands;
  `import` defaults to dry-run, `--apply` required for writes.
- `S3DGraphyExportDialog` gets a QTabWidget with the existing Export
  tab (untouched) plus a new Import tab.

## Acceptance criteria status

All 15 AC pass. AC-2 byte-identical baseline stayed green at every
commit (regression guard for AI03).

## Manual smoke gate (G in plan)

User-driven validation in QGIS — see plan Group G Task G.1 step 3
and Group H Task H.4.

## Carry-overs

- `paradata.graphml` per project — AI05.
- Pluggable `ConflictResolver` strategies — AI06.
- `failure_mode={atomic, best_effort, by_group}` — AI06+.
- Promotion of `GraphProjector` from wrap (D) to real class (A)
  — AI05.
````

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md
git commit -m "$(cat <<'EOF'
docs(dev-log): Phase 2 / AI04 bridge bidirectional entry

Records AI04 outcome: new GraphProjector / GraphIngestor /
ConflictResolver-stub / CLI / Import tab. All 15 acceptance
criteria passed; AC-2 byte-identical baseline stayed green at
every commit.

Carry-overs documented: paradata.graphml (AI05), pluggable
resolvers (AI06), configurable failure_mode (AI06+), Strategy A
promotion (AI05).
EOF
)"
```

### Task H.2: CHANGELOG bilingual entry

**Files:**
- Modify: `dev_logs/CHANGELOG.md`

- [ ] **Step 1: Find the file's current top-of-file format**

```bash
head -30 dev_logs/CHANGELOG.md
```

- [ ] **Step 2: Prepend a new `## [5.3.0-alpha]` section**

Use the Edit tool. The new entry (placed immediately under the file's title / above the previous `## [5.2.0-alpha]` block) reads:

```markdown
## [5.3.0-alpha] - 2026-05-08

### Italiano

- **Phase 2 / AI04 — Bridge bidirezionale PyArchInit ↔ s3dgraphy.** Nuova API pubblica `GraphProjector.populate_graph(db, sito)` e `GraphIngestor.populate_list(graph, db, sito, dry_run, create_missing_epochs)` per il round-trip DB↔grafo. Strategia D wrapper su `_enrich_pyarchinit_graph` (zero impatto sul path AI03; AC-2 byte-identical baseline garantita).
- **Tab "Import" nel dialog Extended Matrix.** Nuova tab con file picker, anteprima dry-run dei conflitti, e bottone "Applica" per scrivere nel DB. La tab "Export" è inalterata.
- **CLI helper `scripts/s3dgraphy_sync.py`** con sottocomandi `export` e `import`. L'import è dry-run di default; `--apply` obbligatorio per scrivere.
- **`UPDATE` selettivo sui 12 campi mappati.** Le 40+ colonne pyarchinit-specifiche (descrizione, foto, profondita, ...) sono preservate intatte durante il round-trip.
- **Transazioni atomiche.** Qualsiasi fallimento durante l'ingestion fa ROLLBACK al DB; mai stati misti.

### English

- **Phase 2 / AI04 — Bidirectional PyArchInit ↔ s3dgraphy bridge.** New public API `GraphProjector.populate_graph(db, sito)` and `GraphIngestor.populate_list(graph, db, sito, dry_run, create_missing_epochs)` for round-trip DB↔graph. Strategy D wrapper on `_enrich_pyarchinit_graph` (zero impact on the AI03 path; AC-2 byte-identical baseline guarantee).
- **"Import" tab in the Extended Matrix dialog.** New tab with file picker, dry-run conflict preview, and "Apply" button for committing to the DB. The "Export" tab is unchanged.
- **CLI helper `scripts/s3dgraphy_sync.py`** with `export` and `import` subcommands. Import is dry-run by default; `--apply` is required to actually write.
- **Selective `UPDATE` on the 12 mapped columns.** The 40+ pyarchinit-specific columns (descrizione, foto, profondita, ...) are preserved untouched during round-trip.
- **Atomic transactions.** Any ingestion failure ROLLBACKs the DB; no mixed states.

```

- [ ] **Step 3: Commit**

```bash
git add dev_logs/CHANGELOG.md
git commit -m "$(cat <<'EOF'
docs(changelog): 5.3.0-alpha — AI04 bridge bidirectional (IT + EN)

Bilingual entry summarising the AI04 release:
- New GraphProjector + GraphIngestor + ConflictResolver-stub
  public API (Strategy D wrap, AC-2 baseline preserved).
- Import tab in S3DGraphyExportDialog (Export tab untouched).
- CLI helper scripts/s3dgraphy_sync.py with export/import
  subcommands (dry-run default, --apply for writes).
- UPDATE selettivo preserving 40+ unmapped columns.
- Atomic transaction guarantee.
EOF
)"
```

### Task H.3: Verify clean working tree before tag

**Files:** none (git operation)

- [ ] **Step 1: Verify state**

```bash
git status --short | grep -vE '^\?\?'
git rev-list --left-right --count HEAD...@{u}
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"
pytest tests/sync/ tests/migrations/ -q
```

Expected:
- tracked changes empty
- ahead/behind: `0\t0` (assuming you've been pushing along the way) OR `N\t0` if there are unpushed commits — Task H.5 will push them all.
- co-author count: `0`
- pytest: ≥ 92 passing.

### Task H.4: Manual smoke gate

**Files:** none (manual QA in QGIS)

This is **user-driven**. Cannot be automated.

- [ ] **Step 1: Restart QGIS** — close and relaunch.

- [ ] **Step 2: Open a real project** with the Volterra database.

- [ ] **Step 3: Open the Extended Matrix dialog** — verify the QTabWidget renders both tabs.

- [ ] **Step 4: Click the "Export" tab** — verify the format checkboxes match the AI03 layout. Click "Export", select an output directory, verify the GraphML produced is visually identical to a previous AI03 export.

- [ ] **Step 5: Click the "Import" tab.** Pick `tests/sync/fixtures/mini_volterra_external.graphml` (or any external graphml). Click "Anteprima". Verify the summary label shows non-zero `applied` (it will show `applied=N (inserted=0, updated=1, skipped=N-1, conflicts=1)` for the canonical mutation).

- [ ] **Step 6: Click "Applica".** Verify a `QMessageBox.information` shows the result counts.

- [ ] **Step 7: Re-open the original DB row** that was mutated. Verify the `d_stratigrafica` column was updated to `EXT_GRAPH_VALUE` and the unmapped columns (e.g. `descrizione`) are intact.

- [ ] **Step 8: Smoke-test the matrix-classic (graphviz) export** to make sure that pipeline (touched in 5.2.0-alpha) still renders a JPG, not just .dot files.

- [ ] **Step 9: User confirms gate passed** — proceed to H.5.

### Task H.5: Tag + push

**Files:** none (git operations)

- [ ] **Step 1: Verify clean tree**

```bash
git status --short | grep -vE '^\?\?'
```

Expected: empty.

- [ ] **Step 2: Create the release tag**

```bash
git tag -a phase2-ai04-bridge-bidirectional-5.3.0-alpha \
    -m "Phase 2 / AI04: bridge bidirezionale PyArchInit ↔ s3dgraphy"
git tag -l | grep -E "phase2|pre-ai04"
```

Expected:
```
phase2-ai03-graphml-delegation-5.2.0-alpha
phase2-ai04-bridge-bidirectional-5.3.0-alpha
pre-ai03-graphml-delegation
pre-ai04-bridge
```

- [ ] **Step 3: Push branch + tag**

```bash
git push origin Stratigraph_00001
git push origin phase2-ai04-bridge-bidirectional-5.3.0-alpha
```

- [ ] **Step 4: Verify on remote**

```bash
git ls-remote --tags origin 2>&1 | grep -E "phase2-ai04|pre-ai04"
```

Expected: two `refs/tags/...` lines (`phase2-ai04-bridge-bidirectional-5.3.0-alpha` and `pre-ai04-bridge` — the latter was pushed in Group 0.2).

- [ ] **Step 5: Confirm zero `Co-Authored-By` trailers in any AI04 commit**

```bash
git log phase2-ai03-graphml-delegation-5.2.0-alpha..phase2-ai04-bridge-bidirectional-5.3.0-alpha \
    --format=%B | grep -c "Co-Authored-By"
```

Expected: `0`.

---

## Self-review checklist (run inline before delivering the plan)

Reviewed against the spec on 2026-05-08:

**1. Spec coverage**

- §1 Overview → addressed by file structure + Group narrative.
- §2 D1–D10 → each decision has at least one task pinning it (see test matrix in "Test strategy" section).
- §3 Components: §3.1 GraphProjector → Group B; §3.2 GraphIngestor → Groups C+D; §3.3 ConflictResolver → A.2; §3.4 IngestResult / ConflictRecord → A.1; §3.5 CLI → F.1; §3.6 UI → G.1.
- §4 Data flow: §4.1 → B.2; §4.2 dry-run → C.2/C.3; §4.3 write mode → D.1/D.2; §4.4 round-trip → E.2; §4.5 idempotent → E.3; §4.6 CLI → F.2.
- §5 Error handling: §5.1 hierarchy → A.3; §5.2 fatal/non-fatal → C.1+C.2+C.3+D.1; §5.3 logging → present in graph_ingestor.py module init; §5.4 UI surfacing → G.1.
- §6 Testing: 16 new tests (AI03 baseline + 5 projector + 7 ingestor + 1 round-trip + 1 idempotent + 4 CLI = 18, exceeds the spec's "16 new" target).
- §7 Acceptance criteria: AC-1 → B.3; AC-2 → 0.3 + every group; AC-3 → C.4; AC-4 → C.2; AC-5 → D.2; AC-6 → E.2; AC-7 → E.3; AC-8 → C.3; AC-9 → D.1; AC-10 → F.2; AC-11 → G.1 + H.4 manual; AC-12 → "≥92" exceeds "≥75"; AC-13 → manual; AC-14 + AC-15 → entire suite invariant.
- §8 Release plan → Group H mirrors it.
- §9 Out of scope → "Explicitly NOT touched" section + reminders in commits.
- §10 Risks → mitigation hooks present (rapporti JSON parse-then-compare in `_values_equal`, fase string CAST AS TEXT in epoch lookup, MAPPED_COLUMNS exhaustive).

**2. Placeholder scan**

- No `TODO`, `TBD`, `FIXME`, `implement later`, `Add appropriate error handling` — every task has explicit code.
- No `Similar to Task N` — code is repeated where needed.
- All file paths absolute or repo-relative.

**3. Type consistency**

- `GraphProjector.populate_graph(db_path, sito)` — same signature in B.2, B.3, E.2, F.1.
- `GraphIngestor.populate_list(graph, db_path, sito, *, dry_run, create_missing_epochs)` — same in C.1, C.2, C.3, D.1, D.2, E.3, F.1, G.1.
- `IngestResult` field names — same across A.1, C, D, E, F, G.
- `ConflictResolver.resolve(db_row, graph_value, field)` — A.2 + C.2.
- `MissingEpochError(missing=...)` — A.3 + C.3.
- `MAPPED_COLUMNS` — A.3 + C.2 + D.2 + E.2.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-08-ai04-bridge-bidirectional.md`. Two execution options:**

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

**Which approach?**
