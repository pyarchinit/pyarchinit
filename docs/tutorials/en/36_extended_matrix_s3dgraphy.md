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

## References

- Upstream issue LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- pyarchinit repository: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
