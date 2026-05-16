# yE-F Multi-Folder Paradata — Design Spec

**Date:** 2026-05-16
**Branch:** Stratigraph_00001
**Predecessor tag:** `yed-fastfix-5.8.5-alpha` (commit `a5e8502b`)
**Target tag:** `yed-f-multifolder-5.9.0-alpha`

---

## 1. Trigger and goal

### Bug report context

`yed-fastfix-5.8.5-alpha` shipped Bug R (B1 multi-row paradata) to restore multi-folder visibility lost in earlier dedup-by-identity behaviour. B1 creates N us_table rows per N yEd occurrences of a shared paradata label (`material`, `D.01`, `position`), with `us` suffix `_2`/`_3` and `d_stratigrafica` carrying the original label.

User accepted B1 as the immediate fix but explicitly requested yE-F as the proper design:

> "vai con B1 e poi progettiamo con C se B1 è veloce da fare"

B1 has three known costs:

1. **us_table cardinality inflated** — 3-5 rows per shared paradata label visible as `material_2`, `material_3` in pyArchInit form; look like duplicates to users.
2. **Identity dedup lost** — variants `D.001` / `D.001-2` / `D.001bis` no longer collapse into one record referencing multiple downstream extractors/combinars/properties (the original user requirement before B1).
3. **Cross-row consistency** — editing one `material` row leaves the other N-1 stale.

### Goal

Add a multi-folder mechanism that:

1. Stores **one us_table row per `(sito, d_stratigrafica, unita_tipo)`** for paradata kinds (DOC, Combinar, Extractor, property).
2. Tracks secondary folder memberships in a new `us_table.other_locations` TEXT column (JSON list of activity codes).
3. **Fan-out at export time**: emits N visual yEd `<node>` copies (one per location) with shared `pyarchinit.node_uuid` for round-trip identity.
4. **Folds at import time**: first occurrence becomes primary; subsequent ones append to `other_locations`.
5. **Coexists with B1**: existing multi-row data in `pyarchinit_test{002..010}.sqlite` (and similar) stays functional; yE-F applies to new imports only.
6. **Editable UI**: multi-select widget in Scheda US form for `other_locations`.
7. **Preserves AC-2** byte-identical regression for non-paradata data and for B1 legacy databases.

### Non-goals

See §13.

---

## 2. Decisions captured during brainstorming (2026-05-16)

| Dim | Question | Decision | Rationale |
|---|---|---|---|
| 1 | B1 → yE-F migration | **Coexist — B1 data untouched, yE-F applies to new imports** | Avoid invasive migration; users can opt-in via cleanup + re-import. |
| 2 | Schema shape for other_locations | **JSON list in `us_table.other_locations` TEXT** | Mirrors AI07 `s3d:other_locations` precedent; no JOIN; single ADD COLUMN migration. |
| 3 | Multi-folder dimension scope | **Activity only (MVP)** | Other dimensions (area, struttura, ...) remain single-value via existing columns; cross-dim deferred to yE-G. |
| 4 | Primary folder selection | **First-in-yEd-document-order** | Deterministic, stable across re-imports, trivial implementation. |
| 5 | Render fan-out at export | **N complete copies with per-folder edge resolution** | Visual coherence with INPUT yEd; preserves "DOC connected to its folder's extractors" UX from Bug R/T. |
| 6 | UI surface | **Full editable multi-select widget** | User can manage memberships post-import; re-import overwrites (yEd is source of truth). |

---

## 3. Architecture overview

yE-F adds three additions to the existing yE-D / yE-fastfix pipeline:

1. **Schema**: `us_table.other_locations TEXT DEFAULT NULL` (idempotent ADD COLUMN, migration script).
2. **Import fold** in `_write_us_rows`: replaces the Bug R no-dedup branch for paradata kinds with a fold-by-label branch that maintains primary + secondary structure.
3. **Export fan-out** in `graphml_writer`: new `_apply_yef_fan_out` step between projector enrichment and graphml emission; emits N visual copies, each carrying the canonical `pyarchinit.node_uuid`.

Detection: rows with `other_locations` non-empty are yE-F; rows with NULL `other_locations` are either single-folder (no membership multi-) or B1 legacy (multi-row). The export side treats both correctly: fan-out only for yE-F rows.

Round-trip identity: yEd `<node>` copies share the canonical `pyarchinit.node_uuid` data key. On re-import via yEd-from-pyarchinit-export, the classifier groups by this UUID and re-folds to one us_table row + N locations. For raw yEd graphmls (no pyarchinit data keys), fold-by-label provides the same outcome.

```
yEd graphml (input)
  │
  ▼
yE-B classifier ──► yE-C parsers ──► yE-D fold (NEW yE-F branch)
  │                                       │
  │                                       ▼
  │                            us_table row primary + other_locations
  │
  ▼
DB (yE-F + B1 legacy coexist)
  │
  ▼
GraphProjector ──► _apply_yef_fan_out (NEW) ──► graph w/ N copies
                                                       │
                                                       ▼
                                         GraphMLExporter ──► graphml output
                                              + per-folder edge resolution
```

---

## 4. Data model

### 4.1 Schema

```sql
ALTER TABLE us_table ADD COLUMN other_locations TEXT DEFAULT NULL;
```

Idempotent via `_columns_of(handle, "us_table")` pre-check. Works for SQLite + PG transparently (`DbHandle` shim, Foundation 5.6.2-alpha).

### 4.2 Field convention

Value is a JSON-encoded **list of strings**, each an activity code matching `us_table.attivita` semantic:

```python
# Examples (after fresh import of EM_demo_02.graphml on a clean DB):
us_table row for 'material':
    us='material', unita_tipo='property',
    attivita='VA01',
    other_locations='["VA04","VA05"]'

us_table row for 'D.01':
    us='01', unita_tipo='DOC',
    attivita='VA02',
    other_locations='["VA01","VA03","VA04","VA05"]'
```

`other_locations` MUST NOT include the primary (`attivita`). Empty list `'[]'` is equivalent to NULL — both signal "single-folder paradata".

### 4.3 ORM update

`modules/db/structures/us_table.py`:

```python
Column('other_locations', Text),  # 65 — yE-F multi-folder paradata
```

Appended after the existing 64 columns to preserve positional layouts.

### 4.4 Validation invariants

- Valid JSON list of strings (server-side check in `_write_us_rows`).
- No duplicates within the list.
- Primary value not present in the list.
- Activity codes are case-sensitive (`VA01` ≠ `va01`).
- NULL is legal and equivalent to single-folder.

---

## 5. Import fold logic

### 5.1 yE-F branch in `_write_us_rows`

Replaces the Bug R `_PARADATA_NODEDUP_UTS` no-dedup branch with a fold-by-label branch:

```python
paradata_primary_by_label: dict[tuple[str, str], tuple[str, str, list[str]]] = {}
# (d_stratigrafica, unita_tipo) → (node_uuid, primary_us, list_of_secondary_locations)

# Pre-load existing yE-F rows for idempotency:
for r in conn.execute(text(
    "SELECT us, unita_tipo, node_uuid, d_stratigrafica, attivita, other_locations "
    "FROM us_table WHERE sito = :s AND unita_tipo IN (...)"
)):
    secondary = json.loads(r.other_locations or "[]") or []
    paradata_primary_by_label[(r.d_stratigrafica, r.unita_tipo)] = (
        r.node_uuid, r.us, secondary,
    )

# Process each yEd paradata leaf:
for c in sql_us_classified:
    if c.user_kind in {DOCUMENT, COMBINER, EXTRACTOR, PROPERTY}:
        label_key = (c.label, unita_tipo)
        current_folder = _resolve_folder_for_leaf(c.yed_id, folders)
        existing = paradata_primary_by_label.get(label_key)
        if existing is None:
            # Primary INSERT
            node_uuid = uuid7().hex
            us_value = _strip_unita_tipo_prefix(c.label, unita_tipo)
            conn.execute(text(
                "INSERT INTO us_table (sito, area, us, unita_tipo, node_uuid, "
                "periodo_iniziale, fase_iniziale, periodo_finale, fase_finale, "
                "d_stratigrafica, attivita, other_locations) "
                "VALUES (:sito, '1', :us, :ut, :nu, :pi, :fi, :pf, :ff, "
                ":d_strat, :attivita, NULL)"
            ), {...})
            paradata_primary_by_label[label_key] = (node_uuid, us_value, [])
            uuid_map[c.yed_id] = node_uuid
        else:
            # Secondary occurrence — append folder to other_locations
            primary_uuid, primary_us, secondary = existing
            if current_folder and current_folder not in secondary \
                    and current_folder != _read_primary_folder(...):
                secondary.append(current_folder)
                conn.execute(text(
                    "UPDATE us_table SET other_locations = :ol "
                    "WHERE sito = :s AND node_uuid = :nu"
                ), {"ol": json.dumps(secondary), ...})
            uuid_map[c.yed_id] = primary_uuid
        if us_by_yed_id_out is not None:
            us_by_yed_id_out[c.yed_id] = primary_us
        continue
```

### 5.2 Helper: `_resolve_folder_for_leaf`

New helper in `yed_import_pipeline.py`:

```python
def _resolve_folder_for_leaf(yed_id: str, folders: list[FolderCandidate]) -> str | None:
    """Return the activity code of the folder containing `yed_id`, or None.

    Iterates folders; the FIRST folder with `auto_dimension == "attivita"`
    whose `member_yed_ids` contains `yed_id` wins. Nested folders are
    walked recursively via `_flatten_members` (Bug F precedent).
    """
    for folder in folders:
        if (folder.user_dimension or folder.auto_dimension) != "attivita":
            continue
        members = _flatten_members(folder, folders)
        if yed_id in members:
            return folder.user_value or folder.auto_value
    return None
```

### 5.3 Idempotency

Pre-loaded `paradata_primary_by_label` from DB ensures re-imports of the same yEd graphml:
- Do not duplicate primary rows.
- Append new folder occurrences to `other_locations` if user added a new folder reference in yEd.
- Are no-ops if no yEd changes occurred since previous import.

### 5.4 uuid_map and rapporti

All yed_ids sharing a paradata label map to the same canonical `node_uuid` via `uuid_map`. Rapporti targets are resolved via Bug S `us_by_yed_id_out` to the primary `us` value (no suffix). Bug T reciprocal rapporti unchanged.

---

## 6. Export fan-out logic

### 6.1 New step: `_apply_yef_fan_out`

Inserted in `graphml_writer.export_graphml` after `GraphProjector.populate_graph` (which runs `_propagate_node_uuid_and_us` and `_enrich_into`) and BEFORE the GraphMLExporter pass.

```python
def _apply_yef_fan_out(graph) -> None:
    """For each StratigraphicUnit-class node with non-empty
    attributes['other_locations'], emit N-1 visual copies (one per
    secondary location). Each copy:
      - Shares node.name (label rendered in yEd)
      - Has fresh node_id `<primary_uuid>_loc_<idx>`
      - Carries canonical pyarchinit.node_uuid via attributes['node_uuid']
      - attributes['attivita'] = the location code of this copy
      - attributes['_yef_canonical_uuid'] = primary node_uuid (for
        downstream edge resolver)

    Result: graph has 1 + len(other_locations) visual nodes per yE-F
    paradata row. Stratigraphic and B1 legacy rows untouched.

    Stashes graph.attributes['_yef_copies_by_canonical'] = dict mapping
    canonical_uuid → list of copy nodes, for the per-folder edge
    resolver (§7).
    """
    import json
    canonical_to_copies: dict[str, list] = {}
    for n in list(graph.nodes):
        attrs = getattr(n, "attributes", None) or {}
        ol_raw = attrs.get("other_locations")
        if not ol_raw:
            continue
        try:
            secondary_locs = json.loads(ol_raw) or []
        except (ValueError, TypeError):
            continue
        if not secondary_locs:
            continue
        primary_uuid = n.node_id
        canonical_to_copies[primary_uuid] = [n]
        attrs["_yef_canonical_uuid"] = primary_uuid
        for idx, loc in enumerate(secondary_locs, start=1):
            copy = _clone_node_for_location(n, loc, idx, primary_uuid)
            graph.add_node(copy)
            canonical_to_copies[primary_uuid].append(copy)
    graph.attributes = getattr(graph, "attributes", None) or {}
    graph.attributes["_yef_copies_by_canonical"] = canonical_to_copies
```

### 6.2 Helper: `_clone_node_for_location`

```python
def _clone_node_for_location(primary_node, location: str, idx: int,
                              canonical_uuid: str):
    """Create a copy of `primary_node` placed in `location` folder.

    The copy is a fresh s3dgraphy node instance with:
      - node_id = f"{canonical_uuid}_loc_{idx}" (unique within graph)
      - name = primary_node.name (same yEd label rendered)
      - description = primary_node.description (idem)
      - Same Python class as primary_node (StratigraphicUnit subclass
        carrying its unita_tipo attribute).
    Then a deep copy of primary_node.attributes is taken, overridden
    with: attivita=location, _yef_canonical_uuid=canonical_uuid,
    _yef_is_copy=True, node_uuid=canonical_uuid (round-trip identity).
    """
    ...
```

### 6.3 yEd output structure

Per row `('material', primary='VA01', other=['VA04','VA05'])`:

```xml
<node id="<canonical_uuid>">                      <!-- primary in VA01 -->
  <data key="d8">test</data>                      <!-- pyarchinit.sito -->
  <data key="d9">property</data>                  <!-- pyarchinit.unita_tipo -->
  <data key="d16"><canonical_uuid></data>         <!-- pyarchinit.node_uuid -->
  <data key="d18">VA01</data>                     <!-- pyarchinit.attivita -->
  ...
</node>
<node id="<canonical_uuid>_loc_1">                <!-- copy in VA04 -->
  <data key="d9">property</data>
  <data key="d16"><canonical_uuid></data>         <!-- SAME canonical -->
  <data key="d18">VA04</data>
  ...
</node>
<node id="<canonical_uuid>_loc_2">                <!-- copy in VA05 -->
  ...
</node>
```

All 3 nodes parent to their respective yEd swimlane folder via the existing `_inject_group_folders` mechanism (AI06/AI07 lineage), which already keys folder parent on `attributes['attivita']`.

---

## 7. Per-folder edge resolution

### 7.1 Problem

A row `Extractor 01.11` (in folder VA04) carries rapporto `[">>", "01", "1", "test"]` pointing to canonical DOC `us='01'`. With fan-out, DOC has 3+ visual copies (one per folder). The edge must target the COPY IN VA04, not the primary in VA01 — otherwise the visual matches against EM_demo_02 INPUT show DOC isolated in its folder (regression of Bug T fix).

### 7.2 Resolver

In `graph_projector._enrich_into` (rapporti edges loop), when computing edge `source → target`:

```python
def _resolve_target_for_folder(target_canonical_node, source_folder, graph):
    """Find the copy of target_canonical_node whose attivita == source_folder.

    If target has no copies (single-folder paradata or non-paradata),
    return target_canonical_node directly. If a matching copy doesn't
    exist (target's folder set doesn't include source_folder), fall
    back to the primary (target_canonical_node).
    """
    copies = graph.attributes.get(
        "_yef_copies_by_canonical", {}
    ).get(target_canonical_node.node_id)
    if not copies:
        return target_canonical_node
    for c in copies:
        cattrs = getattr(c, "attributes", None) or {}
        if cattrs.get("attivita") == source_folder:
            return c
    return target_canonical_node
```

Integration point in `_enrich_into` rapporti loop (replacing current resolver):

```python
src_folder = (us_node.attributes or {}).get("attivita")
target_canonical = nodes_by_us_ut.get((target_us, target_ut))
if target_canonical is not None:
    target_node = _resolve_target_for_folder(target_canonical, src_folder, graph)
```

### 7.3 Cross-folder fallback semantics

When a source's folder doesn't appear in target's `other_locations`, the resolver falls back to the primary copy. Visual outcome: edge crosses folder boundaries. Acceptable interpretation: "Extractor in VA07 cites a Document hosted in VA01 (not also in VA07)".

---

## 8. Round-trip identity

### 8.1 Forward (yEd → DB)

Both for fresh raw yEd graphmls and for re-imports of pyarchinit-exported graphmls:

1. Classifier identifies paradata leaves (Bug I BPMN-aware).
2. `_write_us_rows` folds by `(d_stratigrafica, unita_tipo)` per §5.
3. Resulting us_table has 1 row per identity with primary + N secondaries.

### 8.2 Re-export (DB → yEd)

1. `GraphProjector.populate_graph` reads DB; row attributes include `other_locations`.
2. `_apply_yef_fan_out` emits N visual copies sharing canonical `pyarchinit.node_uuid`.
3. Per-folder edge resolver routes rapporti to the right copy.

### 8.3 Re-import (pyarchinit-export → DB)

1. yEd file has N `<node>` entries with the SAME `pyarchinit.node_uuid` data key.
2. Classifier identifies them by label (yE-D path).
3. Fold logic in `_write_us_rows`:
   - If `pyarchinit.node_uuid` is present, GROUP by `(d_stratigrafica, unita_tipo, pyarchinit.node_uuid)` and reuse the existing row (idempotent UPSERT).
   - Otherwise fold by `(d_stratigrafica, unita_tipo)` only (raw yEd path).
4. Result: cardinality preserved across round-trips.

### 8.4 Identity invariant

`(sito, d_stratigrafica, unita_tipo)` is a de-facto unique key for yE-F paradata rows. The us_table UNIQUE constraint `(sito, area, us, unita_tipo)` remains unchanged — primary `us` is the stripped label without suffix (`'material'`, `'01'`), and a single row per identity satisfies the UNIQUE naturally.

---

## 9. UI surface

### 9.1 Widget

`QListWidget` with `selectionMode = MultiSelection`, placed in `gui/ui/US_USM.ui` (and equivalent forms) below the existing `attivita` combobox.

### 9.2 Populate

On Scheda US load, query distinct activity codes for the current sito:

```sql
SELECT DISTINCT attivita FROM us_table
WHERE sito = ? AND attivita IS NOT NULL AND attivita != ''
ORDER BY attivita;
```

Populate the list widget. Pre-select items present in the row's `other_locations`.

### 9.3 Save

On `pushButton_save` click handler (`tabs/US_USM.py`):

```python
selected = [item.text() for item in
            self.listWidget_other_locations.selectedItems()]
# Strip primary (attivita) if user accidentally selected it
selected = [s for s in selected if s != current_attivita]
other_locations = json.dumps(selected) if selected else None
# Save into us_table.other_locations via the existing UPDATE path
```

### 9.4 Hide for non-paradata

In `tabs/US_USM.py` `on_unita_tipo_changed`:

```python
is_paradata = unita_tipo in ("DOC", "Combinar", "Extractor", "property")
self.listWidget_other_locations.setVisible(is_paradata)
self.label_other_locations.setVisible(is_paradata)
```

### 9.5 Localization

Add translation entry "Other locations" in `modules/utility/pyarchinit_i18n_stratigraphic.py` for 10 languages (it/en/de/es/fr/ar/ca/ro/pt/el). Default Italian: "Altre attività".

### 9.6 Validation

- Tooltip: "Le attività primarie e secondarie devono esistere come record us_table per il sito corrente. Re-importare dal yEd se non presenti."
- Save button disabled if JSON validation fails (defensive — UI builds valid lists by construction).
- No conflict detection between manual edits and pending re-imports — yEd is source of truth; re-import overwrites.

---

## 10. Coexistence with B1

### 10.1 Detection at read time

A us_table row is **yE-F** iff `other_locations` is non-null and non-empty (parsed as a list with ≥1 element). Otherwise it is treated as **B1 legacy** or **single-folder** (indistinguishable, same behaviour).

### 10.2 Reader rules

`graph_projector.populate_graph` + `graphml_writer.export_graphml`:
- For yE-F rows: apply `_apply_yef_fan_out` → N visual copies.
- For B1 multi-row data: each row produces 1 visual copy (current 5.8.5-alpha behaviour). The N rows with synthesised `us_2`/`us_3` values continue to render N separate visual nodes correctly — Bug S rapporti targets still resolve per-row.

Detection branches on `other_locations` per-row in the same pass.

### 10.3 Writer rules

`_write_us_rows` always writes yE-F shape for new imports. The Bug R no-dedup branch is REPLACED by §5 fold. B1 data already in the DB remains untouched — only new imports of the same yEd graphml (after `DELETE FROM us_table WHERE sito = '<test>'`) produce yE-F shape.

### 10.4 Migration script (deferred)

`scripts/migrations/2026_05_yef_collapse_b1.py` (out-of-scope MVP, deferred):
- For each `(sito, d_stratigrafica, unita_tipo)` with N > 1 rows in B1 shape, collapse to 1 row + N-1 other_locations entries.
- Rewrite rapporti targets in other rows to point to the surviving primary.
- Opt-in CLI; not auto-applied; not blocking yE-F rollout.

---

## 11. Schema migration

### 11.1 Library function

`scripts/migrations/2026_05_yef_other_locations_lib.py`:

```python
def add_other_locations_column(handle: DbHandle) -> int:
    """Idempotent ADD COLUMN for us_table.other_locations.

    Returns 1 if column added, 0 if already present.
    Backs up the DB pre-migration (SQLite copy / PG pg_dump).
    """
    cols = _columns_of(handle, "us_table")
    if "other_locations" in cols:
        return 0
    _backup_db(handle)
    with handle.engine.begin() as conn:
        conn.execute(text("ALTER TABLE us_table ADD COLUMN other_locations TEXT"))
    return 1
```

### 11.2 CLI

```bash
python scripts/migrations/2026_05_yef_other_locations.py --apply --db <sqlite_path>
python scripts/migrations/2026_05_yef_other_locations.py --apply --conn-str <pg_uri>
```

Mirrors the Bug PG-A `node_uuid` migration script signature.

### 11.3 QGIS menu entry

`pyarchinitPlugin.py`: add menu item `Plugins → pyArchInit → Migrazioni → Aggiungi colonna other_locations (yE-F)` invoking `_run_yef_migration` handler. Mirror of `_run_uuid_backfill_migration`.

### 11.4 ORM update

`modules/db/structures/us_table.py`:

```python
Column('other_locations', Text),  # 65 — yE-F multi-folder paradata (yed-f-multifolder-5.9.0-alpha)
```

### 11.5 Backward compat

Pre-migration DBs lack the column; the reader handles missing column gracefully (try/except in `_propagate_node_uuid_and_us` SELECT). yE-F is a no-op until the migration is applied.

---

## 12. Test plan

### 12.1 New tests in `tests/sync/test_yed_import_pipeline.py`

- `test_write_us_rows_yef_fold_first_occurrence_primary` — 3 yEd `material` leaves in VA01/VA04/VA05 → 1 row primary VA01 + `other_locations=["VA04","VA05"]`.
- `test_write_us_rows_yef_idempotent_on_re_import` — second run of same drafts → 0 inserts, same `other_locations` payload.
- `test_write_us_rows_yef_appends_new_folder_on_re_import` — re-import with extra VA06 occurrence → `other_locations=["VA04","VA05","VA06"]`.
- `test_b1_legacy_rows_untouched_during_yef_import` — DB pre-populated with B1 multi-row → yE-F fresh import to a different sito leaves B1 sito untouched.
- `test_yef_no_dedup_for_stratigraphic_kinds` — US/USM/USV/SF/VSF/RSF unchanged (still dedup-by-identity).
- `test_resolve_folder_for_leaf` — helper unit test (basic, nested folder, missing leaf, non-attivita dim).

### 12.2 New tests in `tests/sync/test_graphml_writer_helpers.py`

- `test_yef_fan_out_creates_n_copies` — row with `other_locations=["VA04"]` → 2 nodes in graph after fan-out, both with same canonical UUID.
- `test_yef_fan_out_skipped_for_non_paradata` — row US (no other_locations) → 1 node.
- `test_yef_target_resolver_picks_same_folder_copy` — source in VA04 + rapporto to canonical DOC → resolver returns the VA04 copy.
- `test_yef_target_resolver_fallback_to_primary` — source in VA99 (no match) → resolver returns primary.
- `test_yef_copies_share_pyarchinit_node_uuid` — all N copies emit same `pyarchinit.node_uuid` data key in graphml output.

### 12.3 New tests in `tests/sync/test_graph_projector_yef.py` (new file)

- `test_projector_reads_other_locations_into_attrs` — row in DB with `other_locations='["VA04"]'` → `node.attributes['other_locations'] = '["VA04"]'` after projection.
- `test_projector_yef_writes_fan_out_marker` — `graph.attributes['_yef_copies_by_canonical']` populated.

### 12.4 Round-trip integration

- `test_yef_round_trip_em_demo_02` — fresh import of EM_demo_02.graphml → us_table primaries + other_locations populated → re-export → re-import (same yEd file) → identical DB state (idempotent cardinality, idempotent `other_locations`).

### 12.5 Update existing tests

- `test_write_us_rows_paradata_no_dedup_one_row_per_occurrence` (Bug R) — convert to:
  - `test_write_us_rows_paradata_yef_fold_one_row_n_locations` with new assertion shape.
- `test_yed_d_end_to_end_*` integration tests — adjust counts (5 us_table rows + 1 row per shared paradata label, with N-1 secondaries in other_locations instead of N rows).

### 12.6 Target test count

329 → ~340 (+11 net):
- +7 new tests
- +4 updated tests (rename/adjust assertions)
- 0 deletions

AC-2 regression suite (byte-identical export of `mini_volterra.sqlite`, no paradata multi-folder) remains green.

---

## 13. Non-goals

Out of yE-F MVP scope, deferred to future milestones:

- **Multi-dimension other_locations** (yE-G): paradata referenced cross-dimension (folder VA01 + area AR05 + struttura ST10). Requires per-dim dict schema instead of flat list.
- **B1 → yE-F automatic migration script**: opt-in standalone CLI, separate work, not blocking yE-F rollout.
- **Folder description preservation**: `VA02-foundation of the staircase` currently truncated to `VA02` in `us_table.attivita`. Future enhancement could add `attivita_descrizione` column or extend `periodizzazione_table`.
- **Stratigraphic multi-membership**: US/USM/USV records sharing the same `us` value across activities is structurally rare. Bug R B1 multi-row remains the answer if encountered; no yE-F treatment planned.
- **EM 1.5 ParadataNodeGroup rendering as wrapper**: yE-F row-paradata flow through the swimlane Stratigraphic path (Bug P). `_inject_isolated_paradata_nodes` remains scoped to Author/License/Embargo. Future design could unify ParadataNodeGroup wrapping for visual clustering.
- **CIDOC-CRM serialization of multi-folder paradata**: graph_ingestor + CIDOC mapper propagation of `other_locations` to RDF. Future task if RDF interop becomes a requirement.

---

## 14. Acceptance criteria

**AC-1**: Fresh import of `EM_demo_02.graphml` into an empty DB produces:
- 1 `us_table` row per `(d_stratigrafica, unita_tipo)` for paradata kinds.
- Cardinality summary: 3 DOC + 3 Combinar + 28 Extractor + 7 property + 4 US + 8 USV + 2 SF + 2 VSF = **57 row total** (= identity-dedup count of EM_demo_02).
- `material` row has `attivita='VA01'` + `other_locations` listing 4 other folders (VA02..VA06 minus VA01, depending on which folders reference it).

**AC-2 (regression)**: AC-2 byte-identical export of `mini_volterra.sqlite` (no multi-folder paradata) remains green. Diff against baseline = 0 bytes.

**AC-3**: Re-export of an EM_demo_02 fresh import yields graphml with N visual copies per paradata identity:
- 3 `<node>` for `material` (VA01 + VA04 + VA05 copies) sharing `pyarchinit.node_uuid`.
- 5 `<node>` for `D.01` (across its 5 folders) sharing UUID.
- Edges resolve per-folder via §7.

**AC-4 (round-trip)**: Re-import of the re-exported graphml back into a fresh DB produces the same us_table state (cardinality + other_locations content) as the original AC-1 import.

**AC-5 (idempotency)**: Re-import of the SAME yEd graphml into a DB that already has yE-F rows for that sito yields:
- 0 new INSERTs.
- 0 changes to `other_locations` (deep-equal).

**AC-6 (coexist with B1)**: A DB pre-populated with B1 multi-row data (e.g., `pyarchinit_test008.sqlite`) remains functional in pyArchInit after yE-F migration is applied. Reading B1 sito produces correct rendering; writing yE-F to a different sito doesn't affect B1 sito.

**AC-7 (UI)**: Scheda US form for a row with `unita_tipo='property'` shows the `other_locations` widget populated from DB; user can add/remove activities; save updates DB.

**AC-8 (test suite)**: pytest passes 340+ tests / 0 failures.

---

## 15. Implementation milestones

To be detailed by `writing-plans` skill in the next stage. Rough sketch:

1. **yE-F-A — Schema migration**: ADD COLUMN, lib + CLI + menu, ORM update, tests. ~½ day.
2. **yE-F-B — Import fold**: rewrite `_write_us_rows` paradata branch, helper `_resolve_folder_for_leaf`, idempotency pre-load, tests. ~1 day.
3. **yE-F-C — Export fan-out**: `_apply_yef_fan_out`, `_clone_node_for_location`, integration in `export_graphml`, tests. ~1 day.
4. **yE-F-D — Per-folder edge resolver**: `_resolve_target_for_folder`, integrate in `_enrich_into`, tests. ~½ day.
5. **yE-F-E — UI widget**: Qt Designer `.ui` edit, Python handler, i18n in 10 langs, tests. ~½ day.
6. **yE-F-Closure**: round-trip integration test, AC-2 baseline check, dev-log + tutorial + api-docs entries, tag `yed-f-multifolder-5.9.0-alpha`. ~½ day.

Total estimate: **4 days** focused work. Subject to refinement at planning stage.
