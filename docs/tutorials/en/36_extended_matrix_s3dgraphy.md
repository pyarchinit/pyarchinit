# Tutorial 36: Extended Matrix Export and s3dgraphy Bridge

## Introduction

Starting with **5.2.0-alpha** PyArchInit integrates a **bidirectional bridge** with the **s3dgraphy** library (Extended Matrix data model by Emanuel Demetrescu). The bridge allows you to:

- **Export** the stratigraphic diagram as Extended Matrix in **em.json**, the format EMStudio opens (the old GraphML export is retired)
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

The window states at the top what each format is for. It holds:

- **Formati** (Formats): **DOT (Graphviz) — matrice di Harris** and **em.json (Extended Matrix, per EMStudio)**, both checked to start with, plus **Matrice per fasi** (phased matrix, chronological analysis), optional. GraphML is no longer exported: the JSON of this window **is em.json**, the very file the **Extended Matrix → Esporta sito in em.json…** menu produces — same projector, same symbols.
- **Opzioni** (Options): **Controlla la sequenza stratigrafica e segnala i problemi** (check the stratigraphic sequence and report the problems). It is the only option left, and it is really read: unchecked, the check is not run. The two old boxes that spoke to yEd (auto-layout hints, period-based colouring) went away with the GraphML export.
- **Extended Matrix**: four buttons next to the export — **Apri in EMStudio** and **Vedi la matrice** (both light up after a successful em.json export; the second one draws the matrix inside QGIS, without EMStudio), **Consegna alla stanza…** and **Apri la stanza**. They are the same pyArchInit menu entries, within reach.

Pressing **Esporta** asks for the **destination folder**.

Authors, licences, embargoes and groups are handled in the **"Manage paradata"** window (§3).

### 2.2.1 Trenches: a single graph or one per trench

A group of three choices, in the same window, decides **how to split the
em.json** when the dig has several trenches:

- **Automatic**: one graph if the site has a single trench, one graph
  per trench if it has more. This is the starting choice.
- **A single graph for the whole site**: the whole dig in one graph, the
  way it has always been done.
- **One graph per trench**: **a single file**, carrying one graph for
  each trench plus one for the units that left the field empty.
  Relationships that **leave** the trench are not lost: they stay in the
  file as links between graphs (`graph.links`).

> **EMStudio 1.6.0 shows one at a time.** The file is right — the
> library's own loader reads every graph back, with no warning — but
> EMStudio opens the graph named in `active_graph_id`, the first trench,
> and has no switcher for the others. The matrix inside QGIS, **Show
> matrix**, merges them all and draws the whole dig. Measured on
> 2026-10-12 on the example site: 4 graphs (52/49/56/51 nodes), 32
> cross-trench links, 51 units in the merged matrix.

The trench is the **Saggio** field of the US form: units that have it
empty end up in a graph of their own, inside the same file.

### 2.3 Click "Esporta"

The files that are born, according to the formats checked:
- `<site>.em.json` — Extended Matrix, to open in EMStudio or to deliver to a room
- `Extended_Matrix_<site>[_<area>].dot` — Graphviz DOT, for the classic Harris matrix
- `Extended_Matrix_<site>[_<area>]_phased.json` — per-epoch view

> **Places do not enter the em.json.** Site, area and sector stay in each unit's record, but they no longer travel as group nodes with their edges: as long as the file holds even one `is_in_location` edge, EMStudio's **Matrix** view piles every unit into the first band instead of spreading them by epoch (measured on 2026-10-08 against EMStudio 1.6.0-dev.26, by bisection over five files). No information is lost — only one way of representing it.

The closing summary lists the files and, for em.json, **how many nodes and how many edges** came out, with any warnings.

> **GraphML is no longer exported**: the matrix is looked at and validated in EMStudio, which reads em.json. The temporal rows (swimlanes) of the old GraphML went away with it. GraphML survives only on the way **in**, for files drawn in yEd (§5).

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

The primary dimension follows a built-in order, with `struttura` first; `toponym` is never primary.

---

## 5. Round-trip (Import tab)

> **What can be imported**: the Import tab now also reads **em.json** — from EMStudio or from a StratiGraph node — and picks the reader from the file extension; a yEd `.graphml` is still accepted for older files. The procedure below, moving SUs between groups, concerns the yEd/GraphML route.

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
| Swimlane rows show a very long text | Older versions used the periodization Descrizione as label | Update the plugin and re-export, and/or fill **Datazione estesa** with a short name |
| Swimlane epochs are in the wrong order (e.g. Bronze Age above Late Antiquity) | Rows are sorted by **Initial Chronology**; BC years entered as positive numbers (1650 instead of -1650) sort as AD | In the Periodization form enter BC years as negative numbers and re-export. The export summary now shows a "⚠️ Periodizzazione: ..." warning listing the periods to fix |

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

## 6. Generate continuity (CON records)

In the **"Verifica rapporti"** panel — available as a tab inside the s3dgraphy import/export dialog — there is a **"Genera continuità"** button (label kept in Italian as in the plugin). For the currently selected site, this feature automatically builds the **continuity records** of the US/USM whose life spans more than one period.

### 6.1 What it does

1. It scans every US/USM in the site whose **initial period ≠ final period** (i.e. whose life spans more than one period).
2. For each one it creates or updates a continuity record named **`CON_<us>`** (e.g. `US5` → `CON_US5`).
3. The CON record **inherits** from the parent unit: site, area (plus any secondary areas), structure and the full period span (initial → final). Its description is auto-generated.
4. It writes a **reciprocal continuity relationship** on both sides: on the CON and on its parent unit.

> **The phase does not count on its own.** The rule looks at the **period**: a USM running from **2/3 to 2/4** — same period, only the phase changes — generates nothing. If your units survive from phase to phase inside the same period, tick **«anche i salti di fase»** («phase jumps too») next to the button: those jumps then count as well, provided **both** phases are filled in. A unit that does not move — same period and same phase — is never a continuity. The box starts **unticked**, and governs the preview and the writing together.

### 6.2 Idempotency

The operation is **idempotent**: re-running it does not duplicate existing records — it updates the existing `CON_<us>` if the parent unit's data has changed.

### 6.3 Dry-run preview and backup

Before writing, a **dry-run preview** is shown with the counts: how many records to **create**, to **update**, **unchanged** and how many **orphan**. Changes are applied **only after confirmation** (the "Genera" button). On apply, an automatic **database backup** is made first.

A CON record is **orphan** when its parent unit no longer spans periods (e.g. its initial and final period were made equal). By default orphans are only **flagged**; a **checkbox** ("Rimuovi anche le CON orfane") lets you opt into removing them.

**A hand-made continuity is recognised.** A CON record whose relationships name a single unit — `> 12`, or «Continuity after 12» — is that unit's continuity, whatever its name: the generator **updates** it (period span, canonical label) and the name stays its own. No second one is born: continuity is **one per unit**. If a canonical `CON_<us>` also exists, that one wins and the other remains an orphan to be decided by hand.

### 6.4 In the Extended Matrix export

The `CON_<us>` records produced this way appear in the Extended Matrix **em.json** as **continuity elements** (the outgoing GraphML export is retired, §2.3).

---

## 7. Temporal (stratigraphic) paradox check

In the **"Verifica rapporti"** panel (Check relationships — a tab of the s3dgraphy import/export dialog), the check now also flags **temporal paradoxes**: when the period/phase assigned to a unit contradicts the observed stratigraphy. Stratigraphy is the reference datum, so automatic corrections move the **periods**, not the relationships.

### 7.1 What it detects
- **Temporal inversion**: two dated units linked by an ordering relationship (e.g. US5 "covers" US7) in which the unit that is more recent in stratigraphy turns out to be entirely **older** by period.
- **Inconsistent contemporaneity**: units declared contemporaneous (physical equality / bond) but with **disjoint** chronological intervals.
- **Unevaluable**: an ordering relationship in which at least one of the two units has no datable period (flagged only, no correction).

Note on the boundary: two **adjacent periods that touch** at a single chronological point are considered overlapping → they are **not** a paradox (benefit of the doubt).

### 7.2 Automatic correction and suggestions
- When a single shift resolves the conflict, the check proposes moving the **single-period** unit that conflicts with the majority of its neighbours, choosing the period with the smallest shift; for contemporaneities with a non-datable unit it copies the period of the dated neighbour.
- In ambiguous cases — a tie, **multi-period** units (e.g. CON records), no valid period — it does not correct automatically: it provides a **"what + how" suggestion** (e.g. "Move US5 to a period ≥ 3, or US7 to a period ≤ 1, or verify the relationship").

### 7.3 Preview and backup
- The **preview** shows the proposed period changes before applying them.
- Before writing the periods, an **automatic database backup** is performed (SQLite and PostgreSQL).
- After applying, re-run the check to look for any residual paradoxes.

---

## 8. Chronology check (periodization and sheets)

In the same **"Verifica rapporti"** panel (Check relationships — a tab of the s3dgraphy import/export dialog), since version 5.13.64-alpha the check also finds and corrects **chronology** problems of the selected site. The temporal paradox check (section 7) compares the period of a unit with the stratigraphy; this one compares the periodization with itself and with the US sheets that copy it.

### 8.1 What it detects

The tree in the panel groups the problems by kind. Alongside the relationship groups there are four new ones:

| Group | What it reports | How it is handled |
|-------|-----------------|-------------------|
| **Phases with overlapping intervals** | Two periodization rows whose year ranges intersect | Manual: the panel proposes narrowing the intervals only when narrowing leaves a usable interval |
| **Sheet dating out of line** | The `datazione` field of the US sheet says something different from the `datazione_estesa` of its own period/phase | Automatic: the periodization is the source and the sheet is the copy, so the copy is rewritten from the source. An empty field is filled the same way. A US with no period is skipped, because there is nothing to copy from |
| **Periodization with start after end** | `cron_iniziale` greater than `cron_finale` | Manual: these are most likely BC dates without the minus sign — the panel proposes rewriting both years as negatives (`-1650` instead of `1650`); if it is a typo instead, swap the two values by hand |
| **Phase without years** | A phase whose years are missing or unreadable | Reported only: there is nothing to inherit them from |

An example for overlaps. The sample database has two, and neither carries a proposal: the two phases have **identical** intervals, and any narrowing would make a phase end before it begins. The panel simply tells you so; the decision (merge the phases, correct the years, leave things as they are) is the archaeologist's.

### 8.2 Automatic correction and suggestions

**Automatic corrections and proposals.** Automatic corrections are **already ticked**; proposals are **not**, and are applied only if you tick the checkbox. The rule used to be different: a problem whose fix needed a human decision could only be read. Now it has a checkbox, left unticked. This also applies to the two older relationship categories that offer a suggestion, namely the direct contradiction and the stratigraphic cycle.

To use the panel:

1. Select the **site** to verify in the panel. The verification is **per site**: it looks at the selected site and corrects only that one. On a database with ten sites this matters, because the same US numbers exist in all of them.
2. Read the **summary line** above the tree: it says how many problems there are, how many can be corrected automatically and **how many are proposals to tick by hand**.
3. Open the groups and select a problem to read its detail in the preview pane.
4. Check the checkboxes. Automatic corrections are already ticked: untick the ones you do not want to apply. Tick the proposals you agree with.
5. Apply the corrections. Before anything is written an **automatic backup** is taken (a copy of the SQLite file, or `pg_dump` for PostgreSQL into `~/pyarchinit_5/pyarchinit_DB_folder/_pga_backups`); the backup, which already existed for the period-field fixes, now also covers the chronology ones.
6. If the result is not what you wanted, press **Annulla ultimo fix** (undo last fix): the undo also reverts the corrections written to the periodization table.

### 8.3 Preview and backup

**The preview shows the computed date.** For each unit named by a problem, the preview pane shows its computed date in a line like this:

`US 4 · 1500–1549 · epoca · has_first_epoch → epoch_2_2`

The line gives, in order, the span of years, the rule that produced it, and the relation the constraint travelled along together with the node it came from. When the two ends of the span come from different routes, each end is labelled (`inizio …` and `fine …`), so a date is never attributed to the wrong relation. Today, in a normal database, every unit takes its dates from its own period, so most lines will read `epoca`. The point of the line is not to surprise you, but to let you see **where** a date comes from.

---

## 9. How to read the arcs of the matrix

Some choices in the matrix drawing may look odd, but they are not errors:

- **An arrow never passes under a node.** When the arrival column is occupied, the arrow enters the box **from the side**: this is normal.
- **Equality is not an overlap.** A «Uguale a» (Same as) or «Si lega a» (Bonds with) relationship puts the two units on the **same row**, side by side, joined by **two horizontal lines** (the equals sign) **with no arrowhead**.
- **Redundant arcs are not drawn.** If SU 1 covers 2 and 2 covers 3, the arrow from 1 to 3 does not appear, because it adds nothing. Inside a **cycle**, however, all arcs stay, because a cycle is an error you need to see.
- **The lines say which relationship they are.** Grey and solid: the sequence (covers, fills, abuts). **Dotted green**: a cut (`Taglia` / `Tagliato da`), whatever the stratigraphic definition and in any language. **Thick and black**: continuity — a small black diamond with no printed name (the name shows on hover), in its unit's column, so the line is straight. **Red**: an arrow climbing back up the bands, i.e. a contradiction between stratigraphy and chronology; a climbing cut is red **and** stays dotted.
- **Paradata are never a solid line.** They take colour and stroke from the Extended Matrix rules (`em_visual_rules.json`): brown-red dotted «extracted from», orange dashed «data provenance», gold dashed «property», grey dashed «generic connection», tomato dashed «combines» (solid in the file: the one deviation, because an arc towards a document must not look like an overlap).
- **A brown border is masonry.** USM units — WSU, MSE, UEM, USZ, ΤΣΜ in the other languages — have the same box as the US, with a brown border instead of red.

---

## 10. Narrative with AI

Starting with **5.13.106-alpha**, the matrix panel inside QGIS (§2.2, "Vedi la matrice") has two tabs in its right-hand column: **Units** (*Unità*) — the details of the chosen unit, the zoom on the geometry and the media, as before — and **Narrative** (*Narrativa*), which is new. The Narrative tab has an AI write the **story of the site**, one chapter per epoch, and then lets you read it, have a person endorse it and export it to HTML or DOCX. It reads and writes **the same em.json** that EMStudio opens, in the s3dgraphy library format: the narrative you see here is the one EMStudio shows in its *Narrative* tab.

> **No new settings.** The tab has no configuration window of its own: it uses the AI you have already set up elsewhere in pyArchInit (§10.2).

> **The AI writes drafts, not final texts.** Every paragraph written by the model stays an "AI draft" until a person endorses it (§10.6), and in exported documents it carries the ⚠ mark.

The names of the tabs and buttons of the Narrative tab exist in Italian and in English: **they are in Italian if QGIS is in Italian, in English with any other language**. Both are always given here. The plugin's menu entries and dialog windows (such as "Vedi la matrice…" or the three buttons of §10.9) are, instead, in Italian only; the English translation is given in brackets.

### 10.1 Opening the Narrative tab

1. Open the menu **Plugins → pyArchInit - Archaeological GIS Tools** and choose the entry **Extended Matrix → Vedi la matrice…** (View the matrix).
2. Choose the **site**.
3. If the site has **trenches** (*saggi*), pyArchInit asks "Il sito ha N saggi. Come divido il file?" (The site has N trenches. How do I split the file?) with two answers: "Un grafo per ogni saggio (…)" (one graph per trench), the default, or "Un grafo solo per tutto il sito" (a single graph for the whole site). It is the same choice as in §2.2.1 and in the "Esporta sito in em.json…" entry: the two entries write the **same file**, with the same shape.
4. pyArchInit exports the site from the database to `<home>/pyarchinit_EM_folder/<site>.em.json` — `<home>` is `~/pyarchinit_5`, or the folder named by the `PYARCHINIT_HOME` environment variable — and opens the panel **"Matrice — `<site>`"**, docked to the right of the QGIS window. The file name is the site name, with special characters replaced by "_" (for example "Scavo 1" becomes `Scavo_1.em.json`).
5. In the right-hand column of the panel, click the **Narrative** tab.

<!-- IMMAGINE: Screenshot of the Plugins → pyArchInit - Archaeological GIS Tools menu with the entry "Extended Matrix → Vedi la matrice…" -->
![View the matrix menu](images/36_extended_matrix_s3dgraphy/01_menu_vedi_matrice.png)
*Figure 1: The "Extended Matrix → Vedi la matrice…" entry in the plugin menu*

<!-- IMMAGINE: Screenshot of the trench question with the two answers -->
![Trench question](images/36_extended_matrix_s3dgraphy/02_domanda_saggi.png)
*Figure 2: The trench question: one graph per trench or a single graph*

<!-- IMMAGINE: Screenshot of the matrix panel docked on the right, with the Units and Narrative tabs -->
![Panel with two tabs](images/36_extended_matrix_s3dgraphy/03_pannello_due_schede.png)
*Figure 3: The matrix panel with the Units and Narrative tabs*

The file is **one per site and stays on disk**: it no longer lives in a temporary folder. It is the file EMStudio opens, and it is where the narrative is written. Every time you choose "Vedi la matrice…" the site is **exported again from the database** and the file is rewritten; the narrative already in it is kept (§10.8).

You can also reach the tab from two other places:

- from the **Extended Matrix → Esporta sito in em.json…** entry (Export site to em.json), which ends by offering the "Narrativa con l'AI" button (§10.9);
- from the **Vedi la matrice** button of the "Esporta Extended Matrix" window of the US form (§2.2): it opens the same panel on the file you have just exported, in the folder you chose.

### 10.2 Which AI is used

At the top of the Narrative tab a line says which AI it will use: **"Model: `<model>` (`<where it comes from>`)"**, followed by the reminder about EMStudio. If it finds none, it says **"No AI configured: set it in the US form with “Report” (AI provider) or with “Query AI Database”."** and the **Generate with AI** and **Regenerate chapter** buttons stay off.

The tab reads the AI settings **already saved** by the other pyArchInit windows, in this order, and uses the **first** one that has a model and — for network providers — the API key:

| # | Where it is set | What the tab calls it (en / it) |
|---|-----------------|----------------------------------|
| 1 | US form, "Report" button → "Generatore di Report" window (Report generator), "Provider AI" group | Report generator of the US form / Generatore di Report della scheda US |
| 2 | US form, "Query AI Database" button | Query AI Database / Query AI Database |
| 3 | palimpsestr window, "Report AI (analisi descrittiva)…" button, "Provider AI" selector | Palimpsest report / Relazione Palimpsest |
| 4 | "Generazione SQL con AI" window (text to SQL: see tutorial 30) | Text to SQL / Testo in SQL |

The providers are those of the "Provider AI" selectors: **OpenAI** and **Anthropic (Claude)** over the network, with the API key typed in the "API key" field; **Ollama** and **LM Studio** on your own computer, with no key. The selector saves your choice as soon as you change it. If you want another model, change it in the window the tab names in brackets (or in one that comes earlier in the list). The tab re-reads the settings **when the panel opens**: after changing them, open the matrix again.

### 10.3 The Narrative tab

```
┌─ Units ─┬─ Narrative ────────────────────────────────────────────┐
│ Model: <model> (<where it comes from>) · If EMStudio has the     │
│ file open, close it first: the last writer wins.                 │
├──────────────────────────────────────────────────────────────────┤
│ Presentation — to be written                                     │
│ Early 15th century — AI draft                                    │
│ 15th century — endorsed                                          │
│ Modern age — AI draft, truncated                                 │
├──────────────────────────────────────────────────────────────────┤
│ The text of the chosen chapter, units quoted by name.            │
├──────────────────────────────────────────────────────────────────┤
│ Chapter 3 of 9 · 15th century  *                                 │
│ [Generate with AI]  [Regenerate chapter]  [Endorse…]             │
│ [Prepare the chapters]  [Export…]  [Open in EMStudio]  [Cancel]* │
└──────────────────────────────────────────────────────────────────┘
```

\* The progress line and the "Cancel" button are visible only while the AI is writing. In this diagram the list rows are those of the sample site.

<!-- IMMAGINE: Screenshot of the Narrative tab with the chapter list, the text of the chosen chapter and the six buttons -->
![Narrative tab](images/36_extended_matrix_s3dgraphy/04_scheda_narrativa.png)
*Figure 4: The Narrative tab*

From top to bottom:

- **the status line**: the model in use (§10.2) and the reminder *"If EMStudio has the file open, close it first: the last writer wins."*;
- **the chapter list**, one row per chapter: *Title — state*. With the per-trench export (§2.2.1) each trench has its own narrative and each row is preceded by the trench name in square brackets, for example `[Saggio A] 15th century — AI draft`;
- **the text of the chosen chapter**: the prose, with units quoted by name. If the chapter has no prose yet you see its placeholder "[to be written: …]";
- **the progress line**, only while generating: "Chapter 3 of 9 · 15th century";
- **the buttons**, in two rows.

The result of every operation appears in the QGIS message bar, titled "Narrative".

When the file **has no narrative yet** the list is empty and a text says: *"No narrative in the file: “Prepare the chapters” builds the outline (N chapters over epochs and activities), “Generate with AI” writes it."*

#### The states of a chapter

| State (en / it) | What it means |
|-----------------|---------------|
| **to be written** / da scrivere | The chapter holds only the "[to be written: …]" placeholder. |
| **AI draft** / bozza AI | There is prose written by the model that no person has endorsed. One paragraph is enough: if the chapter has even a single unendorsed paragraph, this is its state, even if other prose is present. |
| **endorsed** / convalidato | All the AI's prose has been endorsed by a person. |
| **written** / scritto | Prose written by a person (in EMStudio). |
| **truncated** / troncato | Added to the state (for example "AI draft, truncated"): the model stopped because it reached the length limit, and the text ends halfway. |

#### The buttons

| Button (en) | In Italian | What it does |
|-------------|------------|--------------|
| **Generate with AI** | Genera con l'AI | Writes, **one at a time**, all the epoch (and activity) chapters still "to be written"; those already written are left alone. If there is no narrative yet, it first builds the outline. Shows the progress and the **Cancel** button. On only with a file open and an AI set up. |
| **Regenerate chapter** | Rigenera capitolo | Rewrites **the chapter chosen** in the list (with several trenches, only the one of the chosen trench): the unendorsed AI draft is replaced — but only once the model has answered: if the call fails, the earlier draft stays — and blocks already endorsed stay. It turns on when you choose an epoch or activity chapter and an AI is set up; for "Presentation" and "Where it is" it stays off. |
| **Endorse…** | Convalida… | Opens a menu with "This chapter" and "All chapters", then asks who endorses (§10.6). On when there is a narrative. |
| **Prepare the chapters** | Prepara i capitoli | Builds **only the outline** of the chapters, without AI: it works even if no AI is set up, so you can write by hand in EMStudio. It does not touch prose already written, and adds the chapters of new epochs. Result: "Chapters prepared: N." |
| **Export…** | Esporta… | Saves the narrative as HTML or DOCX (§10.7). On when there is a narrative. |
| **Open in EMStudio** | Apri in EMStudio | Opens the em.json in EMStudio. If EMStudio is not there, the message bar points to the menu entry **Extended Matrix → Installa EMStudio…** (Install EMStudio). |
| **Cancel** | Annulla | Appears only while generating: the AI stops **after the chapter in progress** and what has been written is saved. |

While generating, every button is off except **Cancel**.

### 10.4 What the AI writes

**Which chapters.** The outline is the one from the s3dgraphy library (the "site_story" template):

- **Presentation** and **Where it is** are canonical chapters: they stay as "[to be written: …]" placeholders to be written by hand in EMStudio, because the graph holds nothing to write them from without inventing. "Where it is" exists only if the graph carries a geographic position. The AI does not generate them.
- **One chapter per epoch** (period/phase) that has units, from the oldest to the most recent. The title is the name of the epoch, that is the "Datazione estesa" (extended dating) of the periodization; if it is missing, a generic name such as "Period 8 Phase 1" comes out: fill it in on the Periodization form to get readable titles. A unit appears in the chapter of the epoch where it is born and in those of the epochs where it survives.
- **One chapter per activity**, if the graph contains activity groups. A site exported from the database normally has none — the Activity field of the US form travels as a property of the unit — and then the chapters are the epoch ones.

**What the model receives.** For each chapter, a *briefing* with, for every unit: name, type and description; the filled-in fields of the US form (stratigraphic and interpretive definition, interpretation, period and phase, dating, activity, structure, trench, room, sector, area); the epochs; **the stratigraphic relationships** with the other units (covers, cuts, fills, abuts, equal to…) with their names; and, if there are any, the linked documentary sources. Units are listed **from the oldest to the most recent**, following the relationships. Beyond **80 units** per chapter the briefing is cut to the first 80. It also has a length cap (about 25,000 characters): beyond it, the long texts of the forms are shortened, repeated relationships and evidence chains are dropped and, if that is still not enough, the most recent units are left out. In both cases the model is told how many units are missing.

**The rules.** The model receives the library's five rules: write only what the context supports (no invented dates, materials, functions or events); keep uncertainty (a virtual unit is a hypothesis, not a fact); cite no source that is not there; write continuous prose, with no lists or headings; say openly when the context is too thin. It asks for one to three paragraphs.

**The language.** The prose is in the **language of the narrative**, which is fixed when the outline is first created: **Italian if QGIS is in Italian at that moment, English with any other language** (the model receives its instructions only in these two languages). A narrative that already exists keeps its language even if you later change the QGIS language. The same goes for the titles of the canonical chapters and for the placeholders.

**How it is saved.** In the library format, the one EMStudio reads: a narrative node (`NarrativeNode`) holding the chapters; every paragraph written by the model is an "AI draft" block attributed to that model's **AI author**; the **prompt** used is registered as an extractor linked to the sources, so you can trace what was asked. The units quoted in the text are **mentions** (`[[name]]`): in the file they stay linked to the unit's node, and in the tab and in the exports they appear with its name. A mention that matches no unit in the graph is reduced to plain words, without brackets.

**Costs and times.** The model is called **once per chapter**. With a network provider each call has a cost and a waiting time (in trials with a network model, a few tens of seconds per chapter: a site with about ten epochs takes a few minutes); with Ollama or LM Studio nothing is paid, but times depend on your computer.

### 10.5 Step by step

1. Open the site's matrix (§10.1) and click the **Narrative** tab. Check at the top **which model** it will use.
2. **Close EMStudio** if it has the file open: pyArchInit and EMStudio write the same file, and whoever writes last wins.
3. Optional: **Prepare the chapters** to see the outline, without AI.
4. Click **Generate with AI**. Watch the progress ("Chapter 3 of 9 · …"); you can keep using QGIS. At the end the message bar says, for example, *"7 chapters generated, 1 failed: Modern age — …"* (with *"(cancelled)"* if you cancelled) and the list reloads: the chapters written are "AI draft".
5. **Read**: pick one chapter after the other and read the text under the list. Check it against the stratigraphy: it is a draft built from the data of the US form.
6. If a chapter does not convince you, pick its row and click **Regenerate chapter**. The new draft **replaces** the previous unendorsed one: if you want to keep the earlier version, export it first. If a chapter is "truncated", regenerate it **before** endorsing.
7. When a chapter is right, click **Endorse…** (§10.6).
8. **Export…** to HTML or DOCX (§10.7), or **Open in EMStudio** to write "Presentation" and "Where it is" by hand and polish the rest.
9. Later you can open the matrix again: the narrative stays (§10.8).

<!-- IMMAGINE: Screenshot of generation in progress: the progress line "Chapter 3 of 9 · …" and the Cancel button -->
![Generation in progress](images/36_extended_matrix_s3dgraphy/05_generazione_in_corso.png)
*Figure 5: Generation in progress, with the progress line and the Cancel button*

A chapter that fails does not stop the others: the summary says which. To retry, just click **Generate with AI** again, which writes only the chapters still "to be written".

### 10.6 Endorsing: who signs

Endorsing means that a **person** takes responsibility for the text the model wrote. It never happens on its own: not by generating, not by saving.

1. Click **Endorse…**. A small menu opens: **"This chapter"** — on only if the chosen chapter is an "AI draft" — or **"All chapters"**, that is all the AI drafts not yet endorsed, in every graph of the file.
2. A window asks **"Who endorses? Pick an author or type a new name."** The list holds the **human authors already in the graph** — the people named in the US form as compiler (*schedatore*), US director and US supervisor — and you can type a new name, which becomes a new author of the graph (with several trenches, in every graph that has drafts to sign).
3. The message bar says **"N blocks endorsed by `<name>`."**, or "Nothing to endorse." The file is saved.

<!-- IMMAGINE: Screenshot of the Endorse… menu ("This chapter" / "All chapters") and of the window for choosing the author -->
![Endorse](images/36_extended_matrix_s3dgraphy/06_convalida.png)
*Figure 6: Endorse: the menu and the choice of author*

The blocks go from "AI draft" to "endorsed". In the exported document the person appears among those responsible ("a cura di", edited by) and the model as assistant ("con l'assistenza di", with the assistance of), and endorsed paragraphs no longer carry the ⚠ mark. Regenerating does not delete endorsed blocks: a signature is an act, and is not lost by rewriting.

### 10.7 Exporting to HTML or DOCX

Click **Export…**: the save window opens with two formats, "HTML page (\*.html)" and "Word document (\*.docx)". The suggested name is `<site>_narrativa.html`, in the folder of the em.json; if you type the extension yourself (`.html` or `.docx`) it wins, otherwise the chosen format decides. With the per-trench export **one file per trench** is written, adding the trench name to the name you chose. The message bar confirms: "Narrative exported to `<path>`".

The document contains:

- the title of the narrative (for example "Scavo archeologico — the story of the site"), those responsible ("a cura di") and the model as assistant ("con l'assistenza di");
- for each chapter the prose, with the units quoted by their name, and the list of the units of the chapter;
- at the end the **Fonti** (sources) section: the documents the story rests on and the "Prompt" entry, which points to the prompt recorded in the file.

Things worth knowing:

- **unendorsed drafts go in**, each preceded by "⚠︎ non validato da una persona" (not validated by a person), and the header says how many blocks are in this state. For a document without marks, endorse first (§10.6);
- **all chapters go in**, even those still "to be written": their "[to be written: …]" placeholder stays in the text;
- figures an author planned in EMStudio (for example the matrix of an epoch) are not drawn by pyArchInit's export: a placeholder stays in the document;
- the HTML is a single, self-contained file; the DOCX opens with Word or LibreOffice and needs the `python-docx` package, one of the plugin's requirements.

<!-- IMMAGINE: Screenshot of the exported HTML document: a chapter with a draft preceded by "⚠︎ non validato da una persona" -->
![Exported HTML document](images/36_extended_matrix_s3dgraphy/07_documento_html.png)
*Figure 7: The exported HTML document, with an unendorsed draft marked*

### 10.8 Exporting the site again: the narrative stays

Exporting the site again from the database — with **Vedi la matrice…**, with **Esporta sito in em.json…** or with the "Esporta Extended Matrix" window of the US form — **keeps the narrative** already in the destination file: prose, endorsements, AI author and prompts. Epochs born in the meantime receive a chapter "to be written". A notice says so: **"Narrative kept from the previous file (N chapters)."** You see it in the message bar with "Vedi la matrice…", in the summary of the "Esporta Extended Matrix" window and, with "Esporta sito in em.json…", in the details of the final window.

**Other changes** made to the file in EMStudio — node positions, rewritten descriptions — **do not survive**, as before: the file is regenerated from the database. Only the narrative is kept.

Before rewriting a file that holds a narrative, pyArchInit makes a **safety copy** next to it: `<site>.em.json.bak` (every new export replaces the previous copy).

If you change the shape of the file — from "Un grafo per ogni saggio" to "Un grafo solo per tutto il sito", or the other way round — the graphs change names and the narrative **cannot travel** into the new file. A notice says so: *"The previous file's narrative (graphs: …) did not travel into the new file (graphs: …): the file shape changed. Backup copy in …"*. The text is not lost: it is in the `.bak` copy, which however is replaced by the next export of a file that holds a narrative — put it somewhere safe. To recover it, rename the copy to `.em.json` and export again with the earlier choice.

If the previous file cannot be read (for example a file left half-written), the export goes ahead anyway: the unreadable file is **renamed** `<site>.em.json.broken` and a notice says *"The previous file cannot be read (…): its narrative, if any, was not kept."*

> **The narrative is not in the pyArchInit database: it lives only in the em.json.** A database backup does not copy it. Copy the `pyarchinit_EM_folder` folder from time to time.

### 10.9 From the "Esporta sito in em.json…" entry

The entry **Extended Matrix → Esporta sito in em.json…** asks the same trench question and writes the same file `<site>.em.json` in `pyarchinit_EM_folder`. At the end it shows "Esportato `<path>`" (Exported), with the counts of nodes, edges and notices (the text of the notices is in the details of the window), and **three buttons**:

| Button | What it does |
|--------|--------------|
| **Apri in EMStudio** (Open in EMStudio) | Opens the file in EMStudio; if it is not installed, it offers to install it. |
| **Narrativa con l'AI** (Narrative with AI) | Appears **only if an AI is set up** (§10.2): opens the matrix panel already on the Narrative tab. |
| **Chiudi** (Close) | Closes the window. |

<!-- IMMAGINE: Screenshot of the final window of "Esporta sito in em.json…" with the three buttons -->
![Export site to em.json: three buttons](images/36_extended_matrix_s3dgraphy/08_esporta_tre_bottoni.png)
*Figure 8: The final window of "Esporta sito in em.json…"*

### 10.10 Warnings

- **Close EMStudio before generating or endorsing.** If EMStudio has the file open, whoever writes last wins. With several trenches EMStudio shows one graph at a time (note in §2.2.1): the Narrative tab shows them all.
- **An AI writes only from what it finds in the graph, and it can be wrong.** The rules restrain it, they do not make it infallible: read every chapter before endorsing it.
- **With a network provider the data leaves your computer.** The briefing of each chapter (names, definitions, descriptions and relationships of the units) is sent to the chosen service; with Ollama or LM Studio it stays local.
- **The file is written at the end.** Generation saves when it finishes, even if you cancelled it: do not close QGIS while the AI is writing. Saving is safe: the file is written alongside, read back, and only then replaces the real one; if anything goes wrong, **the previous file stays as it was**.
- **Do not open the matrix again while the AI is writing.** The tab stays on the previous file and warns: *"Generation in progress: wait for it to finish, or press Cancel, before changing file."*
- **The text is edited in EMStudio**, not in pyArchInit.
- The narrative and the nodes that carry it (AI author, prompts) **do not appear in the matrix drawing**.

### 10.11 Troubleshooting

| Message (en / it) | Cause | Remedy |
|-------------------|-------|--------|
| "No AI configured…" / «Nessuna AI impostata…» | None of the four windows of §10.2 has a model (and, for OpenAI and Anthropic, the API key). | Set provider and model — and the key — in one of those windows, then **open the matrix again**: the tab re-reads the settings only when it opens. Even without an AI you can prepare the chapters, endorse, export and open EMStudio. |
| "No narrative in the file…" / «Nessuna narrativa nel file…» | The file has no narrative yet (normal the first time). | Click **Prepare the chapters** (outline) or **Generate with AI** (outline and prose). The number N counts the epoch and activity chapters the outline will have (an epoch with no units gets none); the "Chapters prepared" message also counts "Presentation" and, if present, "Where it is". |
| "EMStudio is not installed…" / «EMStudio non risulta installato…» | The program was not found on the computer. | Use the menu entry **Extended Matrix → Installa EMStudio…** (it has this name with any QGIS language). |
| "truncated" / «troncato» next to the state | The model stopped at the length limit and the text ends halfway. | Before endorsing, **Regenerate chapter**; if it happens again, finish the chapter in EMStudio. |
| "N chapters generated, M failed: `<title>` — `<reason>`" / «N capitoli generati, M falliti: …» | The provider refused the request (invalid key, quota, model not available) or the local server does not answer. "the model wrote nothing" means the reply was empty. | Remove the cause and click **Generate with AI** again: it writes only the chapters left "to be written". |
| "The previous file cannot be read (…)" / «Il file precedente non si legge (…)» | At re-export the existing file was not a readable em.json. | The export went ahead: the unreadable file was kept next to the new one as `….broken`, and the narrative it held, if any, did not travel into the new file. If you need it, recover it from that file or from a backup. |
| "The previous file's narrative (graphs: …) did not travel into the new file…" / «La narrativa del file precedente (grafi: …) non è passata nel file nuovo…» | You changed the shape of the file (one graph per trench ↔ a single graph): the graphs have different names and the narrative cannot travel. | The earlier file is in the `.bak` copy: rename it to `.em.json` and export again with the earlier choice. |
| "Could not write … The previous file is intact." / «Non sono riuscito a scrivere … Il file precedente è intatto.» | Saving failed (full disk, locked file, permissions). | Fix it and repeat: the chapters generated in that session had not been saved. |
| "DocX export needs python-docx — install the extra: …" (always in English) | The `python-docx` package is not installed in QGIS's Python: it is needed only for DOCX. | Install `python-docx` (it is one of the plugin's requirements), or export to HTML, which needs nothing. |

---

## References

- Upstream issue LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- pyarchinit repository: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
