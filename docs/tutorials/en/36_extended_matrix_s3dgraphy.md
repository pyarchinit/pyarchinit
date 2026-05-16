# Tutorial 36: Extended Matrix Export and s3dgraphy Bridge

## Introduction

Starting with **5.2.0-alpha** PyArchInit integrates a **bidirectional bridge** with the **s3dgraphy** library (Extended Matrix data model by Emanuel Demetrescu). The bridge allows you to:

- **Export** the stratigraphic diagram as Extended Matrix in GraphML (with temporal swimlanes, transitive reduction, EM 1.5 edge styling)
- **Re-import** changes made in yEd (US movements between periods/groups) updating the pyarchinit SQL database
- **Attach paradata** (Author / License / Embargo) at site level
- **Group** SUs by dimension (struttura, area, attivita, settore, ambient, saggio, quad_par or ad-hoc groups)

Current tag: `phase2-ai07-locationnodegroup-5.6.0-alpha` (2026-05-10).

---

## 1. Requirements

- SQLite database (PostgreSQL not yet supported)
- **Phase 1 node_uuid migration** applied automatically when the DB is opened
- **yEd Graph Editor** to view the output (https://www.yworks.com/products/yed)

> ⚠️ For DBs from before 5.2.0-alpha, the migration may require restarting QGIS.

---

## 2. Export Extended Matrix (green button)

### 2.1 Open the dialog

1. Open the **US Form** for your site
2. Click the green **"Esporta Extended Matrix"** button (under the Rapporti tab)

### 2.2 "Export" tab

The dialog shows:

- **Output formats**: check DOT / GraphML / JSON / phased JSON (recommended: GraphML)
- **Group US by (optional)**: 7 checkboxes for grouping dimensions + 1 "ad-hoc" checkbox
  - Dimensions populated in the DB are **auto-checked** at dialog open
- **Primary dimension combobox** (default `struttura`): when an SU has memberships across 2+ dimensions, the primary one wins as the visible yEd folder (hierarchical parent). Secondary dimensions show as inline badges below the SU node. `toponym` is never primary regardless of selection.
- **"Select Output Directory"**: target folder

From 5.6.0-alpha you can check **2+ dimensions**: the export works natively thanks to the m:n model with `is_primary` (see "Multi-dimension membership" section).

### 2.3 Click "Export"

4 files are generated with prefix `Extended_Matrix_<site>[_<area>]`:
- `.dot` — Graphviz DOT
- `.graphml` — Extended Matrix for yEd (our main target)
- `_s3dgraphy.json` — native s3dgraphy format
- `_phased.json` — per-epoch view

---

## 3. "Manage paradata" Dialog (4 tabs)

### 3.1 Access
Click the **"Manage paradata"** button in the US form (next to the green Export button).

### 3.2 The 4 tabs

| Tab | Content | File generated |
|---|---|---|
| **Authors** | Add authors (name + ORCID + role) | `paradata_<site>.graphml` |
| **Licenses** | Dataset license (e.g. CC-BY-NC-4.0 + URL) | same |
| **Embargoes** | Embargo dates + reason | same |
| **Groups** | Ad-hoc groups (name + US member selection) | `groups_<site>.graphml` |

Files are saved next to the SQLite DB and are **Git-versionable**.

---

## 4. Per-dimension visual style (5.5.1-alpha + 5.6.0-alpha)

Each grouping dimension has a distinct color in GraphML:

| Dimension | Fill (50% transparency) | Border |
|---|---|---|
| `area` | pastel pink `#FFE0E680` | `#C84A5F` |
| `struttura` | pastel orange `#FFE6CC80` | `#C66B33` |
| `attivita` | pastel yellow `#FFF5CC80` | `#A89A33` |
| `settore` | pastel green `#E6FFCC80` | `#6BC633` |
| `ambient` | pastel aqua `#CCFFE680` | `#33A86B` |
| `saggio` | pastel azure `#CCF5FF80` | `#3389A8` |
| `quad_par` | pastel violet `#E0CCFF80` | `#6633C6` |
| `adhoc` | pastel grey `#F5F5F580` | `#666666` |

From 5.6.0-alpha, `LocationNodeGroup` items are distinguished by `kind`:

| `kind` | Fill (50% transparency) | Border |
|---|---|---|
| `toponym` | pastel lavender `#E6E6FA80` | `#9370DB` |
| `study` | pastel ivory `#FFFFE080` | `#888888` |
| `functional` | pastel cyan `#E0FFFF80` | `#008B8B` |

The 50% alpha lets epoch swimlane rows stay visible behind the group rectangle.

### 4.1 Toponym chain (5.6.0-alpha)

The fields `site_table.{nazione, regione, provincia, comune}` are auto-emitted as a recursive `LocationNodeGroup(kind="toponym")` chain (parent: nazione → regione → provincia → comune). Empty admin levels are skipped without breaking the chain. A cross-site dedupe ensures that the same `comune` present in 2 sites becomes **one shared node** in the GraphML.

---

## 4.2 Multi-dimension membership (5.6.0-alpha)

From 5.6.0-alpha an SU can belong to **multiple dimensions simultaneously** thanks to the m:n model with the `is_primary` flag. Only the primary dimension becomes the visible yEd folder; the others appear as **inline badges** below the SU node and as JSON in `<data key="s3d:other_locations">` for downstream tools.

Example: an SU with `struttura=basilica` and `area=B` (primary `struttura`) yields:
- yEd folder "struttura: basilica" as the visible parent;
- below the SU node, an inline badge `also: B (study), TestCity (toponym)`;
- in the GraphML, the `s3d:other_locations` attribute with a JSON array of secondary memberships.

The primary dimension is controlled via the combobox in §2.2.

---

## 5. Round-trip (Import tab)

To update the SQL database by moving SUs between groups in GraphML:

1. Open the GraphML in **yEd**
2. Drag an SU into a different group, save
3. Back to the dialog → **"Import"** tab
4. **Check** the *"Update SQL on import (struttura/area/...)"* checkbox
5. Load the modified GraphML

The system runs an atomic transaction: if anything fails, **full rollback** (the DB stays unchanged). `adhoc` groups never write SQL — they only update `groups_<site>.graphml`.

From 5.6.0-alpha the import walker is **recursive** and supports nested folders (e.g. toponym chain `nazione > regione > provincia > comune > SU`). When cycles are detected in the folder graph, a `CycleDetectedError` is raised and the import is aborted with rollback.

---

## 6. CLI (alternative to dialog)

For scripts / batch:

```bash
# Export
python scripts/s3dgraphy_sync.py export \
    --db <path> --sito <name> --mapping pyarchinit_us_mapping \
    --output <out.graphml> --group-by struttura

# List ad-hoc groups
python scripts/s3dgraphy_sync.py paradata list-groups \
    --db <path> --sito <name>

# Add author
python scripts/s3dgraphy_sync.py paradata add-author \
    --db <path> --sito <name> --name "Marco Pacifico" \
    --orcid "0000-0002-1234-5678" --role curator
```

Exit codes: 0 = success, 1 = bridge error, 2 = argparse error.

---

## 7. Troubleshooting

| Symptom | Cause | Solution |
|---|---|---|
| "no such column: node_uuid" | Phase 1 migration not run | Restart QGIS, reopen the DB |
| Empty GraphML | DB without rapporti / area filter too strict | Verify us_table.rapporti is populated |
| "rapporti fields must be TEXT" | Entered a number as integer | US/Area fields are **TEXT**, not integer |
| Wrong capitalization on rapporti | Lowercase "copre" in DB | Use "Copre", "Coperto da" capitalized |
| `DeprecationWarning` on 5.5.x file | Legacy `ActivityNodeGroup + group_kind` file | The projector promotes it in-memory to `LocationNodeGroup`. Re-export to migrate the file on disk. |

---

## 8. Technical documentation

For architecture deep dives, design decisions and roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Deferred carry-overs:
- **AI08-F3**: auto-layout heuristics (sub-group bin-packing) — still deferred
- **AI09**: TimeBranchNodeGroup mapping — future
- **Phase 3**: SyncEngine + REST API — future
- **Phase 4**: GraphDBBackend + SPARQL — future

Shipped:
- **AI07** (5.6.0-alpha, 2026-05-10): `LocationNodeGroup` migration with `kind` enum + toponym chain + multi-dim memberships
- **AI08-F1** (fused into AI07): native hierarchical nesting via `is_primary`

---

## 5. yEd-aware Import — importing externally-authored graphmls (5.8.x)

From **5.8.0-alpha** the bridge is **bidirectional even for graphmls authored directly in yEd** (i.e. without first going through a pyarchinit export). Pyarchinit auto-recognises "yEd-raw" graphmls — those without `pyarchinit.*` data keys — and imports them through a dedicated dispatch that maps node-label-prefix → stratigraphic type, recognises TableNode rows as periods, walks group folders as archaeological dimensions, and lets the user pick a policy for folder-touching edges.

### 5.1 6-milestone rollout

| Milestone | Tag | Adds |
|---|---|---|
| **yE-A** | `yed-import-foundation-5.7.5-alpha` | `yed_detector.py` — flavour flag `yed-raw` / `pyarchinit-projected` |
| **yE-B** | `yed-import-classifier-5.7.6-alpha` | `yed_classifier.py` — `ClassificationKind` enum 13 values (US/USV/SF/VSF/RSF/DOC/COMB/PROP/...) + order-sensitive regex |
| **yE-C** | `yed-import-parsers-5.7.7-alpha` | `yed_table_parser.py` (PeriodCandidate from TableNode rows) + `yed_group_walker.py` (FolderCandidate with auto-dimension from label prefix: VA01→attivita / AR01→area / etc.) |
| **yE-D** | `yed-import-pipeline-5.8.0-alpha` | `yed_import_pipeline.py` — `import_yed_raw()` orchestrator + 5 write functions + `FolderEdgePolicy` (SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC) + paradata via `ParadataStore` + `_DryRunRollback` sentinel + DbHandle PG+SQLite |
| **yE-E** | `yed-import-dialog-5.8.2-alpha` | `gui/yed_import_dialog.py` — `YedImportDialog(QWizard)` 5 pages (classifier / periods / folders / policy / preview) + `YedOverrides` dataclass + sidecar `<graphml>.yed_overrides.json` persistence |
| **yE-Closure** | `yed-import-closure-5.8.3-alpha` | This documentation + dev-log + CHANGELOG. |

### 5.2 How it works — user flow

1. **Open a graphml in QGIS via the Import GraphML menu** (same path as the existing pyarchinit-projected flow).
2. Pyarchinit auto-detects it as yEd-raw (no `pyarchinit.*` keys) → dispatches to the new branch instead of falling through to the legacy path.
3. The `YedImportDialog` wizard opens with **5 pages**:
   - **1/5 Classifier** — table, 1 row per leaf. Each row shows `label` + `auto_kind` (e.g. `us_real` / `usv_virtual` / `property`) + a `user_kind` override combobox. **Accept auto** button resets every row to its `auto_kind` (clear all overrides).
   - **2/5 Periods** — 1 row per TableNode-row parsed, editable `periodo` + `fase` cells. Dates (`datazione_iniziale`/`finale`) stay empty: yEd-raw graphmls don't carry dates.
   - **3/5 Folders** — 1 row per group folder. `dimension` combobox (attivita / area / struttura / settore / ambient / saggio / quad_par / `skip` to exclude). `value` text-edit (default = `auto_value` derived from label prefix).
   - **4/5 Rapporti policy** — 4 radio buttons for how to treat folder-touching edges:
     - **SKIP** (default): drop folder-touching edges. Leaf-to-leaf edges pass through unchanged.
     - **FAN_OUT**: a `folder_A → folder_B` edge expands to `N×M` leaf pairs (cartesian product of members).
     - **REPRESENTATIVE**: use the first member of each folder as a proxy.
     - **SYNTHETIC**: create one us_table row per folder (`unita_tipo='VA'` virtual activity) + rewire edges through these anchors.
   - **5/5 Preview** — dry-run of `import_yed_raw(overrides=..., dry_run=True)`. Displays counts (us / inv / period / paradata) **without committing**. Click **Finish** to commit, **Cancel** to abort.
4. On **Finish** the wizard saves your overrides to a **sidecar JSON** `<graphml>.yed_overrides.json` next to the file. Re-opening the same graphml preloads the sidecar so your previous overrides come pre-applied.

### 5.3 Destination routing

The dispatch uses `_classify_destination` (in `yed_import_pipeline.py`) to bucket each leaf:

| ClassificationKind | Destination | Note |
|---|---|---|
| US_REAL | `us_table` (`unita_tipo='US'`) | from label `^US\d+` |
| US_MASONRY | `us_table` (`unita_tipo='USM'`) | from `^USM|USR|USS` |
| US_DOCUMENTARY | `us_table` (`unita_tipo='USD'`) | from `^USD\d+` |
| USV_VIRTUAL | `us_table` (`unita_tipo='USV'`) | from `^USV\d+` |
| USV_FORMAL | `us_table` (`unita_tipo` derived from label prefix: USVs/USVn/USVc) | from `^USVs|USVn\d*$` |
| **REUSED_SPECIAL_FIND** (RSF — **5.8.1**) | `us_table` (`unita_tipo='RSF'`) | from `^RSF\d+` (s3dgraphy 0.1.42, spolia) |
| SPECIAL_FIND | `inventario_materiali_table` | from `^SF\d+` |
| VIRTUAL_FIND | `paradata` (via `ParadataStore`) | from `^VSF\d+` |
| DOCUMENT | `paradata` | from `^D\.\d+` |
| COMBINER | `paradata` | from `^C\.\d+` |
| PROPERTY | `paradata` | label keyword (`material`/`position`/`width`/...) |

**User decision 2026-05-13**: USV* (virtual) are "unità tipo" (still stratigraphic units) and belong in `us_table`, not in paradata. Only DOC/COMB/PROP/VIRTUAL_FIND remain in paradata.

### 5.4 Sidecar JSON — schema

Versioned for forward-compat:

```json
{
  "version": 1,
  "saved_at": "2026-05-13T17:57:00+00:00",
  "graphml_path": "/absolute/path/to/file.graphml",
  "classifier": {
    "n0::n0::n0": "us_real",
    "n0::n0::n2": "us_real"
  },
  "periods": {
    "p0": {"periodo": 5, "fase": 7}
  },
  "folders": {
    "f0": {"dimension": "struttura", "value": "S01"}
  },
  "policy": "fan_out"
}
```

Only USER-MODIFIED fields are persisted (diff). Unknown `ClassificationKind` values (e.g. from future s3dgraphy releases) are skipped silently at load time.

### 5.5 CLI for scripted ingest

For CI / batch re-runs:

```bash
python scripts/import_yed_graphml.py /path/to/file.graphml \
    --site Al-Khutm \
    --db /path/to/khutm2.sqlite \
    --policy skip \
    --overrides /path/to/file.graphml.yed_overrides.json \
    --dry-run
```

Mutex `--db` / `--conn-str` for SQLite vs PostgreSQL backend. `--overrides` is optional (no overrides = yE-D defaults). `--auto-defaults` is a no-op forward-compat flag.

### 5.6 Known limits

- **No date editing in wizard**: yEd-raw graphmls don't carry `datazione_iniziale`/`datazione_finale`. The Periods page edits only `periodo` + `fase` (FK targets).
- **Partial ParadataStore API**: upstream s3dgraphy doesn't yet ship `add_virtual_us` / `add_document` / `add_combiner` / `add_property`. yE-D logs "skip — method missing" per paradata leaf but counts the attempts in the preview.
- **PropertyNode → Path B (no US linkage)**: PROPERTY nodes are written without a target US. The wizard emits a warning. Future: yE-Closure follow-up to add "assign target" in the UI.
- **Multi-DB**: the sidecar JSON is per-graphml, not per-DB. Importing the same graphml into different DBs uses the same overrides for both.

### 5.7 Final test coverage

| Suite | Test | Coverage |
|---|---|---|
| yE-A | `test_yed_detector.py` | flavour detection |
| yE-B | `test_yed_classifier.py` | 13 ClassificationKind + order-sensitive regex |
| yE-C | `test_yed_table_parser.py` + `test_yed_group_walker.py` | PeriodCandidate + FolderCandidate parse |
| yE-D | `test_yed_rapporti_policy.py` (7) + `test_yed_import_pipeline.py` (15) + `test_yed_pipeline_integration.py` (9 incl. 2 L1 overrides e2e) | policies + write functions + dispatch |
| yE-E | `test_yed_import_dialog.py` (5 sidecar JSON) + `test_import_yed_graphml_cli.py` (3) | sidecar persistence + CLI |

**Total suite post-rollout**: 354 passed / 42 skipped (PG-L1 require psycopg2).

### 5.8 Update 5.8.5-alpha (yed-fastfix)

Behavioural fix pack on top of `5.8.3-alpha` that improves the quality of the GraphML re-export after a yEd-aware import. End-user-relevant changes:

- **Multi-folder paradata**: DOC / Combinar / Extractor / property labels shared across yEd folders (e.g. `material` referenced from VA01 + VA04 + VA05) now create ONE `us_table` row PER occurrence — restored multi-folder visibility in the re-exported GraphML. Trade-off: identity-dedup (`D.01` / `D.01-2` / `D.01bis` collapsing into a single row) no longer applies for the second/third occurrence.
- **Reciprocal rapporti**: each yEd edge `a → b` writes the forward rapporto on `a`'s row AND the inverse on `b`'s row (`<<` / "Coperto da" / etc.). DOCs now show all incoming extractor connections in the Scheda US form.
- **Stripped `us` numeric prefix**: `US100` → `us='100'` `unita_tipo='US'` (was `us='US100'`). SF/VSF/RSF are dual-written to `us_table` + `inventario_materiali`.
- **Period/fase auto-fill**: yEd TableNode-row period membership propagates to `us_table.periodo_iniziale`/`fase_iniziale` + `periodizzazione.cont_per`.
- **BPMN-aware classifier**: `D.NN` (BPMN data-object) → `DocumentNode`, `D.NN.MM` (plain) → `ExtractorNode` — preserves the EM 1.5 semantic distinction.
- **Idempotent re-import**: re-running the same import skips rows that are already present; no UNIQUE-collision rollback on the repeat pass.
- **USV palette**: USV nodes now render with the EM canonical blue parallelogram (was rectangle with red border).

### 5.9 yE-F multi-folder paradata (5.9.0-alpha)

Structural evolution of `yed-fastfix-5.8.5-alpha`: the Bug R B1 trade-off (one `us_table` row per occurrence, with `us='D.01_2'` / `us='D.01_3'`) has been superseded. A paradata leaf (DOC / Combinar / Extractor / property) shared across multiple yEd folders now produces **a single row** in `us_table` per canonical label, and multi-membership is preserved in a new `other_locations` column.

End-user-visible changes:

1. **New "Other locations" widget in the US/USM form**: a `QListWidget` labelled "Other locations" appears in the *Periodizzazione* tab — visible **only** when `unita_tipo` is a paradata kind (`DOC`, `Combinar`, `Extractor`, `property`). The user can select multiple activity codes; the selection is serialised as a JSON list in the new `other_locations` column.
2. **New QGIS menu item**: `Plugins → pyArchInit → Migrazioni → Aggiungi colonna other_locations (yE-F)`. Must be run **once** on every pre-existing DB to add the new column (DBs created post-5.9 already have the column).
3. **Improved yEd-aware import**: a paradata leaf that appears in N yEd folders now produces **just 1** `us_table` row (no more N rows with `_2`/`_3` suffix as in 5.8.5). The first folder encountered becomes the primary `attivita`; secondary folders are listed in `other_locations`. On **export**, N visual yEd copies are emitted (one per folder), all sharing the same canonical `node_uuid` to guarantee round-trip identity.

**Backward compatibility**: data produced by Bug R B1 in 5.8.5-alpha (rows with `_2`/`_3` suffix) remain readable without any automatic conversion. The new logic applies to new imports; legacy rows continue to behave as before.

Predecessor: see section 5.8 (`yed-fastfix-5.8.5-alpha`) for the superseded behaviour.

---

## References

- Upstream issue LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- pyarchinit repository: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
