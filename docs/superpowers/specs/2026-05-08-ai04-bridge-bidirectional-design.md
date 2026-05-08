# AI04 — Bridge bidirezionale PyArchInit ↔ s3dgraphy (design spec)

**Date:** 2026-05-08 · **Author:** Enzo Cocca · **Status:** Approved
(brainstorming chiuso; implementation plan to be drafted via
`superpowers:writing-plans`).

**Parent spec:** `docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md`
(see §3.2 GraphProjector, §3.6 GraphIngestor, §3.7 ConflictResolver,
§11 Implementation phasing).

**Predecessor:** `docs/superpowers/specs/2026-05-07-ai03-graphml-delegation-design.md`
shipped as tag `phase2-ai03-graphml-delegation-5.2.0-alpha` on 2026-05-08.

**Target tag:** `phase2-ai04-bridge-bidirectional-5.3.0-alpha`.

---

## 1. Overview

AI04 implements the **bidirectional library bridge** between the
PyArchInit SQL data model and the in-memory s3dgraphy `Graph` object
model. It satisfies T5.4 meeting (2026-05-04) action item AI04
("bridge prototype") and Reference Document v0.1 §6 macro-functions
`populate_graph()` / `populate_list()`.

Scope is intentionally **minimal Phase 2 stratigraphic layer**: only
stratigraphic-family node types (`StratigraphicUnit`, `USM`, `USVs`,
`USVn`, `USD`, `SF`, `VSF`, `CON`, `DOC`, `Extractor`, `Combinar`,
`property`) plus their epoch metadata. Paradata authoring
(`paradata.graphml` per project, `AuthorNode`, `LicenseNode`,
`EmbargoNode`) is deferred to AI05. Networking (`SyncEngine`,
`DatacenterClient`, REST/SPARQL) is deferred to Phase 3+.

Non-goals: configurable conflict resolution strategies, partial
commit modes, multi-graph context, paradata.graphml CRUD, real-time
collaborative editing.

---

## 2. Decisions captured during brainstorming (2026-05-08)

| ID | Topic | Decision | Rationale |
|----|---|---|---|
| **D1** | Scope | Spec-faithful: `GraphProjector` + `GraphIngestor` + `ConflictResolver` stub. No new menu, no paradata.graphml support. | Minimal Phase 2 stratigraphic layer; aligns with parent spec §3 components without bundling AI05/AI06 work. |
| **D2** | `GraphProjector` refactor | Strategy D — thin wrapper around the existing `_enrich_pyarchinit_graph()` in `graphml_writer.py`. Promote to proper class (Strategy A) in AI05+. | Zero diff on AI03-shipped code path. Promotion path documented in `project_ai04_projector_refactor_plan.md`. |
| **D3** | `GraphIngestor` SQL strategy | UPDATE selettivo (only mapped columns) + dry-run mode for preview. | Preserves the 40+ pyarchinit-specific columns the s3dgraphy mapping JSON does not cover (e.g. `descrizione`, `foto`, `profondita`). Dry-run is the obligatory CLI default. |
| **D4** | Round-trip semantics | Semantic invariant on mapped columns (B) + lossy-but-idempotent for external graphs (C). | Bit-identity (A) impossible due to PK auto-increment + timestamps. Pure unit tests (D) miss regressions. |
| **D5** | Missing epoch policy | Strict by default (`create_missing_epochs=False` raises `MissingEpochError`); opt-in to auto-create. | Prevents external graphs from polluting `periodizzazione_table` with spurious periods on Volterra-grade datasets. |
| **D6** | Multi-site | One graph per `sito`; `sito` parameter is mandatory on both `populate_graph` and `populate_list`. | Aligns with AI03 `site_filter`, with parent spec §6 `SyncEngine.push(graph_id)` (graph_id == sito), and with the EM Datacenter "one graph per excavation" assumption. |
| **D7** | UI surfaces | A + B + D: Python API + Import tab in existing `S3DGraphyExportDialog` + CLI helper. No new QGIS menu, no new dialog file. | Maximal reuse of AI03 dialog. CLI enables CI / scripting. Dedicated import dialog (separate file) deferred to AI06+ when conflict UX matures. |
| **D8** | Failure mode | Atomic only (single `BEGIN/COMMIT/ROLLBACK`). Configurable `failure_mode={atomic, best_effort, by_group}` deferred to AI06+. | Atomic plays well with dry-run, avoids mixed states, matches user mental model. Follow-up note saved in `project_ai04_failure_mode_followup.md`. |
| **D9** | Test fixtures | Reuse `mini_volterra.sqlite` from AI03; add new pre-cooked `.graphml` input fixtures for ingest tests. | Single source-of-truth for canonical AI test data; binary fixtures committed to avoid build-flaky regen. |
| **D10** | Release tag | `5.3.0-alpha` minor bump, tag `phase2-ai04-bridge-bidirectional-5.3.0-alpha`. | Matches roadmap pattern: Phase 1 → 5.1, AI03 → 5.2, AI04 → 5.3, AI05 → 5.4. |

---

## 3. Components

### 3.1 `GraphProjector` (new, thin wrapper)

```python
# modules/s3dgraphy/sync/graph_projector.py
class GraphProjector:
    """Project PyArchInit DB rows into a stratigraphic-layer
    s3dgraphy Graph.

    AI04 implementation is a thin wrapper around the existing
    _enrich_pyarchinit_graph() from graphml_writer.py; the real
    promotion to a self-contained class lives in AI05.
    """
    def __init__(self, vocab_provider: VocabProvider | None = None) -> None: ...

    def populate_graph(self, db_path: Path, sito: str) -> "s3dgraphy.Graph":
        """Read sito-filtered rows from us_table + periodizzazione_table.
        Return populated in-memory Graph. Idempotent: project twice
        → identical graph (modulo node ordering)."""
```

**Responsibilities:**
- Open SQLite connection (read-only path acceptable).
- Verify Phase 1 migration applied: `us_table.node_uuid` column exists. Raise `SchemaMismatchError` otherwise.
- Build empty `s3dgraphy.Graph()`.
- Delegate to `_enrich_pyarchinit_graph(graph, db_path, sito_filter=sito)` (the existing function gets a new `sito_filter` keyword argument; default `None` preserves AI03 behaviour).
- Filter the resulting graph: keep only nodes whose `attributes['sito'] == sito` (the AI03 path applies the filter post-process at lines 295-323 of `graphml_writer.py`; the projector does the same so it is independent of caller-side filtering).
- Return the populated graph.

**File size estimate:** ~80 lines including docstrings and error handling.

### 3.2 `GraphIngestor` (new, full implementation)

```python
# modules/s3dgraphy/sync/graph_ingestor.py
class GraphIngestor:
    """Write a s3dgraphy Graph back to the PyArchInit SQL tables.
    Atomic transaction (BEGIN/COMMIT/ROLLBACK).
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
    ) -> "IngestResult":
        """Persist graph nodes to us_table + (optionally) periodizzazione_table.

        Args:
            graph: in-memory Graph as produced by GraphProjector or a
                GraphML/external loader.
            db_path: SQLite database path.
            sito: site identifier; all graph nodes must have
                attributes['sito'] == sito or SiteMismatchError raises.
            dry_run: when True, runs the full validation/conflict
                detection flow but ROLLBACKs at the end. No write.
            create_missing_epochs: when True, EpochNodes referencing
                (periodo, fase) not present in periodizzazione_table
                are auto-inserted; when False (default), raise
                MissingEpochError.

        Returns:
            IngestResult with counts + conflicts + errors.

        Raises:
            SchemaMismatchError: us_table.node_uuid column missing.
            UnknownUnitaTipoError: graph node has unrecognised
                unita_tipo (e.g. legacy USVA after migration).
            SiteMismatchError: graph node attributes['sito'] != sito.
            MissingEpochError: epoch missing in DB and
                create_missing_epochs=False.
            GraphIngestError: any other ingestion failure (FK
                violation, sqlite IntegrityError, ...). Always means
                DB rolled back to pre-call state.
        """
```

**Responsibilities:**
- Validate inputs: `node_uuid` column present, all graph nodes match `sito`.
- Open transaction.
- For each node:
  - Lookup `us_table` row by `node_uuid = node.EMid`.
  - Compute the `MAPPED_COLUMNS` subset from the node attributes.
  - If row found: compute UPDATE statement only for changed mapped columns; record any value diff as `ConflictRecord(resolution="graph_wins")`.
  - If row not found: INSERT new row with mapped columns + node_uuid + sito.
- For each `EpochNode`:
  - Lookup `periodizzazione_table` row by `(periodo, fase)`.
  - If found: noop.
  - If missing and `create_missing_epochs=True`: INSERT.
  - If missing and `create_missing_epochs=False`: collect into a single `MissingEpochError` raised after the per-node loop.
- COMMIT (or ROLLBACK if any step raised, or unconditionally if `dry_run=True`).
- Return `IngestResult` populated with counters and conflict list.

**File size estimate:** ~250 lines.

### 3.3 `ConflictResolver` (new, stub)

```python
# modules/s3dgraphy/sync/conflict_resolver.py
class ConflictResolver:
    """Stub for AI04. Always resolves to 'graph_wins' (last writer
    wins, matching parent spec §6.4 default). The real pluggable
    implementation lands in AI06+."""
    def resolve(
        self,
        db_row: dict,
        graph_node: "s3dgraphy.Node",
        field: str,
    ) -> "ConflictResolution":
        return ConflictResolution.GRAPH_WINS
```

**Responsibilities (AI04):**
- Always return `ConflictResolution.GRAPH_WINS`.
- The interface is in place so AI06 can subclass (`InteractiveConflictResolver`, `TimestampBasedResolver`) without changing `GraphIngestor` signature.

**File size estimate:** ~30 lines.

### 3.4 `IngestResult` + `ConflictRecord` (new dataclasses)

```python
# modules/s3dgraphy/sync/ingest_result.py
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class ConflictRecord:
    node_uuid: str
    field: str
    db_value: Any
    graph_value: Any
    resolution: str   # "graph_wins" in AI04; "db_wins"/"skipped" later

@dataclass(frozen=True)
class IngestResult:
    applied: int                 # rows successfully inserted+updated
    inserted: int                # rows newly created
    updated: int                 # rows updated in place
    skipped: int                 # rows unchanged
    epochs_created: int          # auto-created periodizzazione rows
    conflicts: tuple[ConflictRecord, ...] = ()
    errors: tuple[str, ...] = ()
    dry_run: bool = False
```

### 3.5 CLI helper

```python
# scripts/s3dgraphy_sync.py
def main(argv: list[str]) -> int:
    """Standalone CLI: python scripts/s3dgraphy_sync.py [export|import] ..."""
```

**Subcommands:**
- `export`: thin wrapper around `export_graphml()` from AI03 (for parity / scriptability).
- `import`: invokes `GraphIngestor.populate_list()`. Default mode is dry-run; `--apply` is required for writes.

**CLI surface:**
```
python scripts/s3dgraphy_sync.py export \
    --db DB --graphml OUT --sito NAME

python scripts/s3dgraphy_sync.py import \
    --db DB --graphml IN --sito NAME
    [--apply]                  # default: dry-run, no writes
    [--create-epochs]          # auto-create missing periodizzazione
    [--mapping NAME]           # default: pyarchinit_us_mapping
```

**File size estimate:** ~150 lines including argparse setup and exit codes.

### 3.6 UI integration — Import tab in `S3DGraphyExportDialog`

The AI03 dialog (`gui/dialog_s3dgraphy_export.py` or wherever it lives) gets a `QTabWidget` with two tabs:
- **Tab "Export"** — existing AI03 workflow, **untouched**.
- **Tab "Import"** — new:
  - QLineEdit + QPushButton "Browse…" for `.graphml` file
  - QComboBox for sito selection (populated from `us_table` distinct sites)
  - QCheckBox "Crea periodi mancanti" (`create_missing_epochs`)
  - QPushButton "Anteprima" → runs `populate_list(dry_run=True)` and displays a `QTableWidget` with `IngestResult.conflicts[]` + counters
  - QPushButton "Applica" — disabled until the user has clicked "Anteprima" at least once; on click runs `populate_list(dry_run=False)` and shows `QMessageBox.information` with the result counts.
  - On exception: `QMessageBox.critical` with class name + suggestion (e.g. "Run scripts/migrations/2026_05_node_uuid_backfill.py").

**Constraint:** zero modifications to the existing "Export" tab logic. The AI03 acceptance test (AC-2) verifies byte-identical GraphML output before and after AI04 lands.

---

## 4. Data flow

### 4.1 Projection (DB → Graph)

```
populate_graph(db_path, sito="Scavo archeologico")
  1. open(db_path); verify us_table.node_uuid exists
  2. graph = s3dgraphy.Graph()
  3. _enrich_pyarchinit_graph(graph, db_path, sito_filter=sito)
        ├─ reads us_table WHERE sito=?
        ├─ reads periodizzazione_table (all rows — global epoch context)
        ├─ creates StratigraphicUnit/USM/USVs/.../Combinar nodes
        ├─ creates EpochNode per (periodo, fase)
        └─ creates is_after / has_first_epoch / has_property edges
  4. filter graph: keep only nodes with attributes['sito'] == sito
  5. return graph
```

### 4.2 Ingestion — dry-run

```
populate_list(graph, db_path, sito="X", dry_run=True)
  1. validate: us_table.node_uuid present; every graph node has sito="X"
  2. BEGIN
  3. for node in graph.nodes:
       db_row = SELECT * FROM us_table WHERE node_uuid=?
       if db_row is None:
         record_insert(node)
       else:
         for col in MAPPED_COLUMNS:
           if db_row[col] != node.attribute(col):
             record_conflict(node, col, db_row[col], node.attribute(col))
         record_update(node)
  4. for epoch in graph.epoch_nodes:
       row = SELECT * FROM periodizzazione_table WHERE periodo=? AND fase=?
       if row is None and not create_missing_epochs:
         collect MissingEpochError
       elif row is None:
         record_epoch_insert(epoch)
  5. ROLLBACK              # dry-run never writes
  6. if MissingEpochError collected: raise
  7. return IngestResult(applied=0, dry_run=True, conflicts=..., ...)
```

### 4.3 Ingestion — write mode

```
populate_list(graph, db_path, sito="X", dry_run=False)
  1-4. identical to dry-run
  5. for each recorded operation:
       INSERT or UPDATE us_table
       INSERT periodizzazione_table (if create_missing_epochs)
  6. COMMIT     (or ROLLBACK on any exception)
  7. return IngestResult(applied=N, dry_run=False, ...)
```

### 4.4 Round-trip invariant (D4-B)

```
db_before = read_us_table_canonical(mini_volterra)
graph     = projector.populate_graph(mini_volterra, sito="X")
db_copy   = shutil.copy2(mini_volterra, tmp_path / "rt.sqlite")
ingestor.populate_list(graph, db_copy, sito="X")
db_after  = read_us_table_canonical(db_copy)

# Assert: for every column in MAPPED_COLUMNS,
#   {row[col] for row in db_before} == {row[col] for row in db_after}
# Non-mapped columns may differ (they should be unchanged after UPDATE selettivo).
```

### 4.5 External-graph idempotent invariant (D4-C)

```
external_graph = load_pre_cooked_graphml("mini_volterra_external.graphml")
db = fresh_copy(mini_volterra)

r1 = ingestor.populate_list(external_graph, db, sito="X")
r2 = ingestor.populate_list(external_graph, db, sito="X")
r3 = ingestor.populate_list(external_graph, db, sito="X")

assert r2.inserted == 0 and r2.updated == 0
assert r2.skipped == r2.applied
assert r3.applied == r2.applied   # converged after one iteration
```

### 4.6 CLI flow

```
python scripts/s3dgraphy_sync.py import --db DB --graphml IN --sito X
   → defaults to dry-run; prints summary + conflict list
   → exit 0

python scripts/s3dgraphy_sync.py import --db DB --graphml IN --sito X --apply
   → writes to DB; prints summary
   → exit 0 on success; exit 1 + stderr on GraphSyncError
```

---

## 5. Error handling

### 5.1 Exception hierarchy

```
GraphSyncError                       (base)
├── ProjectionError                  (read-side: GraphProjector)
└── GraphIngestError                 (write-side: GraphIngestor)
    ├── SchemaMismatchError          (us_table.node_uuid missing)
    ├── UnknownUnitaTipoError        (vocab not aligned)
    ├── SiteMismatchError            (graph node has wrong sito)
    └── MissingEpochError            (epoch missing + strict mode)
```

All exceptions live in `modules/s3dgraphy/sync/graph_ingestor.py`; `ProjectionError` lives next to `GraphProjector`.

### 5.2 Fatal vs non-fatal

| Condition | Outcome |
|---|---|
| node_uuid column missing | fatal — `SchemaMismatchError`, ROLLBACK |
| Graph node with unknown `unita_tipo` | fatal — `UnknownUnitaTipoError` |
| `MissingEpochError` & strict | fatal — collected and raised after per-node loop |
| `MissingEpochError` & opt-in | non-fatal — INSERT, counted in `epochs_created` |
| Graph node sito ≠ parameter | fatal — `SiteMismatchError` |
| node_uuid not in DB | non-fatal — INSERT, counted in `inserted` |
| node_uuid in DB, values differ | non-fatal — UPDATE, ConflictRecord recorded, counted in `updated` |
| node_uuid in DB, values equal | non-fatal — no-op, counted in `skipped` |
| FK violation / IntegrityError | fatal — ROLLBACK + raise `GraphIngestError(cause=...)` |

### 5.3 Logging

- Logger: `logging.getLogger("modules.s3dgraphy.sync.graph_ingestor")`.
- Default WARNING; DEBUG mode emits per-node decisions.
- Toggled via QGIS Settings → PyArchInit → Debug.

### 5.4 UI error surfacing

- Import tab catches `GraphSyncError`, shows `QMessageBox.critical` with class name + remediation hint pulled from a static `_HINTS` dict (e.g. `SchemaMismatchError → "Run scripts/migrations/2026_05_node_uuid_backfill.py"`).
- CLI prints to stderr and exits 1.

---

## 6. Testing strategy

### 6.1 Test taxonomy

| Level | Focus | Files |
|---|---|---|
| L0 unit | Dataclass invariants, exception hierarchy | `test_graph_projector.py`, `test_graph_ingestor.py`, `test_conflict_resolver.py`, `test_ingest_result.py` |
| L1 fixture-based pipeline | End-to-end with `mini_volterra.sqlite` | `test_round_trip.py`, `test_idempotent_ingest.py` |
| L2 CLI subprocess | `scripts/s3dgraphy_sync.py` | `test_cli_helper.py` |

### 6.2 Decision-pinning tests

Each design decision D1–D10 has at least one test that fails if the decision is silently reverted.

| Decision | Test |
|---|---|
| D2 (wrap pattern) | `test_graph_projector_wraps_enrich_function` |
| D3 (UPDATE selettivo) | `test_populate_list_update_selettivo_preserves_unmapped_columns` |
| D3 (dry-run) | `test_populate_list_dry_run_no_writes` |
| D4-B (semantic round-trip) | `test_round_trip_preserves_mapped_fields` |
| D4-C (idempotent ingest) | `test_external_graph_ingest_idempotent` |
| D5-A (strict default) | `test_missing_epoch_strict_raises` |
| D5-B (opt-in) | `test_missing_epoch_create_inserts_period` |
| D6 (mandatory sito) | `test_site_mismatch_raises` |
| D8 (atomic) | `test_populate_list_atomic_on_failure` |
| (regression guard) | `test_ai03_export_byte_identical` |

### 6.3 Fixture additions

```
tests/sync/fixtures/
├── mini_volterra.sqlite                        (AI03, reused)
├── mini_volterra_baseline_ai03.graphml         (NEW — AI03 byte-identical baseline)
├── mini_volterra_external.graphml              (NEW — pre-cooked input for ingest tests)
└── mini_volterra_external_with_new_epoch.graphml  (NEW — for D5-B test)

tests/sync/fixtures/build_mini_volterra_external.py    (NEW — generator script)
```

The `.graphml` fixtures are committed as binaries (lxml-canonicalised) so test runs do not depend on the generator.

### 6.4 Test count target

- Baseline (post-AI03): 59 passing.
- AI04 adds ~16 new tests → target ≥ 75 passing.
- All pass in <2 s on a dev laptop without QGIS.
- Zero new third-party dependencies (lxml, pandas, sqlite3, pytest already in `pyproject.toml`).

### 6.5 Non-regression guard

The single most important test is `test_ai03_export_byte_identical`:

```python
def test_ai03_export_byte_identical(mini_volterra, tmp_path):
    """AI03 export pipeline must produce byte-identical GraphML
    after AI04 landing. Strategy D wrap pattern guarantees this."""
    out = tmp_path / "out.graphml"
    export_graphml(db_path=mini_volterra,
                   mapping="pyarchinit_us_mapping",
                   output_path=out)
    baseline = (FIXTURES / "mini_volterra_baseline_ai03.graphml").read_text()
    assert _normalize(out.read_text()) == _normalize(baseline)
```

If this test ever goes red, AI04 has regressed AI03 — block on it.

---

## 7. Acceptance criteria

| # | Criterion |
|---|---|
| AC-1 | `GraphProjector.populate_graph(db, sito="X")` returns a non-empty Graph; every node has `attributes['sito'] == "X"`. |
| AC-2 | AI03 export pipeline produces byte-identical GraphML on `mini_volterra.sqlite` vs the pre-AI04 baseline (regression guard). |
| AC-3 | `populate_list()` is atomic — any mid-transaction failure leaves the DB in pre-call state (verified by sha256-before/after). |
| AC-4 | `populate_list(dry_run=True)` does not write — sha256 of DB unchanged. |
| AC-5 | UPDATE selettivo preserves columns not in the mapping JSON (e.g. `descrizione`, `foto`, `profondita`). |
| AC-6 | Round-trip (DB → Graph → DB') preserves all mapped columns. |
| AC-7 | External-graph ingest converges after one iteration (3 consecutive runs → applied count stable). |
| AC-8 | Strict missing-epoch raises `MissingEpochError`. |
| AC-9 | Opt-in missing-epoch creates the row in `periodizzazione_table`. |
| AC-10 | CLI `import` requires `--apply` to write (default is dry-run). |
| AC-11 | Import tab in `S3DGraphyExportDialog` does not break the Export tab. |
| AC-12 | `pytest tests/sync/ tests/migrations/` ≥ 75 passing tests. |
| AC-13 | Plugin loads in QGIS at every commit (manual smoke after each Group). |
| AC-14 | `test_us_vocabulary_alignment.py` stays green. |
| AC-15 | `test_node_uuid_backfill.py` stays green. |

---

## 8. Release plan

```
Group 0 — Pre-flight
  ├─ Tag pre-ai04-bridge (rollback safety)
  ├─ Capture baseline AI03 GraphML output → fixtures/mini_volterra_baseline_ai03.graphml
  └─ Bump metadata.txt: 5.2.0-alpha → 5.3.0-alpha

Group A — IngestResult + ConflictRecord + ConflictResolver stub
  └─ TDD pure dataclass tests, no DB touching

Group B — GraphProjector wrapper
  └─ ~80 line file + 3 line shim test (verifies it delegates to enrich)

Group C — GraphIngestor populate_list dry-run mode
  └─ TDD: full validation/conflict-detection pipeline, no writes

Group D — GraphIngestor populate_list write mode
  └─ TDD: atomic transaction, INSERT/UPDATE selettivo, MissingEpochError

Group E — Round-trip + idempotent invariants
  └─ Two L1 tests pinning D4-B and D4-C

Group F — CLI helper s3dgraphy_sync.py
  └─ argparse + L2 subprocess tests (dry-run default + --apply)

Group G — UI Import tab in S3DGraphyExportDialog
  └─ QTabWidget refactor + Anteprima/Applica buttons; zero diff on Export tab

Group H — Release packaging
  ├─ H.1: dev-log entry "Phase 2 / AI04: Bridge bidirectional"
  │       in docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md
  ├─ H.2: CHANGELOG bilingual entry (IT + EN) in dev_logs/CHANGELOG.md
  ├─ H.3: Update tutorials in 9 languages if Import tab is user-facing
  ├─ H.4: Manual smoke gate in QGIS — block on this
  └─ H.5: tag phase2-ai04-bridge-bidirectional-5.3.0-alpha + push branch + tags
```

Estimated scope: ~16 commits, 3-5 days of work in subagent-driven flow.

---

## 9. Out of scope (deferred)

| Feature | Released in |
|---|---|
| `paradata.graphml` per project | AI05 |
| CRUD UI for `AuthorNode`/`LicenseNode`/`EmbargoNode`/`DocumentNode` | AI05 |
| Pluggable `ConflictResolver` strategies + UI dialog | AI06 |
| Configurable `failure_mode={atomic, best_effort, by_group}` | AI06+ |
| Promotion of `GraphProjector` from wrap (D) to proper class (A) | AI05 |
| Multi-graph context (`list[Graph]`) | AI06+ |
| `SyncEngine` + `DatacenterClient` + REST API | Phase 3 |
| `GraphDBBackend` + SPARQL | Phase 4 |

---

## 10. Risk assessment

| Risk | Mitigation |
|---|---|
| Wrap pattern (D2) cementa il debito | Memory note `project_ai04_projector_refactor_plan.md`; explicit promotion task in AI05 plan. |
| AI03 regression after touching `_enrich_pyarchinit_graph` (added `sito_filter` kwarg) | AC-2 byte-identical baseline test; new kwarg defaults to None (preserves AI03 call site). |
| Conflict detection generates false positives on JSON-serialised `rapporti` columns (whitespace differences) | Custom equality check on JSON columns: parse-then-compare. Test with non-trivial rapporti. |
| EpochNode lookup case-sensitivity on fase string ("3" vs "3.0") | Normalize fase to canonical str form in both projector and ingestor; explicit test on the user's Volterra dataset patterns (fase "2.1", "3", "3.1", etc.). |
| Mapping JSON in `pyarchinit_us_mapping.json` covers fewer columns than expected (only 5 actually emitted) → UPDATE selettivo is too narrow | Verified during AI03: mapping covers `us`, `sito`, `area`, `unita_tipo`, `periodo_iniziale`, `fase_iniziale`, `rapporti`, `d_stratigrafica`, `d_interpretativa`, `attivita`, `struttura`, `node_uuid`. AI04 reuses this list (constant `MAPPED_COLUMNS`). |
| User imports a graph generated by an external tool (Heriverse, EM Datacenter) with `unita_tipo` outside the pyarchinit vocabulary | `UnknownUnitaTipoError` raised with hint "Run vocab alignment migration"; covered by AC + dedicated test. |

---

## 11. References

- T5.4 meeting minutes 2026-05-04: `~/Downloads/SC1_StratiGraph_T5.4_MeetingNotes_20260504.pdf` (action item AI04 = "bridge prototype").
- T5.4 Reference Document v0.1 (Demetrescu, 2026-05-06): `~/Downloads/T5.4_PyArchInit_s3Dgraphy_Reference_v0.1.pdf` §6.
- Parent spec: `docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md` §3.2, §3.6, §3.7, §11.
- AI03 spec: `docs/superpowers/specs/2026-05-07-ai03-graphml-delegation-design.md`.
- AI03 dev-log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` (Phase 2 / AI03 section).
- s3dgraphy 0.1.40 source: <https://github.com/zalmoxes-laran/s3dgraphy>.
- Memory notes:
  - `project_ai04_projector_refactor_plan.md` — promotion path D → A in AI05+.
  - `project_ai04_failure_mode_followup.md` — atomic-only now, configurable later.
- Brainstorming session: this file's siblings (questions Q1–Q10 transcribed in §2).
