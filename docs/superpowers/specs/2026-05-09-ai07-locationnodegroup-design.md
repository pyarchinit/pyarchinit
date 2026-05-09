# AI07 — `LocationNodeGroup` migration + AI08-F1 m:n hierarchical nesting

**Status**: design approved (2026-05-09)
**Predecessor**: `phase2-ai08f2-hotfix-5.5.2-alpha` (`b569bd51`)
**Target tag**: `phase2-ai07-locationnodegroup-5.6.0-alpha`
**Upstream dependency**: s3dgraphy 0.1.41 (shipped 2026-05-09 — datamodel 1.5.5)
**Parent**: [`docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md`](./2026-05-04-s3dgraphy-bidirectional-sync-design.md)
**Resolved upstream issue**: [`zalmoxes-laran/s3Dgraphy#5`](https://github.com/zalmoxes-laran/s3Dgraphy/issues/5)

## 1. Goal

Migrate pyarchinit's spatial node-grouping representation from the AI06
single-class design (`ActivityNodeGroup` + `group_kind` discriminator) to
the s3dgraphy 0.1.41 native model (`LocationNodeGroup` + `kind` enum),
introducing **many-to-many membership** with `is_primary` disambiguation,
**recursive Location-in-Location hierarchy** (toponym chain), and
**transparent on-read up-conversion** of legacy 5.5.x exports.

This spec fuses the original AI07 (semantic-cleanup) and AI08-F1
(hierarchical nesting) tracks into a single Group, motivated by:

- AI07 alone modifies the same `_merge_groups` and
  `_inject_group_folders` functions that F1 needs to extend
- 0.1.41 ships `is_primary` and recursive support together — splitting
  them into two releases would mean shipping AI07 with the m:n shape but
  no consumer of it
- The 5.5.2-alpha "single-dimension only" warning workaround is removed
  by F1 — no point keeping it after AI07 lands

## 2. Background

### 2.1 What 0.1.41 brings

- **`LocationNodeGroup(node_id, name, kind, ...)`** — `kind ∈ {toponym,
  study, functional}`, `propagation = "additive"` (asymmetry with epoch's
  finest-wins propagation)
- **`is_in_location` edge type** with dual CIDOC mapping: `P53 has former
  or current location` for node→location, `P89 falls within` for the
  recursive location→location hierarchy
- **Optional `is_primary: true` attribute** on at most one
  `is_in_location` edge per source node — disambiguates which membership
  is rendered as a yEd group folder when m:n
- **`ActivityNodeGroup` retained** (NOT deprecated). Continues to handle
  intentional/historical activities (e.g. recording phases of work)
- **`em_visual_rules.json` 1.5.1**: dashed round-rectangle for
  `LocationNodeGroup`, kind-keyed border colour, `primary_modifier` style
  on `is_in_location`

### 2.2 What pyarchinit ships today (5.5.2-alpha)

- All 7 grouping dimensions emit `ActivityNodeGroup` nodes via
  `_merge_groups` (`graph_projector.py:642`)
- All edges are `is_in_activity`
- `group_kind` attribute carries the dimension discriminator
- Round-trip preserved via `<data key="pyarchinit.<kind>">` data entries
  on group folders
- Multi-dim export blocked by warning at
  `s3dgraphy_dot_bridge.py:587` (workaround from `5.5.2-alpha` hotfix)

### 2.3 Decisions from upstream issue #5 (Emanuel, 2026-05-09)

- **Q1 (`attivita` migration target)**: stays as `ActivityNodeGroup`.
  `attivita` reads as historical intentional activity, not spatial
- **Q2 (legacy 5.5.x file handling)**: 0.1.41 reader treats them as
  opaque `ActivityNodeGroup + group_kind` metadata — **NO automatic type
  promotion in the library**. Up-conversion lives in pyarchinit's
  projector code path
- **Multi-projection georef**: paritary siblings (multiple `P161`),
  no canonical-vs-alternate split
- **Toponym chain from `site_table`**: endorsed; pyarchinit emits one
  `LocationNodeGroup(kind="toponym")` per non-empty admin level

### 2.4 Internal pyarchinit decisions (this brainstorm session)

- **Up-conversion strategy**: option (a) on-read auto-promote with
  `DeprecationWarning` log line (NOT explicit migration script)
- **Scope**: option (b) AI07 + F1 fused in a single release
- **Primary selection**: option (c) hardcoded dimension priority order
  with override combobox in the export dialog
- **Toponym empty levels**: option (c) skip empty levels, compact the
  chain; emit nothing if all 4 admin levels are empty
- **Cross-site toponym dedupe**: enabled — `(name, kind)` pair maps to a
  deterministic `group_uuid` (sha1) so 2 sites in the same comune share
  the node

## 3. Architecture

### 3.1 High-level flow

```
                 SQL                                             yEd GraphML
                  │                                                    │
        ┌─────────▼──────────┐                       ┌────────────────▼──────────────┐
        │  GraphProjector    │                       │  GraphIngestor                │
        │  ._merge_groups    │  ─── export ────►    │  ._apply_group_folders_to_sql │
        │                    │                       │  (recursive walker)           │
        │  switch by kind:   │  ◄─── re-import ───   │                               │
        │   spatial→Location │                       │  on-read auto-promote:        │
        │   attivita→Activity│                       │   ActivityNG+group_kind       │
        │  + toponym chain   │                       │   → LocationNG+kind           │
        └────────────────────┘                       └───────────────────────────────┘
```

### 3.2 Three invariants

1. **Toponym chain**: derived from
   `site_table.{nazione,regione,provincia,comune}`. Always secondary
   relative to US (toponyms NEVER win primary). Deduplicated by
   `(name, kind)` cross-site
2. **Primary selection**: hardcoded order
   `struttura > attivita > area > settore > ambient > saggio > quad_par`,
   override available via combobox in the export dialog. Toponym is
   never in the priority list
3. **Backward compat 5.5.x**: projector intercepts
   `ActivityNodeGroup + group_kind ∈ {area,struttura,settore,ambient,saggio,quad_par}`
   on read and promotes in-memory to `LocationNodeGroup + kind`. Single
   `DeprecationWarning` per call

## 4. Mapping table

| pyarchinit dimension | s3dgraphy class | `kind` | edge type | example |
|---|---|---|---|---|
| `struttura` | `LocationNodeGroup` | `functional` | `is_in_location` | "Basilica" |
| `ambient` | `LocationNodeGroup` | `functional` | `is_in_location` | "Cubicolo III" |
| `area` | `LocationNodeGroup` | `study` | `is_in_location` | "A", "B" |
| `settore` | `LocationNodeGroup` | `study` | `is_in_location` | "Settore N" |
| `saggio` | `LocationNodeGroup` | `study` | `is_in_location` | "Saggio I" |
| `quad_par` | `LocationNodeGroup` | `study` | `is_in_location` | "Q4-A2" |
| **`attivita`** | **`ActivityNodeGroup`** (unchanged) | (none) | `is_in_activity` | "Strato di abbandono" |
| `nazione/regione/provincia/comune` | `LocationNodeGroup` | `toponym` | `is_in_location` | recursive chain |
| `adhoc` | `LocationNodeGroup` | `functional` (default) | `is_in_location` | user-defined in GroupStore |

## 5. Data flow

### 5.1 Export (SQL → s3dgraphy.Graph → GraphML)

```
GraphProjector.populate_graph(db_path, sito, primary_priority=DEFAULT)
 │
 ├─ Stage 1: read us_table rows, create StratigraphicNode for each
 ├─ Stage 2a: build EpochNodes from periodizzazione_table
 ├─ Stage 2b: _propagate_node_uuid_and_us
 │
 ├─ Stage 3 (NEW): _emit_toponym_chain(db_path, sito)
 │   ├─ SELECT nazione, regione, provincia, comune FROM site_table WHERE sito=?
 │   ├─ filter empty levels
 │   ├─ for each (level, value), get-or-create LocationNodeGroup(kind="toponym")
 │   │   keyed by sha1((value, "toponym")) — deterministic, cross-site dedupe
 │   ├─ chain: each level → next via is_in_location (recursive)
 │   └─ each US: is_in_location to deepest level (always is_primary=false)
 │
 ├─ Stage 4 (REWORKED): _merge_groups(graph, db_path, sito, dimensions, primary_priority)
 │   ├─ build_groups_from_sql(db_path, sito, sql_dims)  # same as AI06
 │   ├─ for each GroupSpec:
 │   │   ├─ node_class = ActivityNodeGroup if group_kind=="attivita"
 │   │   │              else LocationNodeGroup
 │   │   ├─ kind = {struttura,ambient}→functional / {area,settore,saggio,quad_par}→study
 │   │   │        / "attivita"→None / "adhoc"→functional
 │   │   ├─ edge_type = "is_in_activity" if node_class==ActivityNodeGroup
 │   │   │             else "is_in_location"
 │   │   └─ for each US member:
 │   │       ├─ is_primary = compute_primary(us, primary_priority, all_us_memberships)
 │   │       └─ add_edge(src=us, tgt=group, type=edge_type,
 │   │                  attrs={is_primary: bool})
 │   └─ at most ONE is_primary=true per US
 │
 └─ return graph
```

### 5.2 Re-import (GraphML → SQL)

#### Constants used below

```python
# us_table columns that map 1:1 to a SQL-backed group_kind. Inherits
# AI06's _GROUP_KIND_TO_COL set verbatim (graph_ingestor.py:572).
SQL_BACKED_KINDS = frozenset({
    "area", "struttura", "attivita",
    "settore", "ambient", "saggio", "quad_par",
})

# Subset of SQL_BACKED_KINDS that AI07 promotes from
# ActivityNodeGroup → LocationNodeGroup. EXCLUDES "attivita" (stays as
# ActivityNodeGroup per Emanuel's Q1 decision).
SQL_BACKED_KINDS_SPATIAL = SQL_BACKED_KINDS - {"attivita"}
```

#### Flow

```
GraphIngestor.populate_list(db_path, sito, graphml_path, update_sql_on_import)
 │
 ├─ stage A: parse GraphML → s3dgraphy.Graph (existing — uses 0.1.41 reader)
 │
 ├─ stage B (NEW): _promote_legacy_activitynodegroup(graph)
 │   ├─ for each node where type=ActivityNodeGroup AND has group_kind data attr:
 │   │   ├─ if group_kind ∈ SQL_BACKED_KINDS_SPATIAL:
 │   │   │   ├─ swap class → LocationNodeGroup
 │   │   │   ├─ map group_kind → kind (functional/study)
 │   │   │   ├─ swap incoming is_in_activity edges → is_in_location
 │   │   │   └─ warnings.warn(... DeprecationWarning, stacklevel=2) ONCE per call
 │   │   └─ else: leave as ActivityNodeGroup
 │
 ├─ stage C (REWORKED): _apply_group_folders_to_sql(cur, graphml_path, sito)
 │   ├─ recursive walker:
 │   │   def walk(folder_node, visited):
 │   │     if folder_node.id in visited: raise CycleDetectedError
 │   │     visited.add(folder_node.id)
 │   │     kind = read pyarchinit.<kind> data entry
 │   │     if kind in SQL_BACKED_KINDS:
 │   │         UPDATE us_table SET <kind>=<group_name> WHERE node_uuid IN (...members)
 │   │     for child in folder_node.find_inner_graph().folders():
 │   │         walk(child, visited)  # nested LocationNodeGroup or ActivityNodeGroup
 │   ├─ ad-hoc / toponym → never write SQL (AC-14 unchanged)
 │   └─ count UPDATEs queued, return count
 │
 └─ return IngestResult
```

### 5.3 Algorithm: `compute_primary`

```python
DEFAULT_PRIMARY_PRIORITY = [
    "struttura", "attivita", "area", "settore",
    "ambient", "saggio", "quad_par",
]

def compute_primary(us_node, priority_order, all_memberships):
    """priority_order: list[str], default = DEFAULT_PRIMARY_PRIORITY
       (toponym never primary; adhoc comes after spatial+activity)
    """
    us_dims = {m.kind: m.group_uuid for m in all_memberships
               if m.us == us_node and m.kind != "toponym"}
    for dim in priority_order:
        if dim in us_dims:
            return us_dims[dim]
    return next(iter(us_dims.values()), None)
```

### 5.4 yEd visual rendering (driven by 0.1.41 visual rules)

- **Primary location** (`is_primary=true`): rendered as yEd group folder
  (dashed round-rectangle, border colour from `kind`)
- **Non-primary location** (`is_primary=false`): edge present in graph
  but NO yEd folder. The US node carries
  `<data key="s3d:other_locations">` payload `[{name, kind, group_uuid}, ...]`
  for badge inline rendering
- **Toponym chain**: only group folders (recursive nesting visible in
  yEd as folder-inside-folder), NEVER primary for US

## 6. Components and files touched

| File | Change | LOC |
|---|---|---|
| `modules/s3dgraphy/sync/graph_projector.py` | `_merge_groups` dispatch per dimension; `_emit_toponym_chain` new method | ~120 |
| `modules/s3dgraphy/sync/graph_ingestor.py` | `_apply_group_folders_to_sql` recursive + `_NON_STRAT_TYPES` += `LocationNodeGroup` + cycle detection + `_promote_legacy_activitynodegroup` on read-side | ~120 |
| `modules/s3dgraphy/sync/graphml_writer.py` | `_inject_group_folders` discriminates by node_type, palette extended with kind-aware lookup, `s3d:other_locations` data key emit | ~120 |
| `modules/s3dgraphy/sync/edge_registry.py` | Register `is_in_location` style + `primary_modifier` | ~30 |
| `modules/s3dgraphy/sync/group_projector.py` | `GroupSpec` adds `node_class` + `kind` (computed from `group_kind`) | ~40 |
| `modules/s3dgraphy/s3dgraphy_dot_bridge.py` | Dialog: remove multi-dim warning, add "Primary dimension" combobox | ~60 |
| `tests/sync/conftest.py` | ext_libs/ path bootstrap (Group 0 — see §10) | ~10 |
| `tests/sync/test_locationnodegroup_*.py` | 5 new test files | ~450 |
| `tests/sync/test_ai03_export_byte_identical.py` | Re-baseline (the fingerprint changes: node_type strings) | regen |

## 7. Error handling and edge cases

### 7.1 Projection errors (`ProjectionError`)

| Case | Behaviour |
|---|---|
| `site_table` missing or `sito` not found | Toponym chain = no-op (skip stage 3), continue. Log INFO |
| All admin levels empty | Skip silently. No warning |
| `LocationNodeGroup` not importable (vendored 0.1.40 still in place) | `ProjectionError("s3dgraphy>=0.1.41 required for spatial grouping; got <ver>")` |
| Ad-hoc group with member US not in graph | Edge skip + log WARNING (AI06 behaviour, unchanged) |
| Toponym dedupe collision (sha1 of `(name, "toponym")`) | Last-write-wins. Real-world collision probability negligible |

### 7.2 Ingest errors (`GraphIngestError`)

| Case | Behaviour |
|---|---|
| `LocationNodeGroup` read but 0.1.41 not available | `SchemaMismatchError("LocationNodeGroup found but s3dgraphy<0.1.41 — bump library")` |
| Recursive walker encounters cycle (LocationA → LocationB → LocationA) | `CycleDetectedError`, atomic rollback. Should never occur on coherent exports |
| Membership marked `is_primary=true` but folder absent in GraphML | Treat as non-primary, log WARNING. Non-blocking |
| More than 1 `is_primary=true` for same US | Take first encountered (deterministic walk order), log WARNING |
| Up-conversion: `group_kind` value not in `SQL_BACKED_KINDS_SPATIAL` | Leave as `ActivityNodeGroup`. Log INFO (could be a future custom kind) |

### 7.3 Deprecation policy

`DeprecationWarning` triggered **once per `populate_graph` / `populate_list`
call** with format:

```
DeprecationWarning: Found N legacy ActivityNodeGroup nodes with
group_kind ∈ {area, struttura, ...} in <path>. Promoting in-memory
to LocationNodeGroup + kind. Re-export the file via "Esporta Extended
Matrix" to migrate the on-disk representation. AI07 / pyarchinit 5.6.0+.
```

Routed to Python logger + QGIS console. Non-fatal.

### 7.4 Out of scope

**Batch CLI migration script** (`pyarchinit.tools.migrate_legacy_groupkind`):
deferred. With on-read up-conversion + re-export, users migrate files
naturally as they reopen them. Add the script later if production
demand surfaces.

## 8. Acceptance criteria

Existing AC inherited from AI06 / earlier:

- **AC-2**: byte-identical structural fingerprint on `mini_volterra.sqlite`
  export — RE-BASELINED in this Group (see §10)
- **AC-7**: GroupSpec dispatch determined by `group_kind`
- **AC-14**: ad-hoc / unrecognized kinds never write SQL

New AC for AI07:

- **AC-15**: round-trip identity for toponym chain — `site_table` is
  invariant after export → re-import
- **AC-16**: legacy 5.5.x file → projector promotes in-memory + emits
  `DeprecationWarning` once per call
- **AC-17**: for every US with N spatial memberships, exactly 1 edge has
  `is_primary=true`
- **AC-18**: recursive ingest preserves nesting `Country > Region >
  Province > Comune > Site` with `is_in_location` chain
- **AC-19**: `compute_primary` follows priority order; dialog override
  produces a different primary
- **AC-20**: cross-site dedupe — 2 sites with same `comune="Pompei"` →
  1 single `LocationNodeGroup(kind="toponym")` with deterministic
  `group_uuid`

## 9. Testing

### 9.1 Five new test files

| File | Tests | Cases | LOC |
|---|---|---|---|
| `test_locationnodegroup_projection.py` | dimension → class+kind dispatch | 7 dimensions × 2 path (strict/loose) | ~120 |
| `test_locationnodegroup_recursive_ingest.py` | recursive walker + cycle detection | 3-level nest, cycle abort | ~80 |
| `test_toponym_chain.py` | stage 3 emit + dedupe + skip empties | all populated / all empty / partial / cross-site | ~100 |
| `test_primary_selection.py` | `compute_primary` + dialog override | hardcoded order, custom override, fallback | ~60 |
| `test_legacy_autopromote.py` | on-read up-conversion + DeprecationWarning | 5.5.x → upcast; mixed legacy+new; attivita untouched | ~90 |

### 9.2 Test path bootstrap (Group 0)

**Pre-existing problem**: most sync tests use system pip-installed
`s3dgraphy 0.1.15`, NOT vendored 0.1.41. Only
`test_ai03_export_byte_identical.py` does the path manipulation.

**Fix in Group 0**: extend `tests/sync/conftest.py` with the same
path-bootstrap pattern (clear `s3dgraphy.*` from `sys.modules` +
ext_libs first in `sys.path`). Verify all 179 existing tests stay green
under 0.1.41. Patch surgically any that break (likely none — the API
surface used by sync tests is stable across 0.1.15 → 0.1.41).

### 9.3 AC-2 fingerprint re-baseline

The structural fingerprint at
`tests/sync/fixtures/mini_volterra_baseline_ai03.graphml` changes
because:
- `node_type` strings shift from `ActivityNodeGroup` to
  `LocationNodeGroup` for the 6 spatial dimensions
- Possible new `LocationNodeGroup(kind="toponym")` nodes if
  `mini_volterra` has admin levels populated

Strategy: dedicated commit at end of Group H regenerates the baseline +
updates expected fingerprint values. Diff documented in commit message
+ dev-log. The next commit verifies green again.

## 10. Release plan — 8 Groups (~20 commits)

Single tag at end: **`phase2-ai07-locationnodegroup-5.6.0-alpha`**.

Minor bump (5.5 → 5.6) justified by:
- node_type strings change in GraphML (visible to third-party consumers)
- AC-2 fingerprint changes (visible to CI)
- new edge type `is_in_location` introduced

| Group | Scope | Commits | Tests Δ |
|---|---|---|---|
| **0** | conftest path bootstrap (ext_libs first) + verify 179 existing green with 0.1.41 | 1-2 | regen |
| **A** | edge_registry + visual rules dispatch — register `is_in_location` style + `primary_modifier` | 2 | +5 |
| **B** | GroupSpec extension (`node_class`, `kind` computed from `group_kind`) — TDD pure-Python | 2 | +8 |
| **C** | `_merge_groups` rewrite — dispatch per dimension; AC-7/AC-14 stay green | 3 | +14 |
| **D** | `_emit_toponym_chain` + cross-site dedupe — AC-20 | 2 | +6 |
| **E** | `compute_primary` + dialog combobox override — AC-17, AC-19 | 2 | +5 |
| **F** | `_promote_legacy_activitynodegroup` (on-read) + DeprecationWarning — AC-16 | 2 | +4 |
| **G** | recursive `_apply_group_folders_to_sql` walker — AC-15, AC-18 | 2 | +6 |
| **H** | AC-2 re-baseline + dialog warning removal + manual smoke gate + dev-log + CHANGELOG + tag/push | 4 | regen |

**Totals**: ~20 commits, ~48 new test cases (~30 distinct, others
parametrized).

### 10.1 Manual smoke gate (Group H)

Before tag, **user manually performs**:

1. Open `test_ai_50us.sqlite` (Phase 2 pause synthetic fixture)
2. Export Extended Matrix with multi-dim (struttura + area)
3. Verify in yEd:
   - Primary yEd folder (struttura) rendered as dashed roundrectangle
     with `kind`-coloured border
   - Secondary folder (area) present as sibling, NOT parent of US (not
     primary)
   - Inline badge on US for the `s3d:other_locations` array
   - Toponym chain at canvas edges, recursive nesting Italia → Lazio →
     Roma → Casa del Fauno
4. Re-import in pyarchinit with checkbox "Update SQL" enabled
5. Verify `us_table` invariant (round-trip identity)
6. Open a 5.5.x legacy file: verify `DeprecationWarning` in logs,
   rendering remains sane

User confirms "ok smoke green" → tag + push.

### 10.2 Self-deadline

Target: **AI07 shipped by 2026-05-20** (10-11 days from spec). Margin
of 1-2 weeks before the CIDOC-S3D mapping call (end of May / early June).

## 11. Deliverable to s3dgraphy (separate from AI07 ship)

After the local AI07 tag, a follow-up PR to
`zalmoxes-laran/s3Dgraphy:main`:

1. Extract `test_ai_50us.sqlite` as fixture in
   `tests/integration/pyarchinit_roundtrip/` on s3dgraphy
2. Add Python script `test_pyarchinit_roundtrip.py`: load → projector →
   s3dgraphy → re-import → identity check on `us_table`
3. README explains how an s3dgraphy user runs it (requires pyarchinit
   installed; conditional skip otherwise)
4. PR opened, Emanuel as reviewer, cross-linked from the AI07 commit

## 12. Memory + changelog updates (post-tag)

- `project_ai07_active.md` → archive as `project_ai07_shipped_2026-05-XX.md`
- New `project_ai07_post_release.md` with state (tag SHA, ETA CIDOC call,
  fixture PR pending)
- `MEMORY.md` index updated
- `dev_logs/CHANGELOG.md` bilingual IT/EN entry under heading
  `[5.6.0-alpha] - 2026-05-XX`

## 13. Out of scope (explicit deferrals)

- **AI08-F3 — auto-layout heuristics**: bin-packing for sub-group spatial
  placement. Deferred pending real-world feedback on F2 alpha-blending
- **AI09 — TimeBranchNodeGroup**: `cron_iniziale / cron_finale` mapping.
  Pending future brainstorming
- **`pyarchinit.tools.migrate_legacy_groupkind`** standalone CLI script:
  deferred; on-read auto-promote covers the 90% case
- **Phase 3 (SyncEngine + REST API)** and **Phase 4 (GraphDBBackend +
  SPARQL)**: untouched

## 14. References

- Upstream issue: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Upstream tag: `v0.1.41` shipped 2026-05-09
- s3dgraphy CHANGELOG: https://github.com/zalmoxes-laran/s3Dgraphy/blob/main/CHANGELOG.md
- Predecessor spec (AI06): `docs/superpowers/specs/2026-05-08-ai06-node-grouping-design.md`
- Parent spec: `docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md`
- Memory note: `~/.claude/projects/.../memory/project_ai07_active.md`
