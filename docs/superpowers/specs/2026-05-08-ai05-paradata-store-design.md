# AI05 — `ParadataStore` + UI authoring + Strategy A promotion + edge styling (design spec)

**Date:** 2026-05-08 · **Author:** Enzo Cocca · **Status:** Approved
(brainstorming chiuso; implementation plan to be drafted via
`superpowers:writing-plans`).

**Parent spec:** `docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md`
(see §3.3 ParadataStore, §11 Implementation phasing).

**Predecessors:**
- AI03: `phase2-ai03-graphml-delegation-5.2.0-alpha` (GraphML delegation)
- AI04: `phase2-ai04-bridge-bidirectional-5.3.0-alpha` (Bridge bidirezionale)
- Both shipped successfully; no carryover regressions.

**Target tag:** `phase2-ai05-paradata-store-5.4.0-alpha`.

---

## 1. Overview

AI05 closes Phase 2 of the bridge by delivering the **ParadataStore**
(authorship/licensing/embargo metadata that has no SQL counterpart in
pyarchinit), promoting `GraphProjector` from a thin wrapper to a
proper class (Strategy A from AI04), and applying the same
`NodeRegistry`-style automation to edge styling that AI04.1 introduced
for nodes.

Scope is intentionally **focused on Phase 2 closure**: only the three
node types without SQL counterpart (`AuthorNode`, `LicenseNode`,
`EmbargoNode`) live in `paradata.graphml`. DOC, EpochNode, USVs/USVn
remain SQL-canonical (AI04 added their counterparts to `us_table` and
`periodizzazione_table`). Per-node paradata edges (e.g. Author →
has_authored → specific US) are deferred to AI06+.

Non-goals: per-node paradata granularity, ORCID/SPDX validation, file
locking for concurrent writes, full SyncEngine/DatacenterClient
networking (Phase 3+).

---

## 2. Decisions captured during brainstorming (2026-05-08)

| ID | Topic | Decision | Rationale |
|---|---|---|---|
| **D1** | Scope | Full ParadataStore + UI authoring + Strategy A promotion + edge styling automation. | The user wants Phase 2 closure end-to-end, not piecemeal. |
| **D2** | File location | `{db_path.parent}/paradata_{sito_slug}.graphml`, one file per `sito`. | API always has `db_path`; aligns with AI04 D6 single-graph-per-site; versionable in Git next to the DB. |
| **D3** | `populate_graph` integration | `populate_graph(db, sito, *, include_paradata=True)` defaults to merge. Opt-out via `include_paradata=False`. | Most-common-case-default; AC-2 baseline unaffected since `mini_volterra.sqlite` has no paradata file. |
| **D4** | Node types managed by ParadataStore | `AuthorNode`, `LicenseNode`, `EmbargoNode` only. | DOC/Epoch/USVs/USVn already have SQL counterparts via AI04; duplicating them in paradata creates sync conflicts. |
| **D5** | API surface | Both low-level (`read`/`write`/`add_node`/`remove_node`/`find`) and high-level (`add_author`/`add_license`/`add_embargo`/`list_*`/`remove`). | Low-level for power users / tests; high-level for UI dialog handlers and CLI ergonomics. |
| **D6** | UI | Single `ParadataManagerDialog` with three `QTabWidget` tabs (Authors/Licenses/Embargoes). Triggered by a "Manage paradata" button in the US scheda. | Discoverable, low cognitive load, minimal risk to AI03/AI04 dialog. |
| **D7** | Strategy A promotion | Full move: relocate `_enrich_pyarchinit_graph` body into `GraphProjector` private methods; delete the standalone function; update `export_graphml` call site. | Pays the AI04 carry-over debt. Single source of truth. AC-2 baseline guards regression. |
| **D8** | Edge styling | `EdgeRegistry` helper analogous to AI04's `NodeRegistry` fallback chain — read `s3Dgraphy_connections_datamodel.json` + `em_visual_rules.json` + `em_palette_template.graphml` for canonical style; `_PYARCHINIT_EDGE_OVERRIDES` wins for pyarchinit-specific cases. | Symmetry with the AI04.1 node refactor; future-proof for new edge types s3dgraphy adds. |
| **D9** | Author/License/Embargo scope | Site-level (singleton). No edges to specific nodes. | "Marco Pacifico is the author of Volterra" / "CC-BY-NC 4.0 covers the dataset" / "Embargo until 2030" — these are site-level concerns. Per-node granularity is AI06+ if a real use case emerges. |
| **D10** | Release tag | `5.4.0-alpha`, tag `phase2-ai05-paradata-store-5.4.0-alpha`. | Roadmap pattern: Phase 1 → 5.1, AI03 → 5.2, AI04 → 5.3, AI05 → 5.4. |

---

## 3. Components

### 3.1 `ParadataStore` (new)

```python
# modules/s3dgraphy/sync/paradata_store.py
class ParadataStore:
    """Site-scoped CRUD for paradata.graphml (atomic-safe writes).

    File path: {db_path.parent}/paradata_{sito_slug}.graphml
    where sito_slug = re.sub(r'\\W+', '_', sito).lower()
    """
    def __init__(self, db_path: Path, sito: str) -> None: ...

    @property
    def file_path(self) -> Path: ...
    def exists(self) -> bool: ...

    # ---- Low-level (D5) ----
    def read(self) -> "s3dgraphy.Graph":
        """Parse the file, hydrate AI04 data keys, filter to
        {AuthorNode, LicenseNode, EmbargoNode}. Returns empty
        Graph(graph_id=sito) if file doesn't exist."""

    def write(self, graph: "s3dgraphy.Graph") -> None:
        """Atomic write: serialise to .tmp, embed AI04 data keys,
        os.replace() to final path. Raises ParadataWriteError on
        any failure with the original file untouched."""

    def add_node(self, node) -> None: ...
    def remove_node(self, node_uuid: str) -> None: ...
    def find(self, node_type: str, **kwargs) -> list: ...

    # ---- High-level (D5) ----
    def add_author(self, name: str, orcid: str = None,
                   role: str = None) -> str:
        """Returns the new node's uuid7."""
    def list_authors(self) -> list[dict]: ...
    def add_license(self, spdx_id: str, url: str = None) -> str: ...
    def list_licenses(self) -> list[dict]: ...
    def add_embargo(self, until_date: str, reason: str = None) -> str: ...
    def list_embargos(self) -> list[dict]: ...
    def remove(self, node_uuid: str) -> None: ...   # alias for remove_node
```

**Responsibilities:**
- Atomic file persistence (write to `.tmp` then `os.replace`).
- Defensive read filter (drop non-paradata node types).
- High-level CRUD wraps `s3dgraphy.AuthorNode`/`LicenseNode`/`EmbargoNode` constructors and persists immediately.
- `node.attributes['sito']` set on every paradata node so multi-sito DBs stay scoped.

**File size estimate:** ~250 lines.

### 3.2 `EdgeRegistry` (new)

```python
# modules/s3dgraphy/sync/edge_registry.py

def resolve_edge_style(edge_type: str) -> dict | None:
    """Return {color, width, type, arrowhead} or None if not found.

    Lookup chain (override-wins, like NodeRegistry):
        1. _PYARCHINIT_EDGE_OVERRIDES (pyarchinit-specific)
        2. em_visual_rules.json edge section (if present)
        3. s3Dgraphy_connections_datamodel.json + heuristic
           (TOPOLOGICAL → solid, PARADATA → dashed)
    """

def is_paradata_edge(edge_type: str) -> bool:
    """True iff edge_type's category in connections datamodel is
    'PARADATA'. Falls back to a hardcoded set on missing JSON."""
```

**Responsibilities:**
- Lazy singleton `_edge_registry` (mirrors NodeRegistry pattern).
- Graceful degradation if JSONs missing → return `None` / hardcoded set.
- Replaces hardcoded `_PARADATA_UNITA_TIPI` classification in `graphml_writer.py`.

**File size estimate:** ~120 lines.

### 3.3 `GraphProjector` (Strategy A promotion)

```python
# modules/s3dgraphy/sync/graph_projector.py
class GraphProjector:
    def __init__(self, vocab_provider=None) -> None: ...

    def populate_graph(
        self,
        db_path: Path,
        sito: str,
        *,
        include_paradata: bool = True,   # NEW (D3)
    ) -> "s3dgraphy.Graph":
        """Phase 2 / Strategy A — full-class implementation.

        1. _verify_schema(db_path)
        2. graph = self._build_strat_layer(db_path, sito)
        3. if include_paradata: self._merge_paradata(graph, db_path, sito)
        4. return graph
        """

    # --- private (Strategy A — moved from _enrich_pyarchinit_graph) ---
    def _verify_schema(self, db_path) -> None: ...
    def _build_strat_layer(self, db_path, sito): ...
    def _load_strat_units(self, conn, sito) -> list: ...
    def _load_epochs(self, conn) -> dict: ...
    def _parse_rapporti(self, raw_rapporti, src_node, sito) -> list[edges]: ...
    def _propagate_attrs(self, node, db_row) -> None: ...
    def _merge_paradata(self, graph, db_path, sito) -> None: ...
```

**Migration:** the existing `_enrich_pyarchinit_graph()` standalone function in `modules/s3dgraphy/sync/graphml_writer.py` is **deleted** in this release. The single existing caller (`export_graphml()`) is updated to instantiate `GraphProjector` and call `populate_graph(include_paradata=False)` (preserving AI03 behaviour).

**File size estimate:** ~350 lines (was ~80).

### 3.4 `ParadataManagerDialog` (new UI)

```python
# gui/dialog_paradata_manager.py
class ParadataManagerDialog(QDialog):
    """Single-dialog 3-tab CRUD for site-level paradata.

    Tabs: Authors / Licenses / Embargoes
    Each tab: QTableView + Add/Edit/Remove buttons.
    """
    def __init__(self, parent, db_manager, sito: str): ...
    def setup_ui(self): ...
    def _load_data(self): ...
    def _on_add_author(self): ...
    def _on_add_license(self): ...
    def _on_add_embargo(self): ...
    def _on_remove_selected(self): ...
```

**Trigger:** new "Manage paradata" button in the US scheda
(`tabs/US_USM.py`), positioned next to the existing green "Extended
Matrix" button.

**File size estimate:** ~400 lines.

### 3.5 CLI extensions

```bash
# New paradata subcommands in scripts/s3dgraphy_sync.py
python scripts/s3dgraphy_sync.py paradata add-author \
    --db DB --sito SITE --name "Marco" [--orcid ORCID] [--role ROLE]
python scripts/s3dgraphy_sync.py paradata list-authors --db DB --sito SITE
python scripts/s3dgraphy_sync.py paradata add-license \
    --db DB --sito SITE --spdx ID [--url URL]
python scripts/s3dgraphy_sync.py paradata list-licenses --db DB --sito SITE
python scripts/s3dgraphy_sync.py paradata add-embargo \
    --db DB --sito SITE --until DATE [--reason REASON]
python scripts/s3dgraphy_sync.py paradata list-embargos --db DB --sito SITE
python scripts/s3dgraphy_sync.py paradata remove --db DB --sito SITE --uuid UUID
```

---

## 4. Data flow

### 4.1 `ParadataStore.read()` (atomic-safe parse)

```
1. file_path = {db_path.parent}/paradata_{sito_slug}.graphml
2. if not file_path.exists():
       return Graph(graph_id=sito)  # empty
3. graph = s3dgraphy.GraphMLImporter(filepath=file_path).parse()
4. _hydrate_pyarchinit_data_keys(graph, file_path)  # AI04 helper
5. graph.nodes = [n for n in graph.nodes
                  if type(n).__name__ in {AuthorNode, LicenseNode, EmbargoNode}]
6. return graph
```

### 4.2 `ParadataStore.write()` (atomic crash-safe)

```
1. tmp = file_path.with_suffix('.graphml.tmp')
2. try:
     s3dgraphy.GraphMLExporter(graph).export(str(tmp), persist_auxiliary=False)
     _embed_pyarchinit_data_keys(graph, tmp)   # AI04 helper
     os.replace(tmp, file_path)                # atomic rename
   except OSError as e:
     if tmp.exists(): tmp.unlink()
     raise ParadataWriteError(f'failed: {e}') from e
```

### 4.3 `populate_graph(include_paradata=True)`

```
graph = Graph(graph_id=sito)
self._verify_schema(db_path)
self._build_strat_layer(graph, db_path, sito)   # SQL → strat nodes + epochs

if include_paradata:
    store = ParadataStore(db_path, sito)
    if store.exists():
        try:
            paradata_graph = store.read()
            for n in paradata_graph.nodes:
                if not graph.find_node_by_id(n.node_id):
                    graph.add_node(n)
        except ParadataReadError as e:
            log.warning(f'Paradata file unreadable, falling back: {e}')

return graph
```

### 4.4 High-level CRUD example

```
store = ParadataStore(db, "Volterra")
auth_uuid = store.add_author("Marco", orcid="0000-...", role="curator")
   ├─ graph = self.read()
   ├─ node = AuthorNode(node_id=uuid7(), name="Marco",
   │                    attributes={"orcid": "...", "role": "...", "sito": sito})
   ├─ graph.add_node(node)
   ├─ self.write(graph)
   └─ return node.node_id
```

### 4.5 Round-trip with paradata

```
db_before = read_canonical(mini_volterra, sito)
paradata_before_uuids = {n.node_id for n in
                         ParadataStore(mini_volterra, sito).read().nodes}

graph = projector.populate_graph(mini_volterra, sito, include_paradata=True)
# Now graph has strat + paradata

db_copy = copy(mini_volterra)
ingestor.populate_list(graph, db_copy, sito, dry_run=False)   # writes strat
paradata_extract = filter_paradata(graph)
ParadataStore(db_copy, sito).write(paradata_extract)          # writes paradata

# Assertions
db_after = read_canonical(db_copy, sito)
assert mapped_columns_equal(db_before, db_after)              # AI04 D4-B
paradata_after_uuids = {...}
assert paradata_before_uuids == paradata_after_uuids
```

### 4.6 Edge styling lookup

```
edge_registry.resolve_edge_style("is_after"):
   1. _PYARCHINIT_EDGE_OVERRIDES.get("is_after") → None (not overridden)
   2. _get_edge_registry()._visual_rules.get("is_after") → matches
   3. return {color: "#000000", width: 1.0, type: "line", arrowhead: "normal"}

edge_registry.is_paradata_edge("has_property") → True
edge_registry.is_paradata_edge("is_after") → False
```

---

## 5. Error handling

### 5.1 Exception hierarchy (extension of AI04)

```
GraphSyncError                       (existing, base)
├── ProjectionError                  (existing)
├── GraphIngestError                 (existing)
└── ParadataStoreError               (NEW base)
    ├── ParadataReadError
    ├── ParadataWriteError
    ├── ParadataValidationError
    └── ParadataNotFoundError
```

All `ParadataStoreError` subclasses inherit `GraphSyncError` so existing `try/except GraphSyncError` blocks in the CLI/UI continue to catch them.

### 5.2 Fatal vs non-fatal categorisation

| Condition | Outcome |
|---|---|
| File doesn't exist on `read()` | non-fatal — return empty Graph |
| File parse error | fatal — `ParadataReadError` (caller can decide to fall back to strat-only) |
| File contains non-paradata node types | non-fatal — defensive filter, log warning |
| `add_author(name="")` | fatal — `ParadataValidationError("name required")` |
| `add_author(name="X", orcid="bogus")` | non-fatal — accepted, no validation |
| Disk full / write error | fatal — `ParadataWriteError`, original file untouched |
| Concurrent writers race | non-deterministic last-writer-wins — atomic-rename guarantees no corruption |
| `remove(uuid="not-found")` | non-fatal — no-op, log warning |
| `add_node(custom_class)` | fatal — `ParadataValidationError` if class outside `{AuthorNode, LicenseNode, EmbargoNode}` |
| `populate_graph(include_paradata=True)` & paradata file corrupt | non-fatal — strat layer returned, log warning |

### 5.3 UI error surfacing

```python
# ParadataManagerDialog handler example
try:
    self.store.add_author(name, orcid, role)
except ParadataValidationError as e:
    QMessageBox.warning(self, "Invalid input", str(e))
except ParadataWriteError as e:
    QMessageBox.critical(
        self, "Save failed",
        f"Cannot write paradata file: {e}\n\n"
        f"Check disk space and write permissions:\n{self.store.file_path}")
except GraphSyncError as e:
    QMessageBox.critical(self, type(e).__name__, str(e))
```

### 5.4 CLI error surfacing

```
exit 0 — success
exit 1 — GraphSyncError (any subclass, including ParadataStoreError)
exit 2 — argparse error
```

### 5.5 Logging

- Logger: `logging.getLogger("modules.s3dgraphy.sync.paradata_store")`
- Default WARNING; DEBUG via QGIS Settings → PyArchInit → Debug.
- Atomic-write outcomes logged at INFO.

---

## 6. Testing strategy

### 6.1 Test taxonomy (4 levels)

| Level | Focus | Files |
|---|---|---|
| L0 unit | Dataclass invariants, exception hierarchy, atomic-write semantics | `test_paradata_store.py`, `test_edge_registry.py` |
| L1 fixture-based pipeline | `populate_graph(include_paradata)` end-to-end | `test_graph_projector_paradata.py`, `test_round_trip_with_paradata.py` |
| L2 CLI subprocess | `python scripts/s3dgraphy_sync.py paradata ...` | `test_cli_paradata.py` |
| L3 regression guards | AC-2 baseline + Phase 1 + AI04 | existing tests must stay green |

### 6.2 Decision-pinning matrix

| D | Test |
|---|---|
| D2 | `test_paradata_store::test_file_path_resolves_per_sito` |
| D3 | `test_graph_projector_paradata::test_populate_graph_includes_paradata_by_default`, `test_opt_out_disables_merge` |
| D4 | `test_paradata_store::test_read_filters_to_paradata_only` |
| D5 | `test_paradata_store::test_low_level_add_node`, `test_high_level_add_author_round_trip` |
| D6 | `test_paradata_dialog_smoke::test_paradata_dialog_can_open` (skipif no Qt) |
| D7 | `test_strategy_a_no_regression::test_export_graphml_unchanged`, AC-2 baseline |
| D8 | `test_edge_registry::test_resolves_topological_to_solid`, `test_resolves_paradata_to_dashed`, `test_falls_back_when_datamodel_missing` |
| D9 | `test_paradata_store::test_add_author_creates_isolated_node_no_edges` |

### 6.3 Fixture additions

```
tests/sync/fixtures/
├── mini_volterra.sqlite                 (reuse from AI03)
├── mini_volterra_baseline_ai03.graphml  (reuse, regenerated post-Strategy A)
├── mini_volterra_external.graphml       (reuse from AI04)
├── paradata_volterra.graphml            (NEW — pre-cooked paradata fixture:
│                                          2 AuthorNodes,
│                                          1 LicenseNode,
│                                          1 EmbargoNode)
└── build_mini_volterra_external.py      (extended to also emit paradata fixture)
```

### 6.4 Atomic crash-safety test

```python
def test_atomic_write_no_corruption_on_crash(tmp_path, monkeypatch):
    db = tmp_path / "test.sqlite"
    create_minimal_sqlite(db, "X")
    store = ParadataStore(db, "X")
    store.add_author("Original")
    original_content = store.file_path.read_bytes()

    def boom(src, dst):
        raise OSError("simulated crash")
    monkeypatch.setattr("os.replace", boom)

    with pytest.raises(ParadataWriteError):
        store.add_author("New")

    # Original file untouched, tmp cleaned up
    assert store.file_path.read_bytes() == original_content
    assert not store.file_path.with_suffix(".graphml.tmp").exists()
```

### 6.5 AI03/AI04 non-regression guards (must stay green)

1. `test_ai03_export_byte_identical.py` — structural fingerprint
2. `test_round_trip.py` — AI04 D4-B
3. `test_idempotent_ingest.py` — AI04 D4-C
4. `test_cli_helper.py` — AI04 CLI
5. `test_us_vocabulary_alignment.py` — Phase 1
6. `test_node_uuid_backfill.py` — Phase 1

All must continue passing after Strategy A promotion (Group C).

### 6.6 Test count target

- Baseline (post-AI04+AI04.1): **94 passing**
- AI05 adds:
  - L0 ParadataStore: ~12
  - L0 EdgeRegistry: ~5
  - L1 projector w/ paradata: ~4
  - L1 round-trip with paradata: ~2
  - L2 CLI paradata: ~6
  - L3 strategy A regression: ~3
  - UI smoke (skip if no Qt): ~1
- **Target: ≥120 passing** in <3s, no QGIS required for L0/L1/L2/L3.

---

## 7. Acceptance criteria

| # | Criterion |
|---|---|
| AC-1 | `ParadataStore(db, sito).read()` returns Graph (empty if file absent). |
| AC-2 | AI03 byte-identical baseline stays green post-Strategy A. |
| AC-3 | `add_author/license/embargo` persists atomically (no corruption on crash). |
| AC-4 | `populate_graph(include_paradata=True)` merges by default. |
| AC-5 | `populate_graph(include_paradata=False)` returns pure-strat (AI04 backward-compat). |
| AC-6 | ParadataStore filters read to `{AuthorNode, LicenseNode, EmbargoNode}` only. |
| AC-7 | `remove(uuid)` is idempotent (no error on missing uuid). |
| AC-8 | Round-trip preserves all paradata node uuids on file. |
| AC-9 | `EdgeRegistry.resolve_edge_style("is_after")` returns sane defaults. |
| AC-10 | `is_paradata_edge` correctly classifies TOPOLOGICAL/PARADATA. |
| AC-11 | EdgeRegistry graceful degradation if datamodel JSON missing. |
| AC-12 | `_enrich_pyarchinit_graph` standalone function REMOVED post-Strategy A. |
| AC-13 | AI04 CLI / GraphIngestor still work post-Strategy A. |
| AC-14 | `ParadataManagerDialog` opens with 3 tabs without crash. |
| AC-15 | CLI `paradata add-author` / `list-authors` / `remove` work via subprocess. |
| AC-16 | `pytest tests/sync/ tests/migrations/ -q` ≥ 120 passing. |
| AC-17 | Plugin loads in QGIS at every commit. |
| AC-18 | Phase 1 vocab + node_uuid migration tests stay green. |

---

## 8. Release plan

```
Group 0 — Pre-flight (4 tasks)
  ├─ Push pending commits + create rollback tag pre-ai05-paradata
  ├─ Capture baseline state
  ├─ Bump metadata.txt: 5.3.0-alpha → 5.4.0-alpha
  └─ CHANGELOG header placeholder

Group A — Edge Registry (3 tasks)
  ├─ A.1: scaffold edge_registry.py + L0 tests
  ├─ A.2: integrate into graphml_writer post-processor
  └─ A.3: AC-2 baseline regression check

Group B — ParadataStore Foundation (4 tasks)
  ├─ B.1: scaffold paradata_store.py + atomic read/write
  ├─ B.2: low-level CRUD (add_node/remove_node/find)
  ├─ B.3: high-level helpers (add_author/license/embargo + list_*)
  └─ B.4: exception hierarchy + atomic crash-safety test

Group C — GraphProjector Strategy A promotion (4 tasks)
  ├─ C.1: extract _enrich_pyarchinit_graph body into private methods
  ├─ C.2: add include_paradata=True kwarg + ParadataStore merge
  ├─ C.3: delete standalone _enrich_pyarchinit_graph; update export_graphml
  └─ C.4: AC-2 baseline regen + full regression suite

Group D — Pre-cooked paradata fixture (1 task)
  └─ D.1: extend build_mini_volterra_external.py to emit paradata fixture

Group E — Round-trip + idempotent tests (2 tasks)
  ├─ E.1: test_round_trip_with_paradata.py
  └─ E.2: test_paradata_idempotent.py

Group F — CLI subcommands (2 tasks)
  ├─ F.1: extend scripts/s3dgraphy_sync.py with paradata subcommands
  └─ F.2: test_cli_paradata.py L2 subprocess tests

Group G — UI ParadataManagerDialog (2 tasks)
  ├─ G.1: gui/dialog_paradata_manager.py — 3-tab dialog
  └─ G.2: integrate "Manage paradata" button in scheda US

Group H — Release packaging (5 tasks)
  ├─ H.1: dev-log entry "Phase 2 / AI05: ParadataStore + UI authoring"
  ├─ H.2: CHANGELOG bilingual (IT + EN)
  ├─ H.3: verification (controller, no subagent)
  ├─ H.4: manual smoke gate (USER-driven)
  └─ H.5: tag phase2-ai05-paradata-store-5.4.0-alpha + push branch + tag
```

Estimated scope: ~24 commits, 8-10 days in subagent-driven flow.

---

## 9. Out of scope (deferred)

| Feature | Released in |
|---|---|
| Per-node paradata edges (Author → has_authored → US) | AI06+ |
| Pluggable `ConflictResolver` strategies | AI06+ |
| Configurable `failure_mode={atomic, best_effort, by_group}` | AI06+ |
| ORCID validation, SPDX whitelist, ISO date parsing | AI06+ |
| File locking for concurrent writes | AI06+ |
| `SyncEngine` + `DatacenterClient` + REST API | Phase 3 |
| `GraphDBBackend` + SPARQL | Phase 4 |
| `VirtualSpecialFindUnit` authoring layer | AI06+ |

---

## 10. Risk assessment

| Risk | Mitigation |
|---|---|
| Strategy A move breaks AI03 export | AC-2 byte-identical baseline + 3 dedicated regression tests. Stop and revert if RED. |
| AI04 callers (`s3dgraphy_dot_bridge`, dialog) use `_enrich_pyarchinit_graph` directly | Pre-Group C grep verifies zero direct calls; update all call sites in same commit. |
| Filename collision `paradata_{sito_slug}.graphml` | `\\W+→_` slug + `paradata_` prefix minimises collision. |
| Atomic write fail on non-POSIX (Windows) | `os.replace()` IS atomic on Windows ≥ Vista. Verify in manual smoke. |
| Edge registry JSON missing color/width | Graceful degradation → `None` → caller uses default. AC-11. |
| Two pyarchinit instances writing same file | Last-writer-wins via atomic-rename. Documented as "single-user assumption". AI06+ adds file lock. |
| Qt5/Qt6 incompatibility in dialog | Use `qgis.PyQt` abstraction (AI04 pattern). UI smoke test skip-on-missing-qt. |
| Dialog table model performance | Site-level scope → max ~10 entries per type per sito. Non-issue. |

---

## 11. References

- T5.4 meeting minutes 2026-05-04 (Demetrescu et al., parent spec).
- T5.4 Reference Document v0.1 (Demetrescu, 2026-05-06): §3.3 ParadataStore.
- Parent spec: `docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md` §3.3, §11.
- AI04 spec: `docs/superpowers/specs/2026-05-08-ai04-bridge-bidirectional-design.md`.
- AI04 dev-log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` (Phase 2 / AI04 section).
- AI04.1 fixup commits: `a6d1215a`, `aa5f24db`, `eeb747cf`.
- Memory notes:
  - `project_ai04_projector_refactor_plan.md` — Strategy A promotion path (this spec consummates).
  - `project_ai04_failure_mode_followup.md` — atomic-only ingest, configurable later.
- s3dgraphy 0.1.40 source: <https://github.com/zalmoxes-laran/s3dgraphy>.
- s3dgraphy GraphML export docs: <https://github.com/zalmoxes-laran/s3Dgraphy/blob/main/docs/GRAPHML_EXPORT.md>.
- s3dgraphy data formalization: <https://github.com/zalmoxes-laran/s3Dgraphy/blob/main/docs/DATA_FORMALIZATIONS.md>.
- Brainstorming session: questions Q1–Q10 transcribed in §2.
