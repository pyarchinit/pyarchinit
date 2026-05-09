# AI08-F2 — Per-dimension visual style for group folders

**Status:** Design — accepted by Enzo Cocca on 2026-05-09
**Author:** Enzo Cocca
**Target tag:** `phase2-ai08f2-per-dim-visual-5.5.1-alpha`
**Predecessor tag:** `phase2-ai06-node-grouping-5.5.0-alpha` (current HEAD)
**Branch:** `Stratigraph_00001`
**Sibling specs (deferred):** AI08-F1 (hierarchical nesting), AI08-F3 (auto-layout heuristics), AI07 (LocationNodeGroup migration — see `~/.claude/projects/.../memory/project_ai07_locationnodegroup_deferral.md`)

---

## 1. Overview

AI06 ships group folders in the Extended Matrix export with a single visual style across all dimensions: `<y:Fill color="#F5F5F5">` (light grey), `<y:BorderStyle color="#000000">` (black dashed), and `<y:NodeLabel backgroundColor="#EBEBEB">` (label background grey). When the user enables multiple grouping dimensions simultaneously (e.g. `groups=["struttura", "attivita", "settore"]`), every folder looks identical and only the label text distinguishes them.

AI08-F2 adds per-dimension distinct colors to make the dimensions visually distinguishable in yEd, while keeping the EM canonical layout (`yfiles.foldertype="group"`, `<y:GroupNode>` realizer, dashed border, label position=top).

Two changes:

1. A `<y:Fill>` color per `group_kind` from a hardcoded **pastel-soft palette** with **50% alpha** (`#RRGGBBAA` with `AA=0x80`), so the epoch swimlane rows underneath stay visible through the group rectangle.
2. A `<y:BorderStyle>` color per `group_kind` (solid, no alpha — darker variant of the corresponding fill family).

The change is **opt-in by inheritance** — it only applies when a group is rendered (i.e. when `groups=[...]` is non-empty in the export). Default `groups=None` produces no folders at all, preserving the AC-2 byte-identical baseline.

---

## 2. Decisions (D1–D4)

Resolved during the brainstorming session 2026-05-09. Each decision pins behaviour testable in the acceptance criteria (§7).

### D1 — Color palette

**Choice: A — Pastel-soft (EM-coherent).** Natural extension of the AI06 `#F5F5F5` neutral grey: each dimension differs in hue but with similar luminance, so the white US nodes inside the folder remain readable.

| `group_kind` | Fill base (RGB) | Fill (RGBA 50%) | Border (solid) |
|---|---|---|---|
| `area` | `#FFE0E6` | `#FFE0E680` | `#C84A5F` |
| `struttura` | `#FFE6CC` | `#FFE6CC80` | `#C66B33` |
| `attivita` | `#FFF5CC` | `#FFF5CC80` | `#A89A33` |
| `settore` | `#E6FFCC` | `#E6FFCC80` | `#6BC633` |
| `ambient` | `#CCFFE6` | `#CCFFE680` | `#33A86B` |
| `saggio` | `#CCF5FF` | `#CCF5FF80` | `#3389A8` |
| `quad_par` | `#E0CCFF` | `#E0CCFF80` | `#6633C6` |
| `adhoc` | `#F5F5F5` | `#F5F5F580` | `#666666` |

### D2 — Which visual elements vary per dimension

**Choice: C — Fill (50% transparent) + Border colored, label background unchanged.**

- `<y:Fill color>` uses the per-dimension RGBA value (alpha `0x80`).
- `<y:BorderStyle color>` uses the per-dimension solid value.
- `<y:NodeLabel backgroundColor>` stays `#EBEBEB` (AI06 EM-canonical look).

Rationale for the alpha channel: epoch swimlane rows (background of the `<y:TableNode>`) must remain visible through the group folder rectangle, since groups can span multiple epochs (D7-A spec from AI06 reaffirmed).

yEd RGBA format: `#RRGGBBAA` (alpha last 2 hex). Verified by inspection of `~/Downloads/EM_demo_02.graphml` which contains values like `color="#FFFFFFE6"` (white with alpha `0xE6`). yEd renders this with `transparent="false"` (the alpha channel is honoured even when transparent attribute is false).

### D3 — Where the palette lives

**Choice: A — Hardcoded Python dict in `graphml_writer.py`.**

A module-level constant `_GROUP_KIND_PALETTE: dict[str, tuple[str, str]]` near `_inject_group_folders`. 8 entries × 2 colors. No JSON config file (over-engineering for 8 entries). No new module (would mirror AI05's `edge_registry` pattern but the surface is too small to justify it).

If future need arises (dark theme support, user customization), refactor to a JSON config file (path: `ext_libs/s3dgraphy/JSON_config/em_visual_rules.json`'s extension or a new `pyarchinit_group_palette.json`). The current dict is the simplest reversible form.

### D4 — Scope: which write path gets the per-dimension colors

**Choice: A — Only `graphml_writer._inject_group_folders` (Extended Matrix export).**

PyArchInit has two GraphML write paths involving group nodes:

1. **`graphml_writer._inject_group_folders`** — Output of the green "Esporta Extended Matrix" button. User-visible, opens in yEd. **F2 applies here.**
2. **`group_store._emit_group_node`** — Internal `groups_{sito}.graphml` file written by the dialog "Manage paradata" → tab Groups. Used as the s3dgraphy round-trip channel; relies on `<y:NodeLabel backgroundColor="#CCFFFF">` as the discriminator for `GraphMLImporter.determine_group_node_type_by_color()` to reconstruct as `ActivityNodeGroup`. **F2 does NOT apply here.**

Rationale: the second path is internal plumbing, not user-facing. Touching it would risk breaking the s3dgraphy importer's class reconstruction (Group A discovery from AI06). The visible benefit is in path 1, which is where users interact with the colors.

---

## 3. Components

### 3.1 `_GROUP_KIND_PALETTE` constant (new — in `graphml_writer.py`)

Module-level, near `_inject_group_folders`:

```python
# AI08-F2: per-dimension palette. Pastel-soft (D1-A) with 50% alpha
# fill (D2-C) so the epoch swimlane rows underneath stay visible,
# plus a darker solid border. Keys are group_kind values produced
# by group_projector.build_groups_from_sql + the "adhoc" kind from
# user-authored GroupStore entries.
_GROUP_KIND_PALETTE: dict[str, tuple[str, str]] = {
    # group_kind     : (fill_rgba_50pct,  border_solid)
    "area":            ("#FFE0E680",       "#C84A5F"),
    "struttura":       ("#FFE6CC80",       "#C66B33"),
    "attivita":        ("#FFF5CC80",       "#A89A33"),
    "settore":         ("#E6FFCC80",       "#6BC633"),
    "ambient":         ("#CCFFE680",       "#33A86B"),
    "saggio":          ("#CCF5FF80",       "#3389A8"),
    "quad_par":        ("#E0CCFF80",       "#6633C6"),
    "adhoc":           ("#F5F5F580",       "#666666"),
}
_GROUP_DEFAULT_FILL = "#F5F5F580"
_GROUP_DEFAULT_BORDER = "#000000"
```

### 3.2 `_inject_group_folders` modification

Replace the two hardcoded color sets:

```python
# Before AI08-F2:
fill = etree.SubElement(gn, f"{{{NS_Y}}}Fill")
fill.set("color", "#F5F5F5")
fill.set("transparent", "false")

bs = etree.SubElement(gn, f"{{{NS_Y}}}BorderStyle")
bs.set("color", "#000000")
bs.set("type", "dashed")
bs.set("width", "1.0")

# After AI08-F2:
group_kind = (getattr(group_node, "attributes", None) or {}).get("group_kind", "")
fill_rgba, border_rgb = _GROUP_KIND_PALETTE.get(
    group_kind, (_GROUP_DEFAULT_FILL, _GROUP_DEFAULT_BORDER))

fill = etree.SubElement(gn, f"{{{NS_Y}}}Fill")
fill.set("color", fill_rgba)
fill.set("transparent", "false")

bs = etree.SubElement(gn, f"{{{NS_Y}}}BorderStyle")
bs.set("color", border_rgb)
bs.set("type", "dashed")
bs.set("width", "1.0")
```

All other elements (`<y:Geometry>`, `<y:NodeLabel>`, `<y:Shape>`, `<y:State>`) are unchanged.

### 3.3 No changes elsewhere

- `group_store._emit_group_node` keeps `<y:NodeLabel backgroundColor="#CCFFFF">` (D4-A — single color in the round-trip channel for s3dgraphy importer compat).
- `group_projector.GroupSpec` already carries `group_kind`; nothing needs adding to the data flow.
- `graph_projector._merge_groups` already attaches `group_kind` to `node.attributes`; F2 just reads it.
- UI dialogs unchanged: the user picks dimensions via the existing AI06 checkboxes; colors apply automatically.
- CLI unchanged: `export --group-by struttura,attivita` produces the per-dimension colored output transparently.

---

## 4. Data flow

```
User clicks "Esporta Extended Matrix" with groups=["struttura","attivita","adhoc"]
    │
    ▼
graphml_writer.export_graphml(..., groups=[...])
    │
    ▼
GraphProjector.populate_graph(..., groups=[...])
  → _merge_groups builds ActivityNodeGroup instances with attributes["group_kind"]
    │
    ▼
Pre-export snapshot captures _group_snapshot (AI06)
    │
    ▼
GraphMLExporter writes the GraphML (drops paradata + groups)
    │
    ▼
Stage 4d: _inject_isolated_paradata_nodes (AI05)
Stage 4e: _inject_group_folders(_group_snapshot, _members_map, output_path)  (AI06)
    │
    │   For each group in snapshot:
    │     group_kind = group.attributes["group_kind"]
    │     fill_rgba, border_rgb = _GROUP_KIND_PALETTE.get(
    │                               group_kind,
    │                               (default_fill, default_border))     ← NEW (F2)
    │     <y:Fill color={fill_rgba}/>                                    ← NEW (F2)
    │     <y:BorderStyle color={border_rgb} type="dashed"/>              ← NEW (F2)
    │     <y:NodeLabel backgroundColor="#EBEBEB" .../>                   ← unchanged
    │
    ▼
Output GraphML: each group folder has its dimension's distinct colors
    │
    ▼
User opens in yEd → distinct hue per dimension, 50% alpha lets epoch rows show through
```

---

## 5. Error handling

### 5.1 Unknown `group_kind`

`_GROUP_KIND_PALETTE.get(group_kind, default)` returns the default tuple `("#F5F5F580", "#000000")` (the AI06 grey fill at 50% alpha + black border). No exception, no log. Same shape as before AI08-F2 with the only difference being the alpha channel on the fill.

This case can occur if:
- A future code path adds a new `group_kind` value but forgets to extend the palette (defensive default).
- A `groups_*.graphml` file authored by a different tool uses a non-standard `group_kind`.
- Round-trip from a corrupted file with `group_kind=""`.

### 5.2 Missing `attributes` dict on the group node

`(getattr(group_node, "attributes", None) or {}).get("group_kind", "")` returns the empty string `""`, which falls into the "unknown" branch above. Same default applied.

### 5.3 No new exception types

F2 reuses the AI06 error machinery (`GraphSyncError` / `ProjectionError` / `GroupStoreError` etc.). No new exception class is introduced — the change is too narrow to warrant its own hierarchy.

### 5.4 yEd alpha rendering

If a future yEd version drops `#RRGGBBAA` support, the colors will render as fully opaque. The `transparent="false"` attribute is preserved, so the file remains structurally valid. This is a pure visual degradation, not a data loss — `_GROUP_KIND_PALETTE` values still distinguish dimensions by hue.

---

## 6. Testing

### 6.1 Test levels

All new tests are L4 (EM template compliance), appended to the existing `tests/sync/test_groups_export_em_template.py`. No new test file needed.

### 6.2 New tests

| Test | Pins |
|---|---|
| `test_per_dimension_fill_color` | AC-1: each rendered group folder's `<y:Fill color>` matches `_GROUP_KIND_PALETTE[group_kind][0]` for the configured dimensions |
| `test_per_dimension_border_color` | AC-2: each rendered group folder's `<y:BorderStyle color>` matches `_GROUP_KIND_PALETTE[group_kind][1]` |
| `test_unknown_group_kind_falls_back_to_default` | AC-3: a group with an unrecognized `group_kind` (synthetic via direct ActivityNodeGroup instantiation) gets the default `#F5F5F580` fill + `#000000` border |

### 6.3 Critical regression guards (run after every commit)

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v       # AC-2 (AI03)
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v                       # AI04
PYTHONPATH="$PWD" python -m pytest tests/sync/test_idempotent_ingest.py -v                # AI04
PYTHONPATH="$PWD" python -m pytest tests/sync/test_cli_helper.py -v                       # AI04
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store.py -v                   # AI05
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py -v         # AI05
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_idempotent.py -v              # AI05
PYTHONPATH="$PWD" python -m pytest tests/sync/test_strategy_a_no_regression.py -v         # AI05
PYTHONPATH="$PWD" python -m pytest tests/sync/test_groups_export_em_template.py -v        # AI06
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_groups.py -v           # AI06
PYTHONPATH="$PWD" python -m pytest tests/sync/test_groups_idempotent.py -v                # AI06
```

### 6.4 Test count progression

- Baseline (post-AI06): 176 passed, 3 skipped
- Post-Group A: 179 passed, 3 skipped (+3 new tests)
- Post-Group B: 179 passed, 3 skipped (no new tests)

Final: **179 passed + 3 skipped**.

---

## 7. Acceptance criteria

| # | Criterion | Pinning test |
|---|---|---|
| AC-1 | Group folder `<y:Fill color>` matches `_GROUP_KIND_PALETTE[group_kind][0]` for each of the 8 configured `group_kind` values | `test_groups_export_em_template.py::test_per_dimension_fill_color` |
| AC-2 | Group folder `<y:BorderStyle color>` matches `_GROUP_KIND_PALETTE[group_kind][1]` | `test_groups_export_em_template.py::test_per_dimension_border_color` |
| AC-3 | Unknown / missing `group_kind` → `#F5F5F580` fill + `#000000` border (defensive default) | `test_groups_export_em_template.py::test_unknown_group_kind_falls_back_to_default` |
| AC-4 | All fill values use 50% alpha (last 2 hex == `80`) | `test_groups_export_em_template.py::test_per_dimension_fill_color` (asserts the alpha suffix) |
| AC-5 | `<y:NodeLabel backgroundColor>` stays `#EBEBEB` (D2-C: label bg unchanged) | covered by existing `test_group_visual_matches_em_template` from AI06 |
| AC-6 | AC-2 byte-identical baseline (`tests/sync/test_ai03_export_byte_identical.py`) stays green when `groups=None` | existing AI03 baseline (must remain green per Group A.2 verification) |
| AC-7 | All AI04 + AI05 + AI06 critical regression guards (11 files) stay green at every commit | per-task validation in plan |
| AC-8 | Suite `pytest tests/sync/ tests/migrations/ -q` reports ≥179 passed, 3 skipped | controller verification step |
| AC-9 | Manual smoke gate: user opens a multi-dim export in yEd and visually confirms distinct hue per dimension + 50% alpha lets epoch swimlane rows show through | manual user-driven |

---

## 8. Release plan

### Group 0 — Pre-flight (3 tasks)

- 0.1 Verify clean tree, push pending commits (HEAD = AI06 tag)
- 0.2 Create rollback tag `pre-ai08f2-palette` + push
- 0.3 Bump `metadata.txt` `5.5.0-alpha` → `5.5.1-alpha` + commit

### Group A — Palette + tests (2 tasks, +3 tests)

- A.1 TDD: 3 failing tests in `test_groups_export_em_template.py` (per-dim fill, per-dim border, unknown-kind fallback) → add `_GROUP_KIND_PALETTE` constant in `graphml_writer.py` → modify `_inject_group_folders` to use the lookup → 3 passing tests → commit. Suite at 179 passed, 3 skipped.
- A.2 Verification (no commit): AC-2 baseline + 8 AI04/AI05 critical guards + 3 AI06 group guards. All must remain green.

### Group B — Release (3 tasks)

- B.1 Dev-log entry "Phase 2 — AI08-F2 Per-dimension visual style" in `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` + commit
- B.2 CHANGELOG bilingual entry for `5.5.1-alpha` + commit
- B.3 Manual smoke gate (USER-driven): open a multi-dim export in yEd, visually confirm distinct colors + 50% alpha. Then tag `phase2-ai08f2-per-dim-visual-5.5.1-alpha` + push branch + push tag.

**Estimated totals:** ~6 commits, +80 LOC (~20 production / +60 test), 176 → 179 tests, ~2-3 hours of work.

---

## 9. Out of scope

- **AI08-F1 Hierarchical nesting** — separate spec/release (target `phase2-ai08f1-hierarchical-nesting-5.6.0-alpha` or similar)
- **AI08-F3 Auto-layout heuristics** — separate spec/release
- **AI07 LocationNodeGroup migration** — deferred (memory note `project_ai07_locationnodegroup_deferral.md`)
- **JSON config / theme support** — only if a real use case emerges. Refactor path is straightforward (~30 min).
- **Color customization in UI** — out of scope. The 8-entry hardcoded palette is the contract.
- **`group_store._emit_group_node` color changes** — D4-A explicitly excludes the round-trip channel.

---

## 10. Risks

| Risk | Sev | Mitigation |
|---|---|---|
| yEd version doesn't render `#RRGGBBAA` alpha → groups fully opaque | 🟢 low | Visual degradation only; structural validity preserved. Manual smoke gate (B.3) on user's yEd version confirms rendering before tag. |
| Color choice clashes with existing visual rules in `em_visual_rules.json` | 🟢 low | The `em_visual_rules.json` covers stratigraphic node types, not group folders. No collision. Manual smoke gate verifies. |
| Unknown `group_kind` leaks an AC-2 baseline change | 🟢 low | Default `groups=None` → no folders → no palette lookup → byte-identical to AI06. Test `test_default_groups_empty_preserves_ac2_baseline` (existing) verifies. |
| Pastel colors too light to distinguish on projector / colorblind users | 🟡 med | Each fill has a darker corresponding border (B/W-printable). Future iteration could add a high-contrast theme via D3-B JSON config refactor if requested. Not blocking. |
| Round-trip changes the rendered fill (`#FFE6CC80` → `#FFE6CC` alpha stripped) | 🟢 low | The post-processor in AI06 reads only `yfiles.foldertype="group"` + `id` prefix `grp_*` (lxml-based, color-agnostic). Round-trip preserves the colors verbatim. AI06 `test_round_trip_with_groups.py` (existing) covers this. |

---

## 11. References

### Predecessor specs

- `docs/superpowers/specs/2026-05-08-ai06-node-grouping-design.md` — AI06 (parent: introduces `_inject_group_folders` + `group_kind` discriminator)
- `docs/superpowers/specs/2026-05-08-ai05-paradata-store-design.md` — AI05 (sibling: ParadataStore + Strategy A)

### Predecessor plans

- `docs/superpowers/plans/2026-05-08-ai06-node-grouping.md` — AI06 plan (style reference for AI08-F2 plan)

### Memory notes

- `~/.claude/projects/-Users-enzo-Library-Application-Support-QGIS-QGIS3-profiles-default-python-plugins-pyarchinit/memory/project_ai06_node_grouping.md` — AI06 origin
- `~/.claude/projects/-Users-enzo-Library-Application-Support-QGIS-QGIS3-profiles-default-python-plugins-pyarchinit/memory/project_ai07_locationnodegroup_deferral.md` — AI07 deferred status
- `~/.claude/projects/-Users-enzo-Library-Application-Support-QGIS-QGIS3-profiles-default-python-plugins-pyarchinit/memory/feedback_no_claude_coauthor.md` — strict commit-author rule

### Reference files

- `~/Downloads/EM_demo_02.graphml` — verified `#RRGGBBAA` color format
- `tests/sync/fixtures/mini_volterra.sqlite` — test DB
- `tests/sync/fixtures/mini_volterra_baseline_ai03.graphml` — AC-2 baseline (must stay byte-identical)

### Production code touching points

- `modules/s3dgraphy/sync/graphml_writer.py` — `_inject_group_folders` (the only function modified)
- `tests/sync/test_groups_export_em_template.py` — 3 new L4 tests
