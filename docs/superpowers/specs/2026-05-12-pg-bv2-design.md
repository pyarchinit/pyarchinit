# PG-Bv2 — Design Spec (GraphML export on PostgreSQL)

**Date:** 2026-05-12
**Branch:** Stratigraph_00001
**Predecessor tag:** `pg-uuidfix-5.7.8.1-alpha` (commit `84d625fc`)
**Target tag:** `pg-bv2-5.7.9-alpha`

---

## 1. Goal

Complete the PostgreSQL support gap left by PG-B (`phase3-pgcompat-b-export-5.7.1-alpha`, 2026-05-10): enable end-to-end GraphML export from the matrix viewer when the user's pyarchinit project is on a PG backend. After PG-Bv2 ships, a PG user can click "Export Matrix" → get a complete `Extended_Matrix_<site>.graphml` file equivalent to the SQLite output.

User-demand priority: HIGH (explicitly requested 2026-05-12 evening as next milestone before yE-D Pipeline).

## 2. Background

PG-B (commit `3a2597ab`, 2026-05-10) flipped 5 SQL READ sites in `modules/s3dgraphy/sync/graph_projector.py` to use `_resolve_db_handle` (lines 303, 367, 509, 761, 877). Those 5 helpers all work on PG. BUT the orchestrator `populate_graph()` itself was missed:

- **Line 165**: `db_path = Path(db_path)` — unconditional `Path()` coercion that raises `TypeError` when called with a `Pyarchinit_db_management` instance.
- **Line 190**: `PyArchInitImporter(filepath=str(db_path), mapping_name="pyarchinit_us_mapping")` — the upstream importer in `ext_libs/s3dgraphy/importer/pyarchinit_importer.py` uses `sqlite3` directly and only accepts filesystem paths.

The user discovered this during PG-UIFix testing 2026-05-12: removing the `if db_path is None: skip` branch in `s3dgraphy_dot_bridge.py:191-206` exposed the TypeError. PG-UIFix reverted the export-skip removal with an honest "pending PG-Bv2" message (commit `bc90c86c`). PG-Bv2 closes the gap properly.

## 3. Architectural decisions (brainstorm 2026-05-12)

| Q | Choice | Reason |
|---|---|---|
| Q1 — Approach | **α — SQLAlchemy native reader replacing upstream** | Clean, no disk I/O, no upstream patch, identical on SQLite/PG when needed |
| Q2 — Scope | **α-narrow — PG branch only, SQLite stays on upstream** | Preserves AC-2 byte-identical baseline; matches PG-B's per-site flip pattern |
| Q3 — Version | **`pg-bv2-5.7.9-alpha` (minor bump)** | Feature, not patch. Shifts yE-D to `5.8.0-alpha`, yE-E to `5.8.1-alpha`, yE-Closure to `5.8.2-alpha`. |

Rejected:
- β (temp PG → SQLite roundtrip): hacky, disk I/O per export, double type conversion, depends on `pg_dump` for export not just backup
- γ (patch upstream `PyArchInitImporter`): touches `ext_libs/s3dgraphy/` package, complicates future `pip install s3dgraphy` upgrades
- α-wide (replace upstream for BOTH backends): too risky for AC-2 byte-identical baseline in one milestone
- α-flag (env var switch): permanent dual code paths, more maintenance

## 4. Architecture

### New module: `modules/s3dgraphy/sync/pyarchinit_pg_importer.py` (~100 LOC)

Public function:

```python
def import_from_pg(
    handle: DbHandle,
    sito: str,
    mapping_name: str = "pyarchinit_us_mapping",
) -> "s3dgraphy.Graph":
    """Build a stratigraphic Graph by reading us_table from a PG backend
    via SQLAlchemy. DbHandle-aware replacement for the upstream
    PyArchInitImporter call in graph_projector.populate_graph() when
    backend is PG.

    Args:
        handle: DbHandle for the PG database
        sito: site identifier (us_table.sito value)
        mapping_name: mapping JSON name in
            ext_libs/s3dgraphy/mappings/pyarchinit/<name>.json

    Returns:
        s3dgraphy.Graph populated with StratigraphicNode + PropertyNode
        objects connected by has_property edges per the mapping JSON.
        Graph is UNREGISTERED (caller sets graph_id + registers).
    """
```

Implementation steps:

1. **Load mapping JSON** from `ext_libs/s3dgraphy/mappings/pyarchinit/{mapping_name}.json` using `importlib.resources` or direct file read. Cache per call.

2. **Read rows** via SQLAlchemy:
   ```python
   with handle.engine.connect() as conn:
       rows = conn.execute(
           text("SELECT * FROM us_table WHERE sito = :sito"),
           {"sito": sito},
       ).mappings().all()
   ```

3. **Build StratigraphicNodes** per row:
   - Use `_get_stratigraphic_node_class(unita_tipo)` from `ext_libs/s3dgraphy/utils/utils.py` (already exists, no change needed there)
   - Name = `row[id_column]` (from `column_mappings.*.is_id`)
   - Description = `row[desc_column]` (from `column_mappings.*.is_description`)
   - Type derived from `unita_tipo` column

4. **Build PropertyNodes** per row × column:
   - For each `column_mappings[col].node_type == "PropertyNode"`:
     - Create `PropertyNode(name=property_name, value=row[col], description=...)`
     - Connect via `has_property` edge

5. **Build edges** from `relations[]` in mapping JSON.

6. **Return** the unregistered `Graph` (caller sets graph_id + registers).

Note: this mirrors the contract of `PyArchInitImporter.parse()` but only for the subset of mapping types pyarchinit actually uses (US table → StratigraphicNode + PropertyNode + has_property). Other s3dgraphy importer features (EpochNode auto-creation, multi-graph mode, enriching-existing-graph) are NOT in scope — `populate_graph()` builds those separately.

### Modified: `modules/s3dgraphy/sync/graph_projector.py` lines 161-196

```python
if not sito:
    raise ProjectionError(...)

# PG-Bv2: route through DbHandle shim. Path coercion + SQLite-only
# importer call removed for PG; SQLite path kept unchanged for
# AC-2 byte-identical baseline preservation.
from ._db_handle import _resolve_db_handle
handle = _resolve_db_handle(db_path)

if strict_schema:
    self._verify_node_uuid_column(handle)  # already PG-flipped

try:
    from s3dgraphy import Graph
    if handle.is_postgres:
        # PG-Bv2: native SQLAlchemy reader.
        from .pyarchinit_pg_importer import import_from_pg
        imported = import_from_pg(handle, sito,
                                  mapping_name="pyarchinit_us_mapping")
    else:
        # SQLite: upstream PyArchInitImporter unchanged for AC-2.
        from s3dgraphy.importer.pyarchinit_importer import (
            PyArchInitImporter)
        if not Path(db_path).exists():
            raise ProjectionError(f"DB file not found: {db_path}")
        importer = PyArchInitImporter(
            filepath=str(db_path),
            mapping_name="pyarchinit_us_mapping",
        )
        imported = importer.parse()
except (ImportError, Exception) as e:
    raise ProjectionError(f"Importer failed: {e}") from e
```

The 5 downstream helpers (`_enrich_into`, `_propagate_node_uuid_and_us`, `_emit_toponym_chain`, `_merge_paradata`, `_merge_groups`) ALREADY accept `db_path | DbHandle` via `_resolve_db_handle` (PG-B). They keep working with either input.

### Modified: `modules/s3dgraphy/s3dgraphy_dot_bridge.py` lines 188-220

Re-remove the `if db_path is None: skip` branch (originally removed by PG-UIFix commit `de0174f0`, restored by revert commit `bc90c86c`). The `else:` body becomes unconditional again. `db_path = self.db_manager` passes the manager directly to `export_graphml()` which routes through `_resolve_db_handle`.

This is the same code change PG-UIFix attempted but it's safe NOW because the underlying `populate_graph()` actually supports PG.

### Test 2 inversion in `tests/sync/test_pg_uifix.py`

DELETE `test_graphml_export_pg_skip_branch_is_present_pending_pg_bv2` (its purpose was to pin the deferred-state; PG-Bv2 ends the deferral).

REPLACE with `test_graphml_export_runs_on_pg_backend`:
- Assert NO `"pending PG-Bv2 milestone"` in source
- Assert NO `"postgresql backend deferred"` in source
- Assert NO `"if db_path is None"` PG-skip pattern in source

Plus the original PG-UIFix Bug 2 import-flow guards stay removed.

## 5. Files

### Created (1 module + 1 test file)

| Path | Purpose | LOC |
|---|---|---|
| `modules/s3dgraphy/sync/pyarchinit_pg_importer.py` | DbHandle-aware reader replacing upstream `PyArchInitImporter` on PG | ~100 |
| `tests/sync/test_pg_bv2_pg_importer.py` | 2 L0 tests (mapping JSON load + mocked rows) + 2 L2 PG tests (end-to-end export + SQLite-vs-PG structural equivalence) | ~150 |

### Modified

| Path | Change | LOC delta |
|---|---|---|
| `modules/s3dgraphy/sync/graph_projector.py` | Replace lines 161-196 with handle-aware branch | ~−30 / +35 |
| `modules/s3dgraphy/s3dgraphy_dot_bridge.py` | Re-remove `if db_path is None: skip` branch (restored by PG-UIFix `bc90c86c`); de-indent `else:` body | ~−30 / +5 |
| `tests/sync/test_pg_uifix.py` | Replace `test_graphml_export_pg_skip_branch_is_present_pending_pg_bv2` with `test_graphml_export_runs_on_pg_backend` | ~−40 / +25 |
| `metadata.txt` | `5.7.8.1-alpha` → `5.7.9-alpha` | 1 |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.9-alpha]` section | ~80 |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Prepend PG-Bv2 section above PG-UUIDFix | ~60 |
| `docs/superpowers/specs/2026-05-12-yed-import-pipeline-design.md` | Target tag shift: `5.7.9` → `5.8.0`, `5.8.0` → `5.8.1`, `5.8.1` → `5.8.2` | ~5 |

Total scope: ~380 LOC delta.

## 6. Tests

### L0 (run everywhere, no PG runtime needed)

1. **`test_pg_importer_mapping_json_resolves`**: assert `ext_libs/s3dgraphy/mappings/pyarchinit/pyarchinit_us_mapping.json` exists and is valid JSON with expected schema (column_mappings, relations keys).

2. **`test_pg_importer_builds_strat_node_from_mock_row`**: use `unittest.mock` to stub `handle.engine.connect()` returning fake rows. Call `import_from_pg(mock_handle, "S")`. Assert returned Graph has 1 StratigraphicNode named "1" with description from `d_stratigrafica`, and N PropertyNodes connected by `has_property` edges.

### L2 PG (skip when psycopg2 missing or PG offline)

3. **`test_pg_export_graphml_end_to_end`**: use `pg_with_volterra` fixture (PG-B). Call `S3DGraphyDotBridge.export(formats=['graphml'])`. Assert `exported_files['graphml']` is set, file exists, contains expected `<node id="us-N">` patterns. NO `graphml_status: skip` reason.

4. **`test_pg_export_graphml_structural_match_sqlite`**: load same Volterra fixture into both SQLite (in `tmp_path/volterra.sqlite`) and PG (`pg_with_volterra`). Export both as graphml. Assert structural equivalence:
   - Same number of `<node>` elements
   - Same set of `<edge>` source/target pairs
   - Same set of stratigraphic node IDs (`us-1`, `us-2`, ...)
   - Allow minor ordering differences (not byte-identical, but topologically equivalent)

### Update PG-UIFix Bug 2 test

5. **DELETE** `test_graphml_export_pg_skip_branch_is_present_pending_pg_bv2` (no longer applicable).

6. **ADD** `test_graphml_export_runs_on_pg_backend`: source-inspection assert NO `"pending PG-Bv2 milestone"`, NO `"postgresql backend deferred"`, NO `"if db_path is None"` skip pattern in `s3dgraphy_dot_bridge.py`. Belt-and-braces for the actual end-to-end L2 test.

### Regression gates (all must stay green)

- AC-2 byte-identical (SQLite path unchanged)
- 3 critical SQLite gates
- 8 PG-D L2 (when PG online)
- 5 yE-A + 12 yE-B + 16 yE-C
- 2 PG-UIFix L0 (1 inverted, 1 unchanged)
- 7 PG-UUIDFix (2 L0 + 5 sources/mocks/L2)

Test count progression: 296 → 300 passed, 35 skipped (PG offline) — 4 new (2 L0 + 2 L2 skip). With PG online: 296 → 304 passed, 12 skipped.

## 7. Implementation plan groups

Following the established PG-UIFix / PG-UUIDFix pattern:

- **Group 0** — Pre-flight: clean state check, rollback safety tag `pre-pg-bv2`, baseline test counts
- **Group A** — Production: new module `pyarchinit_pg_importer.py` + graph_projector branch + bridge re-removal + L0 tests + L2 PG tests + PG-UIFix Bug 2 test inversion (single commit)
- **Group B** — Docs + version bump 5.7.8.1 → 5.7.9-alpha + bilingual CHANGELOG + dev-log PG-Bv2 section + yE-D spec re-version (5.7.9 → 5.8.0)
- **Group C** — Annotated tag `pg-bv2-5.7.9-alpha` + USER APPROVAL GATE + push
- **Group D** — Memory snapshot

Effort estimate: ~2-3 person-days. The new module is the substantial part (~100 LOC of careful schema/JSON consumption code).

## 8. Risks & mitigations

| Risk | Mitigation |
|---|---|
| New reader produces output differing from upstream importer (subtle attribute or edge missing) | L2 test #4 compares SQLite (upstream) vs PG (new reader) output side-by-side, asserts structural equivalence |
| Mapping JSON evolves and breaks the reader | Mapping is loaded at module-level; test #1 pins the expected schema |
| PG-D L2 tests break (paradata/group store regressions) | None expected — `populate_graph` change is isolated to lines 161-196, downstream helpers untouched |
| AC-2 byte-identical regression | NOT a concern — α-narrow keeps SQLite path on upstream importer, AC-2 fixture unchanged |
| User's khutm2 export still slow due to slow remote PG | Out of scope — PG-Bv2 only fixes correctness, not throughput. Note in dev-log that very large remote PG may take minutes to export. |

## 9. Out of scope

- **yE-D Pipeline** (`yed-import-pipeline-5.8.0-alpha`) — next milestone, shifted by PG-Bv2
- **pg-media-fix** — separate diagnostic milestone (user provided initial signal: "view media" button in US/Pottery forms does nothing on PG; needs handler trace)
- **α-wide promotion** — replacing upstream `PyArchInitImporter` for SQLite too. Future milestone (e.g., `pg-bv3-unify-importer-5.x.y-alpha`) after PG-Bv2 is battle-tested.
- **GraphML export performance optimization** on PG — possible follow-up if needed
- **Schema files** — already declare correct PKs (audited 2026-05-12), no changes

## 10. Plan-time investigation checklist

Before writing Group A code, the implementer must:

1. **Confirm `_resolve_db_handle` accepts Pyarchinit_db_management** end-to-end:
   ```bash
   grep -n "_resolve_db_handle\|class DbHandle" modules/s3dgraphy/sync/_db_handle.py | head -20
   ```

2. **Locate upstream `PyArchInitImporter.process_row()`** to understand what attributes it sets on StratigraphicNode:
   ```bash
   grep -n "PropertyNode\|StratigraphicNode\|property_node" ext_libs/s3dgraphy/importer/pyarchinit_importer.py
   ```

3. **Confirm `_get_stratigraphic_node_class(unita_tipo)`** is importable + handles all `unita_tipo` values pyarchinit produces (US, USM, USR, USVs, USVn, ...):
   ```bash
   grep -n "def _get_stratigraphic_node_class\|^STRATIGRAPHIC_CLASSES" ext_libs/s3dgraphy/utils/utils.py
   ```

4. **Verify `pg_with_volterra` fixture covers** the necessary tables for graphml export end-to-end (us_table, site_table, periodizzazione_table, paradata):
   ```bash
   grep -n "pg_with_volterra\|load_sqlite_into_pg" tests/sync/conftest_pg.py
   ```

5. **Spot-check that PG-UIFix Bug 2 test still exists** as we'll invert it:
   ```bash
   grep -n "test_graphml_export_pg_skip_branch_is_present_pending_pg_bv2" tests/sync/test_pg_uifix.py
   ```

## 11. Predecessor lineage

```
yed-import-parsers-5.7.7-alpha  (yE-C, 2026-05-12, 5d666c67)
  └── pg-uifix-5.7.8-alpha       (2026-05-12, e35e137c) — partial scope
      └── pg-uuidfix-5.7.8.1-alpha (2026-05-12, 84d625fc) — patch
          └── pg-bv2-5.7.9-alpha    (TBD, this milestone)
              └── yed-import-pipeline-5.8.0-alpha  (yE-D, was 5.7.9)
                  └── yed-import-dialog-5.8.1-alpha  (yE-E, was 5.8.0)
                      └── yed-import-closure-5.8.2-alpha  (yE-Closure, was 5.8.1)
```

## 12. User test plan (Group C gate)

Before push, 3 manual checks:

1. **PG project graphml export end-to-end**: open `khutm2` on PG → matrix viewer → "Esporta Matrix" → log shows `✅ GraphML → /path/to/Extended_Matrix_Al-Khutm_1.graphml` (NOT skip message). Open the file with yEd or text editor → contains stratigraphic node markup.

2. **SQLite still exports correctly**: switch to SQLite project (any) → repeat export → behavior identical to pre-PG-Bv2 (AC-2 byte-identical preserved).

3. **PG paradata still works (PG-UIFix regression check)**: open paradata manager on PG project → add author → save. No errors.

If all 3 pass: user replies `approvato` → push branch + tag.
