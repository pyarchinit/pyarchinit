# PyArchInit ↔ s3dgraphy ↔ Datacenter — Bidirectional Knowledge Graph Sync

**Spec date:** 2026-05-04
**Last updated:** 2026-05-06 (aligned with Emanuel Demetrescu's T5.4 Reference Document v0.1, 2026-05-06)
**Author:** Enzo (with brainstorming session)
**Status:** Design proposal — direction confirmed in StratiGraph WP5/T5.4 meeting (2026-05-04) and consolidated in T5.4 Reference Document v0.1 (2026-05-06)
**Target plugin version:** 5.1.0-alpha
**Target s3dgraphy version:** 0.1.40 (currently bundled: 0.1.30, system pip: 0.1.15)
**Target Extended Matrix version:** **EM 1.5** (PyArchInit currently hard-codes EM 1.4 — see §2.1.A); EM 1.6 in pipeline (building archaeology + working-units-on-surfaces) — arrives as JSON entries, no code change needed

## 1. Overview

PyArchInit is currently a data-ingestion plugin for archaeological excavations.
s3dgraphy is a Python library for stratigraphic knowledge graphs (Extended
Matrix datamodel v1.5.3, CIDOC-CRM aligned). The Extended Matrix Datacenter is
a service "in costruzione" that will host published knowledge graphs.

This document specifies how PyArchInit becomes a **bridge** between its SQL
data stores (SQLite/Spatialite/PostgreSQL+PostGIS) and s3dgraphy graphs, and
how it **bidirectionally synchronizes** parts of those graphs with the EM
Datacenter (and optionally a generic GraphDB / triple-store endpoint).

It also specifies how PyArchInit's UI vocabularies (the `unita_tipo` combo box
and related dropdowns) become **slaved** to s3dgraphy's canonical JSON
dictionaries, so that adding a new unit type in s3dgraphy makes it appear in
PyArchInit without code changes.

## 2. Decisions captured during brainstorming

| # | Decision | Value |
|---|---|---|
| D1 | Datacenter targets | **A** (EM Datacenter, REST/JSON) and **B** (generic GraphDB / triple-store, SPARQL) |
| D2 | s3dgraphy target version | **0.1.40** (latest, includes `GraphMerger`, `GraphMLPatcher`, `classification` API, `aux_tracking`) |
| D3 | System of record | **C — per-entity ownership (hybrid)** |
| D4 | Vocabulary sync scope | All 4 vocabularies: units, edges, paradata, CIDOC-CRM mappings |
| D5 | Data sync scope | All 5 categories: raw US/USM/SF (local-only), published stratigraphic graph (push), virtual reconstructions + epoch (bidirectional), paradata authors/license/embargo (bidirectional), other excavations' graphs (pull-only browse) |
| D6 | Architectural approach | **Hybrid layered** (Approach 3): DB stays the source for raw stratigraphy; paradata layer in `paradata.graphml`; merge via `s3dgraphy.merge.GraphMerger` |
| D7 | URI strategy | UUID v7 stored in DB column `node_uuid` + human-readable `semantic_id` URI as label |
| D8 | Vocabulary divergence | Migrate `USVA/USVB → USVs`, `USVC → USVn` one-shot; align `pyarchinit_i18n_stratigraphic.py` to s3dgraphy abbreviations |

## 2.1 Alignment with T5.4 meeting (2026-05-04)

Source: `SC1_StratiGraph_T5.4_MeetingNotes_20260504.pdf` (Emanuel Demetrescu,
Enzo Cocca, Luca Mandolesi). The meeting validated the spec direction and
added five clarifications, captured here as first-class design constraints.

### A. EM version: 1.4 → 1.5 via dynamic JSON loading

PyArchInit currently hard-codes the **EM 1.4** stratigraphic-unit type list
inside `pyarchinit_i18n_stratigraphic.py` and similar helpers. The current
released Extended Matrix language is **EM 1.5**, and s3dgraphy ships the
authoritative type catalogue as JSON files inside its package. The
`VocabProvider` (§3.1) replaces the hard-coded list with a dynamic read of
those JSONs, so future EM releases (1.6, 1.7, …) are picked up by bumping the
s3dgraphy dependency — no PyArchInit code change.

This satisfies meeting action item **AI02** (Enzo Cocca, iterative).

### B. Property-graph layer first; CIDOC-CRM / triple-store deferred to WP3

s3dgraphy today exposes a **property-graph** representation: each node is a
small typed record (human ID, 16-digit machine UID, minimal description,
typed properties). This is the layer used by Heriverse and Blender + EM-tools
**today** and is the contract PyArchInit will speak.

The **triple-store / CIDOC-CRM** representation is the machine-actionable
form required by the European Collaborative Cloud (EOSC). Mapping property
values to CIDOC-CRM entities (e.g. *who took this photo on the morning of 4
May during the excavation*) is the typical interoperability bottleneck and is
being developed under **WP3** as the "intermediate body" between
property-graph payloads and triples. **It is not a blocker for T5.4.**

Implication for the phasing in §11: phases 1–3 target the property-graph
layer only. The `GraphDBBackend` (phase 4) is implemented against SPARQL
1.1, but the CIDOC-CRM mapping it consumes is the WP3 deliverable, not a
PyArchInit-side artefact. PyArchInit ships with a placeholder mapping file
sufficient for tests; the production mapping arrives via WP3.

### C. Delegate the GraphML writer to s3dgraphy

s3dgraphy already ships an **always-up-to-date GraphML writer** that tracks
the latest Extended Matrix version. PyArchInit currently maintains its own
`.xml` template embedding EM-compliant nodes; this duplicate writer is
**dropped**. The `GraphProjector` (§3.2) builds the in-memory s3dgraphy
graph and delegates serialisation to `s3dgraphy.exporter.graphml_exporter` (or
the equivalent symbol exposed in 0.1.40). Every new EM release reduces, on
the PyArchInit side, to bumping the s3dgraphy version pin.

This satisfies meeting action item **AI03** (Enzo Cocca, iterative). The
internal `.xml` writer file becomes a deprecated shim for one release cycle,
then is removed.

### D. Two-level validation (data entry + egress)

| Layer | Where | What it validates | When |
|---|---|---|---|
| **Data entry** | PyArchInit's existing US-relations validator (`tabs/US_USM.py` and friends) | Invalid relations, missing reciprocal relations, periodisation gaps, paradoxes | Live, while the user fills the US form |
| **Egress** | s3dgraphy, before any push to the central knowledge graph | Node-type schema (mandatory fields, datatypes), relation legality (e.g. *an actor cannot cut a USM*), visual-rule coverage | At `SyncEngine.push()` time, before the network call |

The two layers are complementary, not redundant: PyArchInit's validator
catches author mistakes early in a familiar UI; s3dgraphy's validator
guarantees that whatever reaches the knowledge graph satisfies the EM
formalism. Failures from the egress layer surface in the
`ConflictResolver` flow as 422 responses (§6.3, §8).

### E. Schema-as-data: s3dgraphy JSON catalogues

s3dgraphy externalises its formalism into JSON files shipped inside its
Python package. Three catalogues drive every consumer (PyArchInit, Heriverse,
Blender + EM-tools, tropi, FieldOS-style exports):

| File (canonical name in s3dgraphy 0.1.40) | Content | Consumed by `VocabProvider` for |
|---|---|---|
| `node_datamodel.json` (a.k.a. *nodes JSON*) | Every EM node type (US, USM, epochs, images, actors/authors, USVn/USVs, …): mandatory fields, accepted fields, datatypes, metadata | Combo-box population, schema validation, family classification |
| `connections_datamodel.json` (a.k.a. *relations JSON*) | Every legal relation between node types (e.g. *US is_after US* allowed; *Actor cuts USM* refused) | Edge-type combo, egress validation |
| Visual rules JSON (icons, colours, 3D logo file per node type) | Rendering metadata for any tool that wants to display an EM node | Future Harris-matrix and 3D-preview integrations; not consumed by data forms |

When the EM community adds a new node type (the example raised in the
meeting was an extension proposed by Knut, Korea), updating the JSONs in a
new s3dgraphy release is sufficient: every consuming tool — PyArchInit
included — picks up the new type without code changes. The
`VocabProvider`'s file-system watcher and `vocabulary_changed` signal close
the loop on the PyArchInit side.

### F. Function naming alignment with Blender + EM-tools

The Blender + EM-tools chain already uses two macro-functions at the
graph/tabular boundary: `populate_graph` (tables → in-memory graph) and
`populate_list` (graph → tables). PyArchInit adopts **the same names** for
the symmetric pair on the SQL side, even though PyArchInit's "list" is a
multi-table SQL fan-out rather than a Blender list. Keeping the names
identical lowers the cognitive cost for users moving between the two
ecosystems and makes the bridge symmetry explicit in the code.

| Direction | s3dgraphy + PyArchInit symbol | Implemented by |
|---|---|---|
| PyArchInit tables → in-memory s3dgraphy graph | `populate_graph(...)` | `GraphProjector` (§3.2) |
| In-memory s3dgraphy graph → PyArchInit tables | `populate_list(...)` | New `GraphIngestor` module (added in §3.7 below) |

UID semantics confirmed during the meeting: PyArchInit's per-record UID is
re-used as the s3dgraphy `EMid` (the GraphML attribute name on every node).
Collision means *same entity* and drives an **update**; absence drives a
**create**. This is the same hybrid "stable UUID + readable label" rule
formalised in §4.3 — the meeting just fixed the GraphML attribute name as
`EMid`.

This satisfies meeting action items **AI04** (bridge prototype) and **AI05**
(macro-function adoption).

## 2.2 Alignment with T5.4 Reference Document v0.1 (2026-05-06)

Source: `~/Downloads/T5.4_PyArchInit_s3Dgraphy_Reference_v0.1.pdf` — editor
Emanuel Demetrescu (CNR-ISPC, T5.4 Chair). Building on Enzo's proposal of
2026-05-05 and the meeting minutes of 2026-04-28 + 2026-05-04. Status: Draft
for partner review (Athena RC / FS Engineering–Italferr / WP3-WP4).

The reference document **confirms in full** the four substantive points of
§2.1 (validation in s3dgraphy, GraphML writer delegated, property-graph
first / CIDOC-CRM in WP3, identity aligned via `EMid` ↔ `node_uuid`) and
introduces five clarifications that we fold into this spec.

### G. Three JSON pillars, individually versioned

| File (in `ext_libs/s3dgraphy/JSON_config/`) | Content | v0.1 reference version | Currently bundled |
|---|---|---|---|
| `s3Dgraphy_node_datamodel.json` | All EM node types (stratigraphic, temporal, group, paradata, reference, visualisation, rights). Per type: class, parent, mandatory/optional properties, datatypes, mapping hints | 1.5.2 | 1.5.1 (in 0.1.30) |
| `s3Dgraphy_connections_datamodel.json` | All legal edge types and (source, target) node-type pairs — **36 edge types** in 1.5.4: `is_after`, `cuts`, `fills`, `overlies`, `abuts`, `is_bonded_to`, `changed_from`, … | 1.5.4 | (verify on 0.1.40 vendor) |
| `em_visual_rules.json` | Per node type: icon, fill/stroke colour, palette, 3D logo file. Plus document-role and content-nature visual variants | EM 1.5.0 | (verify on 0.1.40 vendor) |
| `em_qualia_types.json` (+ `_additions`) | Paradata sub-graphs vocabulary | — | bundled |
| `em_extractor_types.json` | Source-of-evidence node types | — | bundled |
| `em_document_types.json` | Document taxonomy | — | bundled |

The three pillars evolve independently with their own version field; client
tools can pin a minimum version on the one they care about. `VocabProvider`
exposes each version separately and rejects loads of files older than the
configured minimum, surfacing a banner in the QGIS log so users know which
EM features are temporarily unavailable.

The mapping `mappings/pyarchinit/pyarchinit_us_mapping.json` already exists
inside the s3dgraphy package and is the contract `GraphProjector` consumes;
per §7 of the reference document, **CNR-ISPC commits to keeping it
co-evolving with the `Stratigraph_00001` branch of pyarchinit**, so we have
a stable reference contract throughout T5.4 implementation.

### H. Consumption model: Option B (per-tool parsing) preferred — Option A coexists

The reference document (§4.5) raises the question of how the JSON configs
reach client tools. Two patterns are on the table:

| Option | What it means | Trade-off |
|---|---|---|
| **A — library-internal loading** | s3dgraphy parses the JSONs at import time, exposes a typed Python (and twin JS) API: `list_stratigraphic_types()`, `legal_edges_from(node_type)`, `visual_style_for(node_type)`. Clients never see the JSON | Narrow contract, schema cost shifts into the library |
| **B — per-tool parsing** | The JSONs are the public artefact; each tool parses them on its own to feed combo boxes, DB entries, palettes. Library still owns validation + serialisation | Forces every developer to look at the JSON once and form a clear mental model — fewer integration surprises |

**CNR-ISPC's preference is Option B**, and the two patterns can coexist
(library may still load JSON internally for its own use). For PyArchInit
this means the `VocabProvider` parses the JSON files **directly** rather
than wrapping a typed s3dgraphy API. The contract is the JSON itself —
guaranteed stable per Emanuel's commitment in §7.1 of the reference
document (top-level file names and top-level keys are public API; renames
deprecated one minor version in advance with a migration shim).

This simplifies the §3.1 `VocabProvider` design: no dependency on
unreleased typed APIs, no version coupling beyond the JSON file shape.

### I. EM 1.6 in pipeline — building archaeology + working units on surfaces

§4.3 of the reference document announces two EM 1.6 vocabulary axes that
land **as JSON entries**, not as s3dgraphy code changes:

- **Building archaeology**: complete unit set for upstanding architecture,
  including *neutral* stratigraphic units that record architectural
  reservations — doors, windows, niches: voids in masonry that are part of
  the design but not active stratigraphic events.
- **Working units on object surfaces**: `UL` / `WorkingUnit` will be
  augmented to model traces of working *on the surface of* artefacts and
  architectural elements (currently trialled in the Basilica Iulia
  dataset).

Implication for our migration plan: when `VocabProvider` is in place
(post-AI02), bumping s3dgraphy from 0.1.40 to whatever ships EM 1.6 makes
all these new types appear in PyArchInit combo boxes with **zero code
change**. The migration `USVA/USVB → USVs`, `USVC → USVn` (§4.4) is the
last one-shot vocabulary migration we expect.

### J. Synchronisation policy — last-writer-wins, but timestamps deferred

§5 of the reference document is the **only point where the answer
requested by my proposal is "not yet settled on our side either"**.

| Aspect | State | Implication for PyArchInit |
|---|---|---|
| Identity policy | **Settled.** s3dgraphy assigns UUID v7 on first read of any GraphML node lacking one; collision = same entity, absence = create new. PyArchInit's per-record UID lines up exactly | No migration needed beyond §4.3's UUID-as-`EMid` policy already in this spec |
| Conflict UX (draft) | Last-writer-wins with user notification: pop-up + hook PyArchInit subscribes to | `ConflictResolver` (§3.7) implements this contract; both pyarchinit and EM-tools surface the same notification UX |
| Modification timestamps | **Open.** Property graph has no `updated_at` per node today. Adding it naively risks duplicating triple-store provenance (PROV-O / CRMdig). Decision waits for PSNC-side KG revision-time encoding | Phase 1–3 work against `EMid`-only identity + opt-in conflict callback that, in absence of timestamps, simply asks the user. Stronger heuristic added later without API change |
| Locked-down at | AI08 resync (post-PyArchInit-team review of s3dgraphy sources + Volterra ~1500 US smoke test) | Drives concrete `ConflictResolver` policy + decides whether timestamp lives on node, paradata sub-node, or graph-level revision record |

This **unblocks Phase 1–3** of the roadmap (§11): we ship the bridge with
the simplest possible conflict callback (call user, they decide). The
timestamp-based heuristic gets added to `ConflictResolver` after AI08
without changing the public API.

### K. Division of responsibilities — explicit contract

§6 of the reference document fixes the ownership table that informs every
component split in §3 of this spec. Reproduced here for traceability:

| Concern | Owned by s3dgraphy | Owned by PyArchInit |
|---|---|---|
| EM formalism (node/edge types, legal relations, visual rules) | Authoritative — served as JSON, versioned per file | Consumer — reads via `VocabProvider` |
| GraphML serialisation | Authoritative writer, always EM-current | Delegated — internal `.xml` template retired |
| Validation at egress (graph → KG) | Authoritative — enforces JSON schema | Optional friendly validation at form time stays as is |
| Identity (`EMid` / per-record UID) | Generates UUID v7 on first read where missing | Stores UID on every record (already in place) |
| Sync policy (last-writer-wins, conflict UX) | Provides conflict callback + notification primitive | Subscribes to callback; surfaces it in QGIS |
| Triple-store I/O + CIDOC-CRM mapping | Will own once next s3dgraphy release lands; coordinated with WP3 | None — bridge writes through s3dgraphy when available |
| Tabular ingestion (forms, US/USM cards, geometries, photos) | None — s3dgraphy reads PyArchInit through existing mapping | Authoritative |
| 2D georeferenced refinement of data produced elsewhere | Provides absolute coordinates verbatim | Authoritative — `populate_list` writes back into QGIS layers |

### L. Georeferencing — out-of-the-box compatible

§4.4 of the reference document confirms that PyArchInit's QGIS-native
absolute coordinates (EPSG-coded) travel **verbatim** through the s3dgraphy
graph — nothing to convert, nothing to invent. PDF cards and 2D
georeferenced views generated by PyArchInit consume the same payload that
Heriverse reads in 3D.

The complementary case — 3D models and proxy positions in *local*
coordinates with a separate shift vector — is acknowledged as a real
concern for Blender + EM-tools but **out of scope for the PyArchInit ↔
s3dgraphy contract**, to be revisited later in T5.4 when (and only when) it
becomes load-bearing.

### M. New node types from real datasets — encouraged

§4.2 of the reference document explicitly anticipates that, working with
real Adarte datasets, we will surface the need for one or more node types
that s3dgraphy does not yet ship. *"That is a good outcome, not a problem."*
The same already happens on the EM-tools side (e.g. excavation photographs
as first-class graph nodes in the Basilica Iulia case study).

The contract: such additions are **JSON pull requests against the
s3dgraphy package**, not pyarchinit-side ad-hoc additions. After the PR
merges, every consumer (pyarchinit, EM-tools, Heriverse) sees the new type
without a code change.

This shifts our discovery work in Phase 2/3: when GraphProjector encounters
an unmapped pyarchinit field, the right action is to draft a JSON PR
against `s3dgraphy_node_datamodel.json` upstream rather than to extend the
mapping locally.

## 3. Components

Seven modules under `modules/s3dgraphy/sync/`. None of them blocks the
existing plugin functionality — all sync work happens in a `QThread`, and a
feature flag (`QSettings("pyarchinit/sync_enabled", False)`) disables the
whole subsystem leaving the plugin's pre-sync behavior intact.

### 3.1 `VocabProvider` (singleton, `QObject`)

Reads s3dgraphy's JSON dictionaries and exposes them to PyArchInit's UI.

```python
class VocabProvider(QObject):
    vocabulary_changed = pyqtSignal(str)  # 'units' | 'edges' | 'paradata' | 'cidoc'

    def __init__(self, plugin_dir: Path, user_config_dir: Path) -> None: ...

    def get_unit_types(self, lang: str | None = None) -> list[UnitType]: ...
    def get_edge_types(self, lang: str | None = None) -> list[EdgeType]: ...
    def get_paradata_types(self) -> dict[str, list[ParadataType]]: ...
    def get_cidoc_mapping(self, unit_type: str) -> str | None: ...
    def refresh_from_datacenter(self, client: 'DatacenterClient') -> RefreshResult: ...
    def reload_local(self) -> None: ...
```

Source priority (decreasing): `~/.config/pyarchinit/vocab_overrides/*.json`
(pulled from datacenter), then bundled `ext_libs/s3dgraphy/JSON_config/*.json`.
Merge is **per top-level key**, not whole-file: an override file that defines
only `stratigraphic_nodes.UL` overrides the bundled `UL` entry but leaves all
other types coming from the bundled file. This way a partial vocabulary update
from the datacenter does not erase locally available types. Cache in memory;
`QFileSystemWatcher` on both sources triggers `reload_local()` and emits
`vocabulary_changed`.

### 3.2 `GraphProjector`

Transforms PyArchInit DB rows into a stratigraphic-layer s3dgraphy `Graph`.
Reuses the already-existing `s3dgraphy.importer.pyarchinit_importer` as base,
overrides where mapping needs adjustment. Idempotent: project twice → identical
graph (modulo timestamps, which are normalized).

Output covers only stratigraphic-family nodes: `StratigraphicUnit`,
`StratigraphicUnitMasonry`, `DocumentaryStratigraphicUnit`,
`SpecialFindUnit`, `NegativeStratigraphicUnit`, `WorkingUnit`. Plus the
stratigraphic edges (`is_after`, `covers`, `cuts`, `leans_against`,
`has_same_time`, `fills`, `connected_to`).

### 3.3 `ParadataStore`

Owns `<project>/paradata.graphml` — a single file per QGIS project, versionable
in Git. CRUD API for the node types that have **no SQL counterpart**:
`AuthorNode`, `LicenseNode`, `EmbargoNode`, `DocumentNode`,
`VirtualSpecialFindUnit`, `USVn` / `USVs` (when authored locally), and
`EpochNode` (mirror of `periodizzazione_table` enriched with paradata).

Atomic persistence: write to `paradata.graphml.tmp` then `os.replace()`.
Crash-safe.

### 3.4 `SyncEngine`

Orchestrator. Runs in a `QThread`. Public API:

```python
class SyncEngine(QObject):
    state_changed = pyqtSignal(SyncState)  # idle | syncing | pending | conflict | error

    def push(self, graph_id: str, message: str | None = None) -> PushResult: ...
    def pull(self, graph_id: str) -> PullResult: ...
    def diff_against_remote(self, graph_id: str) -> GraphDiff: ...
    def fetch_metadata(self, graph_id: str) -> RemoteMetadata: ...
    def list_pending(self) -> list[QueuedOp]: ...
    def cancel_pending(self, op_id: str) -> None: ...
```

Composes the projected stratigraphic layer + `ParadataStore` content using
`s3dgraphy.merge.GraphMerger`. Persists offline queue in
`~/.cache/pyarchinit/sync_queue.sqlite`. Retry with exponential backoff
(2/4/8/16/30/60s, max 1h). Idempotent via `request_id` (UUID v7) header.

### 3.5 `DatacenterClient`

Transport abstraction. Concrete backends:
- `EMBackend` — REST/JSON, contract specified in section 6.
- `GraphDBBackend` — SPARQL UPDATE on named graphs `urn:pyarchinit:graph:{id}:rev:{rev}`,
  RDF Turtle conversion driven by `VocabProvider.get_cidoc_mapping()`.

Auth via `IAuthProvider`: phase 1 API key, phase 2 OAuth 2.0 device flow.
Configuration in QGIS Settings → PyArchInit → Datacenter dialog.

### 3.6 `GraphIngestor` (read-back path — `populate_list`)

The symmetric counterpart of `GraphProjector`. Takes an in-memory s3dgraphy
graph (built by s3dgraphy from any input format: GraphML, central knowledge
graph response, Heriverse JSON, Excel, tropi export, …) and writes/updates
the PyArchInit SQL tables.

```python
class GraphIngestor:
    def populate_list(
        self,
        graph: 's3dgraphy.Graph',
        *,
        site_filter: str | None = None,
        dry_run: bool = False,
    ) -> IngestResult: ...
```

Decision rule per node, driven by `node.EMid` ↔ `node_uuid` collision
(§4.3):

| Match in DB? | Local row newer than graph node? | Action |
|---|---|---|
| No | — | INSERT new row (preserve `node_uuid = EMid`) |
| Yes | No (graph wins) | UPDATE columns covered by the s3dgraphy mapping |
| Yes | Yes (DB wins) | Skip; surface in `IngestResult.skipped` for user review |
| Yes | Tie (same `updated_at`) | Skip; defer to `ConflictResolver` if the user requests reconciliation |

`GraphIngestor` never touches columns outside the s3dgraphy mapping
(`pyarchinit_us_mapping.json` and friends): user-only fields like internal
notes, photo captions, and Soprintendenza-specific metadata are preserved
verbatim. This is what makes Scenario B of the meeting (PyArchInit as a
**full participant**, refining 2D plans/elevations on top of 3D-derived
data) safe.

Used by `SyncEngine.pull()` (§3.4) but also exposed as a standalone
"Import GraphML / EM project" menu entry, so the read-back path is usable
even before the datacenter side ships.

### 3.7 `ConflictResolver`

Receives `MergeResult` from `GraphMerger`. Applies per-node-type policy
(see section 6.4). For nodes that require user intervention, opens a Qt dialog
with side-by-side diff (Local | Remote | Resolved) and three actions:
**Accept**, **Cancel**, **Save as branch**. Persists user choices to the
SyncEngine.

## 4. Data mapping and URI schema

### 4.1 Tables → node types

| PyArchInit table | Filter | s3dgraphy node | Authority |
|---|---|---|---|
| `us_table` | `unita_tipo IN {US,SU,UE,SE,ΣΜ,…}` | `StratigraphicUnit` | DB |
| `us_table` | `unita_tipo IN {USM,WSU,MSE,UEM,USZ,…}` | `StratigraphicUnitMasonry` | DB |
| `us_table` | `unita_tipo = 'USD'` | `DocumentaryStratigraphicUnit` | DB |
| `us_table` | `unita_tipo IN {USVs, USVn}` (post-migration) | `USVs` / `USVn` | Bidirectional via `paradata.graphml` |
| `inventario_materiali_table` | — | `SpecialFindUnit` | DB |
| `site_table` | — | Site metadata properties | DB |
| `periodizzazione_table` | — | `EpochNode` | **Bidirectional** |
| (no SQL) | paradata-only | `AuthorNode`, `LicenseNode`, `EmbargoNode`, `DocumentNode`, `VirtualSpecialFindUnit` | `paradata.graphml` |

Existing `ext_libs/s3dgraphy/mappings/pyarchinit/pyarchinit_us_mapping.json`
is the column→property base; `GraphProjector` overrides only where needed.

### 4.2 Stratigraphic relations → edge types

| `rapporti` value (PyArchInit) | s3dgraphy edge | Canonical direction |
|---|---|---|
| Copre / Covers | `covers` | recent → ancient |
| Coperto da | `is_after` | recent → ancient |
| Taglia / Cuts | `cuts` | recent → ancient |
| Tagliato da | `is_after` | recent → ancient |
| Si appoggia a | `leans_against` | recent → ancient |
| Uguale a / Same as | `has_same_time` | symmetric |
| Riempie | `fills` | recent → ancient |
| Connesso a | `connected_to` | symmetric |

Full table maintained inside `VocabProvider`, sourced from
`connections_datamodel.json`. Read-only direction: PyArchInit translates,
does not invent edge types.

### 4.3 URI schema (stable identity)

Hybrid: opaque UUID v7 stable across renames + readable URI as label.

```
node.id          = "0192a3f1-9b4d-7c2e-8d3a-..."           # node_uuid column (stable)
node.semantic_id = "pyarchinit:site=Volterra/area=A1/us=24"  # human-readable label
node.local_label = "US 24"                                   # localized
```

The `node_uuid` is the sync key. The `semantic_id` is regenerated from
current site/area/us values, used for debug, and free to change when records
are renamed.

**GraphML attribute name.** When the in-memory graph is serialised to
GraphML by s3dgraphy (§7.6 below), `node.id` lands on every node under the
attribute name `EMid` (Extended-Matrix id). This is the wire-level
identifier seen by every other tool in the chain (Heriverse, Blender +
EM-tools, tropi, FieldOS exports). PyArchInit's `node_uuid` and s3dgraphy's
`EMid` are **the same value with two names** depending on the layer; no
mapping table is needed.

For paradata-only nodes: the `ParadataStore` generates the UUID v7 at
creation; `semantic_id` follows the same scheme:
`pyarchinit:site=Volterra/epoch=Roman_Imperial`.

### 4.4 Vocabulary alignment migration

`USVA / USVB → USVs`, `USVC → USVn`. One-shot script in
`scripts/migrations/2026_05_us_vocabulary_alignment.py` with `--dry-run`,
`--apply`, `--rollback`. Auto-backup of each DB to
`<db_path>.pre_alignment_<date>` before the `UPDATE`. Logs to
`migration.log`.

After migration, `pyarchinit_i18n_stratigraphic.py` is rewritten as an adapter
over `VocabProvider` — kept for one release cycle for backward import
compatibility, then removed.

### 4.5 Required DB schema migration (minimal, additive)

```sql
ALTER TABLE us_table ADD COLUMN node_uuid TEXT;
ALTER TABLE inventario_materiali_table ADD COLUMN node_uuid TEXT;
ALTER TABLE periodizzazione_table ADD COLUMN node_uuid TEXT;
CREATE UNIQUE INDEX ix_us_node_uuid ON us_table(node_uuid);
CREATE UNIQUE INDEX ix_im_node_uuid ON inventario_materiali_table(node_uuid);
CREATE UNIQUE INDEX ix_per_node_uuid ON periodizzazione_table(node_uuid);
-- backfill via scripts/migrations/2026_05_node_uuid_backfill.py
```

Compatible with both SQLite and PostgreSQL. No new tables, only one nullable
column on three existing tables (the three tables whose rows map to graph
nodes per section 4.1: `us_table`, `inventario_materiali_table`,
`periodizzazione_table`). `tomba_table` is intentionally **not** migrated:
burial records are out of scope for this spec.

## 5. Vocabulary sync layer

### 5.1 Propagation chain

```
EM Datacenter (in costruzione)
  ↓ GET /api/v1/vocabularies/<name>
~/.config/pyarchinit/vocab_overrides/*.json   (priority 1)
ext_libs/s3dgraphy/JSON_config/*.json          (priority 2, bundled fallback)
  ↓ load + merge
VocabProvider (cache, QFileSystemWatcher, vocabulary_changed signal)
  ↓ get_unit_types(lang)
pyarchinit i18n layer (resources/vocab/vocab_i18n.json — translator-editable)
  ↓ ordered list
US/USM/SF form widgets (comboBox_unita_tipo, comboBox_rapporti, …)
```

### 5.2 i18n separation of concerns

| Concern | Source |
|---|---|
| Which types exist | s3dgraphy `node_datamodel.json` |
| Localized abbreviation per language | PyArchInit `vocab_i18n.json` |
| Localized label and description | PyArchInit `vocab_i18n.json` |
| CIDOC-CRM mapping | s3dgraphy datamodel |
| Family / symbol | s3dgraphy datamodel |

When s3dgraphy adds a new type (e.g. `WorkingUnit` in 0.1.35) the
`VocabProvider` exposes it immediately. PyArchInit shows the English label
until a translator adds the localized entry; a warning is logged once per
session.

### 5.3 Hot-reload

UI dialogs connect to `vocabulary_changed`. The existing snippet at
`tabs/US_USM.py:17207` already implements
`blockSignals → clear → addItems → setEditText(current_text)` — reused
verbatim. If the current value is no longer valid (e.g. `USVA` removed
post-migration), a warning banner at the bottom of the form suggests the
replacement.

### 5.4 Refresh policy

| Trigger | Action |
|---|---|
| Plugin start | Load local cache (instant). Background `refresh_from_datacenter()` with 5s timeout. Failure: silent fallback. |
| Manual "Sync vocabularies" menu entry | Explicit refresh with feedback dialog (new, deprecated, conflict counts). |
| `QFileSystemWatcher` event on a JSON | Immediate `reload_local()`. |
| Plugin update (s3dgraphy version bump) | Bundled JSONs change → watcher reloads automatically. |

## 6. Sync protocol and API contract

### 6.1 Concurrency model

Optimistic concurrency at the **graph-as-a-whole** granularity, not per-node.
Each published graph has:

- `graph_id` — UUID v7, generated on first publish
- `revision` — UUID v7, monotonic, bumped on every accepted push
- `parent_revision` — the revision this one is derived from
- `checksum` — SHA-256 of canonicalized GraphML (integrity check)

Client retains `last_known_remote_revision` per project in `QSettings`.

**Rationale for graph-level revisions:** Harris matrices are coherent only as
a whole — changing one relation can invalidate another. Per-node would
require distributed transactions or a server-side constraint solver.
Graph-level keeps payloads under 1 MB even for ~1500 US datasets.

### 6.2 Operations

| Op | Trigger | Behavior |
|---|---|---|
| `pull` | Manual / project open | Fetch HEAD if differs from `last_known_remote_revision`. 3-way merge with local paradata. Conflicts → `ConflictResolver`. Update `paradata.graphml` and `last_known_remote_revision`. |
| `push` | Manual ("Publish") | Compose stratigraphic projection + paradata, checksum, send with `parent_revision = last_known_remote_revision`. 409 → enter pull→merge→push flow. |
| `diff` | Pre-publish dry-run | Show user the diff (added/removed/changed nodes) before confirming. |
| `fetch_metadata` | Background, lightweight | `GET /graphs/<id>/HEAD` returns only `{revision, checksum, updated_at, updated_by, node_count}`. Updates status bar indicator. |

### 6.3 REST API contract for EM Datacenter

Versioned at `/api/v1/`. The EM team implements this; PyArchInit consumes it.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1/graphs` | GET | List published graphs (filters: site, author, embargo_status, period). Paginated. |
| `/api/v1/graphs` | POST | Create a new `graph_id`. Body: `{site, area, owner, license_id}`. Returns `{graph_id, initial_revision}`. |
| `/api/v1/graphs/{id}/HEAD` | GET | Head metadata: `{revision, parent_revision, checksum, updated_at, updated_by, node_count}`. Cheap. |
| `/api/v1/graphs/{id}/revisions/{rev}` | GET | Full GraphML for the revision. Supports `If-None-Match`. |
| `/api/v1/graphs/{id}/revisions` | POST | Push a new revision. Body: `{parent_revision, graphml, checksum, message, request_id}`. Returns 201 with new revision, or 409 with current revision. |
| `/api/v1/graphs/{id}/revisions` | GET | Revision history (for "git log" view). Paginated. |
| `/api/v1/vocabularies/{name}` | GET | Returns a vocabulary JSON (`units`, `edges`, `paradata`, `cidoc`). Supports `If-Modified-Since`. |
| `/api/v1/vocabularies` | GET | Lists available vocabularies with `updated_at`. |

Status codes: 200, 201, 304, 401, 403, 409 (conflict, body has `current_revision`),
422 (validation, body has violations list), 429 (rate-limit, `Retry-After`
header).

### 6.4 Conflict resolution policy

| Node type | Policy |
|---|---|
| `StratigraphicUnit` / `StratigraphicUnitMasonry` / `DocumentaryStratigraphicUnit` / `SpecialFindUnit` | **Always dialog** — primary data, never silent auto-merge |
| `EpochNode` | Auto-merge if only timestamp changes; dialog if label or temporal range changes |
| `AuthorNode` | Last-writer-wins by `updated_at`; passive notification |
| `LicenseNode`, `EmbargoNode` | **Server always wins** (compliance / centralized governance) |
| `USVn` / `USVs` / `VirtualSpecialFindUnit` | Dialog (interpretations — conflicts are semantically meaningful) |
| `DocumentNode` | Per-property merge (URI immutable, metadata last-writer-wins) |

### 6.5 Authentication

- **Phase 1 (MVP):** API key in `Authorization: Bearer <key>`. Stored in
  `QSettings` with encrypted flag.
- **Phase 2:** OAuth 2.0 device flow (institutional SSO).

`DatacenterClient` is parameterized over `IAuthProvider` so adding phase 2
does not require rewriting the client.

### 6.6 Offline and retry

| Situation | Behavior |
|---|---|
| Push offline | Save payload + `parent_revision` to `~/.cache/pyarchinit/sync_queue.sqlite`. Status bar shows "pending". Retry on network event with exponential backoff (2/4/8/16/30/60s, max 1h). |
| Pull offline | Use last cached GraphML. Status bar: "stale (last sync: 2h ago)". |
| Queued push triggers conflict on retry | Standard `ConflictResolver` flow. Nothing lost. |
| Server 5xx | Backoff retry. After > 5 min, persistent notification, queue retained. |

Idempotency: every push includes a `request_id` (UUID v7) header. The server
treats a duplicate `request_id` as the original — returns the existing
revision instead of creating a new one. The client retains `request_id` in the
queue until 2xx.

### 6.7 GraphDB / triple-store backend variant

Same `SyncEngine`, different transport.

| EM operation | GraphDB equivalent |
|---|---|
| `POST /graphs/{id}/revisions` | `SPARQL UPDATE` into named graph `urn:pyarchinit:graph:{id}:rev:{rev}`; promote to head by setting `pa:isHead "true"` |
| `GET /graphs/{id}/revisions/{rev}` | `CONSTRUCT { ?s ?p ?o } FROM <urn:…:rev:{rev}> WHERE { ?s ?p ?o }` |
| Conflict detection | `ASK { GRAPH ?g { ?g pa:revision <{parent_rev}> ; pa:isHead true } }` |

GraphML → RDF Turtle conversion driven by `VocabProvider.get_cidoc_mapping()`,
encapsulated inside `GraphDBBackend`. `SyncEngine` is unaware.

## 7. Upgrade plan: 0.1.30 → 0.1.40

### 7.1 Audit summary

Current PyArchInit code uses **only 3 s3dgraphy symbols**: `Graph`, `Node`,
`Edge`. These have stable APIs since 0.1.20. Direct breakage risk is low.
The work is in **adopting new modules** (`GraphMerger`, `classification`,
`aux_tracking`) and refactoring 12 string-tagged modules in
`modules/s3dgraphy/` to use typed s3dgraphy nodes.

### 7.2 New 0.1.40 APIs we will adopt

| API | Available since | Used in |
|---|---|---|
| `s3dgraphy.merge.GraphMerger` | 0.1.33 | `SyncEngine` (3-way merge on pull and 409) |
| `s3dgraphy.merge.GraphMLPatcher` | 0.1.33 | `ParadataStore` (incremental patch) |
| `s3dgraphy.classification` (`get_family`, `is_real`, `iter_subtypes`) | unreleased→0.1.40 | `VocabProvider` |
| `NegativeStratigraphicUnit` / `WorkingUnit` | 0.1.35 / unreleased | `GraphProjector` |
| `aux_tracking` (`mark_as_injected`, `apply_override_reversal_policy`) | unreleased | `SyncEngine` (volatile vs bake) |
| `importer.pyarchinit_importer` | already present | `GraphProjector` (base) |
| `exporter.unified_xlsx_exporter` | 0.1.37 | Optional offline export fallback |

### 7.3 Code touch list

| File | Change | Effort |
|---|---|---|
| `modules/s3dgraphy/s3dgraphy_integration.py` (1281 lines) | Replace `Node()` constructions with typed factories that read type from `VocabProvider`. Drop `node.node_type = 'string'` patterns. | M (1 day) |
| `modules/s3dgraphy/s3dgraphy_dot_bridge.py` | Visual mapping reads `family` via `classification.get_family()` instead of hardcoded table. | S (3-4 h) |
| `modules/s3dgraphy/cidoc_crm_mapper.py` | Drop hardcoded `CRM_CLASSES`, look up via `VocabProvider`. | S (2-3 h) |
| `modules/s3dgraphy/matrix_graph_visualizer.py`, `matrix_visualizer_qgis.py`, `plotly_visualizer.py` | Filter expressions move from `node_type = 'stratigraphic_unit'` to `family = 'real'` via classification API. | S (1-2 h each) |
| `modules/s3dgraphy/blender_integration.py` | Audit only; Blender export is a private format, OK to keep its own tags. | XS |
| `modules/s3dgraphy/graphml_spatial_enhancer.py`, `spatial_grouping_manager.py`, `simple_graph_visualizer.py` | Audit; expected zero changes. | XS |
| `modules/s3dgraphy/graphviz_visualizer.py` | None; compatible. | — |
| `modules/utility/pyarchinit_i18n_stratigraphic.py` | Refactor as adapter over `VocabProvider`. Keep file as compat shim for one release. | M (1 day) |

Total estimate: ~2-3 days refactor + 1-2 days tests = 1 person-week.

### 7.4 Procedure

1. Create branch `feature/s3dgraphy-bridge-0.1.40` and tag
   `pre-s3dgraphy-040` for fast rollback.
2. Run baseline test suite, save green result.
3. Replace vendored package:
   ```bash
   cd ext_libs/
   rm -rf s3dgraphy s3dgraphy-0.1.30.dist-info
   pip install s3dgraphy==0.1.40 --target . --no-deps
   ```
4. Smoke test: restart QGIS, open a US form, generate a Harris matrix.
   No refactor yet.
5. Run `scripts/migrations/2026_05_us_vocabulary_alignment.py --dry-run`, then
   `--apply`.
6. Run `scripts/migrations/2026_05_node_uuid_backfill.py`.
7. Refactor files one-by-one (suggested order: `cidoc_crm_mapper` →
   `s3dgraphy_integration` → `matrix_visualizer_qgis` → rest). Test after
   each.
8. Implement new modules in `modules/s3dgraphy/sync/`: `VocabProvider`,
   `GraphProjector`, `ParadataStore`, `SyncEngine`, `DatacenterClient`,
   `ConflictResolver`.
9. Update `requirements.txt`: `s3dgraphy>=0.1.40`.
10. Update CHANGELOG (bilingual IT+EN), bump plugin version `5.0.25-alpha` →
    `5.1.0-alpha`.

### 7.5 Required data migrations

| Script | Purpose | Idempotent |
|---|---|---|
| `2026_05_us_vocabulary_alignment.py` | `USVA`/`USVB` → `USVs`, `USVC` → `USVn` in all open `us_table` databases. Auto-backup before mutating. Logs to `migration.log`. | Yes |
| `2026_05_node_uuid_backfill.py` | `ALTER TABLE` to add `node_uuid TEXT` to four tables, then `UPDATE` with UUID v7 where NULL. Creates unique index. | Yes |
| `2026_05_paradata_bootstrap.py` | For each QGIS project, create empty `paradata.graphml` if missing. Seed with `AuthorNode` from user preferences. | Yes |

All scripts support `--dry-run`, `--apply`, `--rollback`. Accessible via
QGIS menu → PyArchInit → Maintenance → Migrations.

### 7.6 Drop the in-house GraphML writer (delegate to s3dgraphy)

Per meeting decision §2.1.C, the EM-compliant `.xml` template currently used
by PyArchInit's GraphML writer is **superseded** by s3dgraphy's built-in
GraphML exporter, which always tracks the latest EM version.

| File | Change | Effort |
|---|---|---|
| `modules/s3dgraphy/s3dgraphy_integration.py` (writer paths) | Replace local GraphML construction with `s3dgraphy.exporter.graphml_exporter` (or the equivalent symbol exposed in 0.1.40); delete the embedded `.xml` template once the migration is verified. | M (1 day) |
| `modules/export/graphml_writer*.py` (if any standalone writer remains) | Re-route through `GraphProjector.to_graphml()` which delegates to s3dgraphy. | S (3-4 h) |
| `resources/templates/em_graphml_template.xml` (or similar) | Mark as deprecated; remove after one release cycle. | XS |

**Self-test gate.** Before deleting the legacy writer, run a
byte-equivalence check on a representative dataset: project the same
PyArchInit DB through both writers (legacy and delegated), GraphML-diff the
results. Differences must be limited to attributes s3dgraphy adds (newer EM
version metadata) — never to attributes s3dgraphy removes. Test fixture in
`tests/integration/test_graphml_writer_parity.py`.

### 7.7 Rollback

| Failure point | Rollback action |
|---|---|
| `ext_libs/` replace fails | `git checkout ext_libs/s3dgraphy` (was versioned) |
| Smoke test red post-replace | Same; checkout `pre-s3dgraphy-040` tag |
| Vocab migration corrupts DB | Auto-backup at `<db>.pre_alignment_<date>`; restore via `cp` |
| UUID backfill partial failure (PostgreSQL) | Script `--rollback` does `ALTER TABLE … DROP COLUMN node_uuid` |
| Single module refactor introduces regression | Per-module commits → selective `git revert <sha>` |
| Sync engine unstable in production | Feature flag `QSettings("pyarchinit/sync_enabled", False)` disables push/pull, leaves read-only export functional |

## 8. Error handling

Strata: 8 error categories, each with a strategy.

| Category | Strategy |
|---|---|
| Network | Offline queue + exponential backoff. Notify user only after 3 consecutive failures (no noise). |
| Auth | Suspend queue, show "Re-authenticate" dialog. Queue is preserved across re-login. |
| Concurrency (409) | `ConflictResolver` flow. Conflicts are never swallowed. |
| Schema validation (422) | Not auto-recoverable. Dialog shows specific violations and edit suggestions. Push blocked until fixed. |
| Integrity (checksum mismatch, malformed GraphML) | Reject payload, retry once, then log + dialog. |
| Database | Reuse `pyarchinit_db_manager`. Errors bubble up with "during sync operation X" context. |
| Filesystem | Specific path in notification, suggest fix. No crash; in-memory fallback + persistent warning. |
| Internal bug | Top-level wrapper: log with stack + anonymized payload → "Open issue with logs" dialog. Does **not** block non-sync plugin functionality. |

**Guiding principle:** the sync layer is **secondary** to the excavation
work. A sync error must never block saving a US form, opening a project, or
generating a local Harris matrix. `SyncEngine` runs in `QThread`; its
exceptions never escape to the QGIS main thread.

### 8.1 Logging channels

| Channel | Content | Audience |
|---|---|---|
| `QgsMessageLog` tag `"PyArchInit-Sync"` | Human-readable events ("Push to datacenter started", "Vocabulary refreshed (3 new types)") | User via QGIS Log Messages panel |
| `~/.cache/pyarchinit/sync.log` (rotating, 5×2MB) | Structured JSON: timestamp, op, status, latency_ms, payload_size, request_id, error_class, stack | Developer when user shares logs |
| `~/.cache/pyarchinit/sync_queue.sqlite` | Offline queue: timestamp, op, payload, attempts, last_error, next_retry_at | "Show pending sync" dialog |
| QGIS status bar | Live state: idle / syncing / pending(N) / conflict / error. Click for details. | User always |

Logs **never contain PII** — no stratigraphic content, only metrics and IDs.
Full payloads live only in `sync_queue.sqlite`, exportable on user's explicit
consent.

### 8.2 Local metrics (no external telemetry)

Small SQLite table `~/.cache/pyarchinit/sync_metrics.sqlite`:
- `op_count` per type (push/pull/diff/vocab_refresh)
- `error_count` per type
- `conflict_resolution_outcome` (local/remote/branched)
- p50/p95/p99 latency per op
- `queue_depth_high_water_mark`

Surfaced in a "Sync diagnostics" dialog. **Nothing is automatically sent
anywhere.**

## 9. Testing strategy

Pyramid: ~150 unit, ~30 integration, ~5 E2E.

### 9.1 Per-module test focus

| Module | Coverage |
|---|---|
| `VocabProvider` | JSON read, override priority, hot-reload, missing-translation fallback, signal emission |
| `GraphProjector` | Idempotency, mapping coverage per `unita_tipo`, orphan handling, geometry preservation |
| `ParadataStore` | CRUD, atomic persistence (no half-graphml on crash), import-existing |
| `SyncEngine` | Push happy path, push 409 → pull → merge → push, offline queue, retry backoff, request_id idempotency |
| `DatacenterClient` | EM mock, GraphDB with local Fuseki in Docker, auth provider switching |
| `ConflictResolver` | Pure logic separate from UI, per-type policy, deterministic outputs |
| Vocab migration | Accurate dry-run report, idempotent apply, working rollback, multi-DB |
| UUID backfill | SQLite + PostgreSQL schema migration, partial-failure recovery, unique-index correctness |

### 9.2 E2E scenarios (5 minimum before release)

1. **Happy path publish** — first push, second push, third push (3 revisions)
2. **Conflict + resolve** — A publishes R1, B publishes R2, A pushes from R1 → 409 → pull R2 → merge → push R3
3. **Offline queue** — push with datacenter down, datacenter up, retry succeeds
4. **Vocabulary update** — datacenter publishes a new type, PyArchInit receives it, comboBox shows it
5. **Pull-only browse** — user B downloads user A's graph in read-only mode, cannot push

A small HTTP server `tests/e2e/mock_datacenter.py` implements the section 6.3
contract with in-memory storage.

### 9.3 Manual smoke tests (pre-release gate)

1. **Three OS smoke** — macOS Sequoia, Windows 11, Ubuntu 24.04 LTS. Open a
   pre-upgrade PyArchInit project, accept the migration prompt, verify the
   Harris matrix still generates.
2. **Stress on large dataset** — Volterra (~1500 US): push latency target
   `< 5s` for full GraphML, `< 30s` for upload to a real datacenter.
3. **UI responsiveness during sync** — push must not block the QGIS event
   loop (sync runs in `QThread`).

## 10. Definition of Done

- All unit + integration tests green in CI (target: GitHub Actions, 3 OS × 2 Python = 6 jobs)
- All 5 E2E scenarios green against the mock datacenter
- Manual smoke results documented in `docs/superpowers/specs/s3dgraphy-bridge-design/smoke-results.md`
- CHANGELOG updated with bilingual entry (IT/EN)
- Tutorials updated in 9 languages for the new sync UI
- Plugin version bumped to `5.1.0-alpha`, git tag created, pushed to origin
- API contract document (this spec, sections 6.3 and 6.7) delivered to and acknowledged by the EM Datacenter team

## 11. Implementation phasing

The scope is too large for a single implementation plan. It should be
decomposed into four phases, each with its own plan and PR series. The
phases are independently shippable: stopping after any of them leaves the
plugin in a coherent state.

| Phase | Deliverable | User-visible value | Risk |
|---|---|---|---|
| **1. Foundation** | s3dgraphy 0.1.30 → 0.1.40 upgrade. `VocabProvider` reading bundled JSONs only (no datacenter pull yet). Refactor of `pyarchinit_i18n_stratigraphic.py` as adapter. Vocab alignment migration (`USVA/USVB → USVs`, `USVC → USVn`). UUID backfill migration. Refactor of the 12 `modules/s3dgraphy/` files. | New unit types appear in combo boxes when s3dgraphy is updated; existing functionality preserved. | Low: only library upgrade and refactor, no networking. |
| **2. Local graph layer** | `GraphProjector` + `ParadataStore`. New menu entry "Generate stratigraphic graph". `paradata.graphml` per project, editable through new dialogs. No networking. | User can produce a coherent s3dgraphy graph file from their excavation data; can author paradata locally. | Medium: introduces new file management and dialogs. |
| **3. Datacenter sync (EM backend)** | `SyncEngine` + `DatacenterClient` with `EMBackend`. Push/pull/diff/conflict UI. Offline queue. Mock datacenter for tests. | User can publish to and pull from EM Datacenter (when EM team finishes its construction). | High: depends on EM Datacenter API actually existing. Phase 3 ships gated behind feature flag if datacenter is not ready. |
| **4. GraphDB backend (parallel)** | `GraphDBBackend` implementing the same `IDatacenterBackend` interface. Configurable via Settings. RDF/Turtle conversion driven by CIDOC mappings. | Institutional triple-store deployments (Fuseki, GraphDB, Stardog) become a sync target. | Medium: SPARQL semantics vary across triple-stores; testing against multiple is needed. |

Phase 4 can run in parallel with phase 3 once phase 2 is complete: the
backends are independent. Each phase produces its own implementation plan
following this spec.

**Property-graph first (meeting §2.1.B).** Phases 1–3 target the
property-graph layer of s3dgraphy — the layer Heriverse and Blender +
EM-tools already consume today. The CIDOC-CRM mapping that lifts those
property values to the triple-store form required by the European
Collaborative Cloud is the WP3 deliverable and is **not on PyArchInit's
critical path**. Phase 4's `GraphDBBackend` ships against the SPARQL 1.1
surface; the CIDOC-CRM enrichment it delegates to is whatever WP3 publishes
when it is ready.

## 12. Open questions

1. **EM Datacenter authentication scheme.** Phase 1 spec assumes API key in
   `Authorization: Bearer`. The EM team may already have an OIDC/SSO design in
   mind — to be confirmed when their construction milestone publishes the
   API.
2. **GraphDB target identity.** Which deployment? Apache Jena Fuseki?
   GraphDB Free? Stardog? The triple-store choice affects test setup. Spec
   currently targets the SPARQL 1.1 standard surface so any compliant
   triple-store works, but performance and named-graph semantics vary.
3. **Multi-site projects.** A single QGIS project can contain multiple
   PyArchInit sites. Does each site map to its own `graph_id`, or is there
   one project-level graph? Current spec assumes one-graph-per-site (cleaner
   ownership), but EM team may prefer one-project-graph for cross-site
   correlation.
4. **PostgreSQL `node_uuid` extension.** Spec uses UUID v7, which requires
   PostgreSQL 17+ for native support; on older versions the migration script
   generates UUID v7 in Python and inserts as text. To be confirmed against
   the deployment fleet.
5. **Embargo policy enforcement.** When `EmbargoNode` says "embargo until
   2030", does the datacenter hide the graph from `/graphs` listings, or
   show it with restricted access? Server-side decision, document at
   integration time.

## 13. References

- **Meeting minutes (alignment source for §2.1):**
  `~/Downloads/SC1_StratiGraph_T5.4_MeetingNotes_20260504.pdf` — StratiGraph
  WP5 / T5.4 — Pyarchinit ↔ s3Dgraphy connection — 2026-05-04, 11:13–12:02
  CEST. Chair: Emanuel Demetrescu (CNR-ISPC). Action items AI01–AI08.
- **T5.4 Reference Document v0.1 (alignment source for §2.2):**
  `~/Downloads/T5.4_PyArchInit_s3Dgraphy_Reference_v0.1.pdf` — editor:
  Emanuel Demetrescu (CNR-ISPC). Date: 2026-05-06. Status: Draft for
  partner review (Athena RC, FS Engineering / Italferr, WP3-WP4). Confirms
  the four substantive points of Enzo's proposal of 2026-05-05 and adds
  the JSON-pillars catalogue, the Option B consumption preference, the
  EM 1.6 pipeline preview, the synchronisation-policy honest framing, and
  the division-of-responsibilities table reproduced in §2.2.K.
- s3dgraphy v0.1.40 source: <https://github.com/zalmoxes-laran/s3dgraphy>
- s3dgraphy core concepts:
  <https://docs.extendedmatrix.org/projects/s3dgraphy/en/latest/s3dgraphy_core_concepts.html>
- Extended Matrix "How to" (entry point to s3dgraphy Sphinx docs):
  <https://docs.extendedmatrix.org/>
- PyArchInit API documentation (Sphinx, hosted on pyarchinit.org).
- Section PDFs (rendered for review):
  - `docs/superpowers/specs/s3dgraphy-bridge-design/01-componenti.pdf`
  - `docs/superpowers/specs/s3dgraphy-bridge-design/02-mappatura-uri.pdf`
  - `docs/superpowers/specs/s3dgraphy-bridge-design/03-vocabulary-sync.pdf`
  - `docs/superpowers/specs/s3dgraphy-bridge-design/04-sync-protocol.pdf`
  - `docs/superpowers/specs/s3dgraphy-bridge-design/05-upgrade-migration.pdf`
  - `docs/superpowers/specs/s3dgraphy-bridge-design/06-errori-test.pdf`
