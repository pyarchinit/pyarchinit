# One Bridge — pyArchInit on the library's `s3dgraphy.sync`, em.json/EMStudio, room delivery

**Spec date:** 2026-10-07
**Author:** Enzo (brainstorming session, decisions captured below)
**Status:** Shipped (A+B1) — 2026-10-07: A1–A3 `one-bridge-5.13.24-alpha`, B1 `em-export-5.13.25-alpha`, A4 `graphml-retire-5.13.26-alpha`, A5 `one-bridge-closing-5.13.27-alpha`. B2 and C wait for the StratiGraph node.
**Branch:** `Stratigraph_00001` only (decision of 2026-10-07: no feature ports to `master`)
**Target s3dgraphy:** `1.6.0.dev40` at the time of writing — pinned **exact** at migration time (never `>=`), re-checked against the then-current dev release
**Driving threads:** ExtendedMatrix/s3Dgraphy#25 (direction), #26 (US mapping), #27 (performance, fixed in dev40), pyarchinit/pyarchinit#663 (DOT stays), Emanuel's Telegram notes of 2026-10-07 (rooms: REST vs WebSocket; contract; room client; EMStudio viewer)

## 1. Overview

pyArchInit carries its own copy of the graph bridge in `modules/s3dgraphy/sync`
(24 modules, 12,361 lines). It was upstreamed into the s3dgraphy library
(PRs #11/#12) and the two copies have drifted ever since: the library moved to
1.6.0.dev40 while the plugin pins `1.6.0.dev9`, and swapping dev40 under the
vendored bridge breaks 26 of our sync tests (measured 2026-10-07; §3). Every
new capability of the library — the dev40 performance fixes, `em.json`,
`stratigraphic_kind`, the RDF/CIDOC exporter, `s3dgraphy.contract` — lands on
the far side of that drift.

This spec makes the library's `s3dgraphy.sync` the **one bridge**. The
vendored package shrinks to the pyArchInit-specific extensions; the plugin
imports everything else from the library. On that foundation, two
user-visible capabilities follow: **em.json export with EMStudio as the
matrix viewer** (B), and the **asynchronous REST delivery of a site to a
StratiGraph room** (C).

The work is a chain of three sub-projects — **A** (one bridge), **B**
(em.json + EMStudio), **C** (room delivery) — in one spec, released
separately. B1 depends on A2; B2 and C also depend on a reachable
StratiGraph node.

## 2. Decisions captured during brainstorming

| # | Decision | Value |
|---|----------|-------|
| 1 | Scope of this spec | The whole chain A + B + C, one spec, separate releases |
| 2 | Fate of the yEd/GraphML path | **Import stays** (one-time, library pipeline + our Qt dialogs). **Our GraphML export retires** (groups-as-folders, swimlane rendering) once the EMStudio viewer (B) works; its tests are retired with written rationale |
| 3 | C test environment | Designed against `s3dgraphy.contract`; verified against a **locally-run `stratigraph-server`** (open source). Access to the real node (Keycloak/ORCID, editor role) is a noted prerequisite, not a blocker |
| 4 | Migration approach | **Section-by-section replacement with parity tests** (approach 1): each functional path moves to the library and its tests decide; the suite must be green on dev40 at every stage; the vendored modules disappear at the end of A, not at the start |
| 5 | How pyArchInit talks to a room | **REST** (`POST /v1/rooms/{id}/ops`, ≤1000 ops, idempotent), never the WebSocket room: pyArchInit delivers and leaves (Emanuel, 2026-10-07) |
| 6 | `refused` semantics | A refused operation inside a 200 is a **response of a converging system, not an error**: never retried, reported in the summary |
| 7 | Authorship | The author of every operation is the authenticated caller; any author inside the payload is discarded by the server. Writing needs the editor role in the room |
| 8 | Operation identity | Stable ids derived via `s3dgraphy.contract.stable_id` — **never uuid4** — so a second delivery duplicates nothing |
| 9 | Classic Harris-matrix DOT export | Untouched (pyarchinit#663, Option A agreed with Emanuel): DOT + `graphviz` stay until a native replacement exists |
| 10 | EMStudio integration | Two stages: **B1** export `em.json` + open in EMStudio **desktop**; **B2** panel with the **web EMStudio served by the node**, pointed at the site's room, read-only, in a `QWebEngineView` (fallback: system browser) |
| 11 | Licensing boundary | EMStudio is GPL-3, the plugin GPL-2: never import or bundle EMStudio code into the plugin — separate process and HTTP only |
| 12 | Branch policy | Everything on `Stratigraph_00001`; `master` stays at 4.9.17 for fixes only |

## 3. Measured baseline (2026-10-07)

What the numbers say, so the plan stands on facts:

* **Swapping dev40 under the vendored bridge breaks 26 tests** (dev9
  baseline: 5 pre-existing failures). Breakage areas: localized SU/WSU rows
  no longer reach the graph (projector), `GraphIngestor` stops writing mapped
  columns back, group kinds and GraphML rendering differ, paradata edge
  resolution. The pin therefore stayed at dev9 (`requirements.txt`, rationale
  next to it; commit `bf16b3a9`).
* **Module drift, vendored vs library dev40** (diff lines):

  | fate | modules | drift |
  |------|---------|-------|
  | identical → delete, import from library | `yed_group_walker`, `yed_detector`, `vocab_types`, `vocab_provider_core`, `uuid7`, `ingest_result`, `group_store`, `conflict_resolver`, `_legacy_paradata_svgs`, `_db_handle` | 0 |
  | small drift → reconcile hunk by hunk | `yed_rapporti_policy` (3), `yed_classifier` (7), `yed_import_pipeline` (8), `paradata_store` (9), `edge_registry` (10), `group_projector` (10), `yed_table_parser` (11), `pyarchinit_pg_importer` (24), `_workspace` (26), `__init__` (56) | 3–56 |
  | real drift → parity tests | `graph_projector` (209), `graph_ingestor` (191) | 191–209 |
  | retires with the GraphML export | `graphml_writer` (78) | — |
  | stays ours (pyArchInit-specific) | `vocab_provider` (Qt wrapper), `continuity_generator`, `paradata_edge_resolver` + all Qt/DB-manager glue | — |

* `rapporti` moved to **`s3dgraphy.rapporti`** (core, no DB dependencies)
  since dev29; `s3dgraphy.sync.rapporti` is a compatibility re-export, so our
  imports keep resolving. Our vendored `rapporti.py` must be reconciled
  against `s3dgraphy/rapporti.py`, not against the 15-line shim.
* **Performance and em.json, verified on real data** (Al-Khutm, PG, 489 US →
  2,061 nodes / 3,514 edges): `PyArchInitImporter.parse()` 1.48 s (dev39) →
  **0.27 s** (dev40); `export_emjson` 0.15 s; read-back identical, 0
  warnings. File produced: `~/Downloads/Al-Khutm.em.json` (graph named after
  the site). Numbers posted on s3Dgraphy#27.
* **dev9 has no `emjson_exporter`** → em.json inside the plugin requires the
  migration; there is no shortcut.
* **GraphML exporter fails on NumPy ≥ 1.24** (`np.int`), dev39 and dev40
  alike — reported on #27. It does not touch the one-time yEd *import*.
* `set_kind` / `unit_code` calls are already in the bridge at the three node
  creation/enrichment sites, guarded, no-ops on dev9 (`bf16b3a9`);
  `tests/sync/test_usm_kind_dev40.py` arms itself when the pin moves.

## 4. Sub-project A — one bridge

**Goal:** the plugin imports `s3dgraphy.sync` from the library; the vendored
package reduces to `vocab_provider.py`, `continuity_generator.py`,
`paradata_edge_resolver.py` and the Qt/DB-manager glue.

Stages, each one releasable with a green suite on dev40:

* **A1 — free wins + vocabulary.** Bump the pin (exact version). Delete the
  10 identical modules; the vendored package's `__init__` re-exports from the
  library during the transition so callers keep working. Reconcile the
  small-drift modules hunk by hunk with a rule per hunk: *generic* → PR to
  s3dgraphy (Emanuel asked for exactly this); *pyArchInit-specific* → move
  into our extension modules; *stale* → adopt the library's line. Reconcile
  our `rapporti.py` against `s3dgraphy.rapporti`.
* **A2 — projector parity.** `graph_projector` moves to the library's, with
  our 209 delta lines triaged as in A1. Parity harness: for the sample DB and
  one real site, project with the vendored module and with the library's —
  same nodes, same edges, same attributes (allowing for `stratigraphic_kind`,
  which only the library knows). The localized SU/WSU regression and the
  epoch-name regression measured in §3 are the first acceptance tests. After
  A2, **B1 can ship**.
* **A3 — yEd one-time import on the library's ingestor.** `graph_ingestor`
  parity the same way; the "mapped column not updated" regression of §3 is
  the acceptance test. The yEd import dialogs stay ours and call the library
  pipeline.
* **A4 — retire our GraphML export** (runs only after B1 has shipped:
  the replacement viewer exists before the old export goes). Menu entries for the GraphML export
  with groups/swimlane are removed (the path becomes em.json); the ~20 tests
  of `test_groups_export_em_template.py`, `test_em_export_rendering.py`,
  `test_graph_projector_groups.py` and friends are retired with a written
  rationale in the changelog; `graphml_writer.py` and its vendored-only
  helpers are deleted. The classic DOT matrix is untouched (decision 9).
* **A5 — sweep.** Callers in `tabs/` and `modules/` import `s3dgraphy.sync`
  directly; the vendored re-export shim goes; `modules_installer` /
  `requirements.txt` install the new pin + `dtcstamp`; a source guard test
  asserts no plugin file imports `modules.s3dgraphy.sync` for the migrated
  modules.

**Acceptance for A:** suite green on dev40 (≤ the pre-existing failures,
retired tests excluded); yEd one-time import works on a real GraphML; the
`unita_tipo` vocabulary still comes from `VocabProvider`; the DOT matrix
unchanged.

## 5. Sub-project B — em.json and EMStudio

* **B1 (after A2).** Menu action «Esporta sito in em.json»: the library's
  canonical DB→graph path (`PyArchInitImporter` with
  `pyarchinit_us_mapping`, graph id = site name) + `export_emjson`, written
  to `pyarchinit_EM_folder`. Button «Apri in EMStudio»: hand the file to the
  installed desktop app (`open -a EMStudio` / `start` on Windows), fallback
  to a file-save dialog with a link to the EMStudio releases page. Validation
  per Emanuel: *if EMStudio reads it, the file is sound* — plus our own
  read-back check (`import_emjson`, 0 warnings) before handing it over.
* **B2 (needs a node).** A dock panel with `QWebEngineView` — the pattern
  with fallback already used in `tabs/Cantiere.py` — loading the web EMStudio
  **served by the StratiGraph node**, pointed at the site's room, read-only.
  No server binary is bundled (decision 11); QGIS builds without WebEngine
  fall back to the system browser.

**Acceptance for B1:** an exported real site opens in EMStudio desktop with
its epochs, qualia and relations visible; the read-back check reports 0
warnings.

## 6. Sub-project C — delivery to a room

* Port `room_client.py` from the StratiGraph fork of pyarchinit-mini
  (branch `stratigraph/09-client-stanza`) into
  `modules/s3dgraphy/room_client.py` — Emanuel: "the logic ports almost as
  is". It leans on **`s3dgraphy.contract`** (descriptor, handshake,
  `stable_id`, the write guard): nothing of that is rewritten.
* Semantics (decisions 5–8): `POST /v1/rooms/{id}/ops`, batches ≤1000,
  idempotent; `refused` inside a 200 reported, never retried; author = the
  authenticated caller; editor role required.
* **UI:** a «Consegna al nodo StratiGraph» action next to the em.json export;
  configuration (node URL, room id) in the configuration dialog; credentials
  via environment variables, following the WebDAV `ENV_NAMES` pattern — never
  in the repo or in `config.cfg` in clear.
* **Tests:** against a locally-run `stratigraph-server`; acceptance: first
  delivery writes the site's ops, the **second delivery returns all
  `refused` and changes nothing** (the idempotency promise, observable);
  authorship test: an author field smuggled into the payload does not reach
  the room.

## 7. Testing and release rhythm

One alpha release per stage — in order **A1, A2, B1, A3, A4, A5**, then
**B2** and **C** as the node arrives — each with: changelog entry
(IT+EN), the fate of every touched test written down, and the usual release
flow (tag, GitHub release, api-docs). The pin guard
(`test_usm_kind_dev40.py`) and the source guard of A5 keep the migration
honest. PG paths tested against `localhost:5433` as usual.

## 8. Risks

| Risk | Mitigation |
|------|------------|
| The library is a moving target (dev40 → devNN weekly) | Pin exact; re-measure the §3 baseline at the start of A1 against the then-current release; small PRs upstream instead of re-vendoring |
| Parity hides in attributes, not counts | Parity harness compares nodes, edges **and attributes**, not totals |
| `graph_projector`/`graph_ingestor` deltas carry undocumented fixes | Every delta hunk gets a fate (upstream / ours / drop) written in the PR description |
| A node is never provisioned | B stops at B1 (already useful), C stays verified against the local server |
| QGIS without QtWebEngine | B2 falls back to the system browser (pattern already in `Cantiere.py`) |
| GPL-2 / GPL-3 | Decision 11: process + HTTP boundary only |

## 9. Parked (explicitly out of this spec's work)

* em.json **import back** into the DB (returning edits made in EMStudio) —
  next brainstorming once B2 exists.
* The 990-US database of s3Dgraphy#27 — location unknown; numbers added to
  #27 when found.
* dtcstamp provenance for media and exports — mentioned by Emanuel, worth its
  own small design.
* RDF/CIDOC export menu action — trivial after A (library function), but out
  of scope here.
* The ICCD crosswalk (`us_table` ↔ `iccd-us-2021`) and Luca's involvement —
  Enzo answers Emanuel directly.
* pyarchinit-mini: out of the StratiGraph integration plan (Emanuel,
  2026-10-07); nothing in this spec targets mini.

## 10. Out of scope

Ports to `master`; the CRDT/WebSocket room (pyArchInit is an asynchronous
contributor by design); rewriting `s3dgraphy.contract` or the server;
EMStudio code inside the plugin.
