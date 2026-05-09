# AI08-F2 — Per-dimension visual style for group folders: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Distinguish the 8 grouping dimensions (`area`, `struttura`, `attivita`, `settore`, `ambient`, `saggio`, `quad_par`, `adhoc`) in the Extended Matrix export by giving each `<y:Fill>` a 50%-alpha pastel color and each `<y:BorderStyle>` a corresponding solid darker color, while keeping the AI06 EM-canonical layout (label background `#EBEBEB`, dashed border, position=top) — release `5.5.1-alpha`.

**Architecture:** A new module-level constant `_GROUP_KIND_PALETTE: dict[str, tuple[str, str]]` in `modules/s3dgraphy/sync/graphml_writer.py`, mapping each `group_kind` to a `(fill_rgba_50pct, border_solid)` tuple. The Stage 4e post-processor `_inject_group_folders` reads `group_kind` from the snapshot's `attributes` dict and looks up the palette to populate `<y:Fill color>` and `<y:BorderStyle color>`. Unknown / missing `group_kind` falls back to `("#F5F5F580", "#000000")` (AI06 grey at 50% alpha + black border). All other elements (label background, geometry, shape, state) unchanged.

**Tech Stack:** Python 3.9+, lxml (transitive — already in use), pytest. **No new dependencies, no new modules, no new exception types.**

**Spec source of truth:** `docs/superpowers/specs/2026-05-09-ai08f2-per-dim-visual-design.md` (commit `ecfb1788`)

**Predecessor releases:**
- AI06: tag `phase2-ai06-node-grouping-5.5.0-alpha` (current HEAD baseline)

**Memory notes (consult before refactoring):**
- `~/.claude/projects/.../memory/project_ai06_node_grouping.md` — AI06 origin
- `~/.claude/projects/.../memory/project_ai07_locationnodegroup_deferral.md` — AI07 deferred status (reactivation deadline 2026-05-23)
- `~/.claude/projects/.../memory/feedback_no_claude_coauthor.md` — strict commit-author rule

**Commit-message rule:** Never include `Co-Authored-By: Claude …` trailers. Sole author is Enzo Cocca. Every HEREDOC in this plan is already trailer-free; do not re-add it. After each commit run `git log -1 --format=%B HEAD | grep -c Co-Authored-By` — must return `0`.

---

## File Structure

### Modified

| Path | Δ LOC | Why |
|---|---|---|
| `modules/s3dgraphy/sync/graphml_writer.py` | +18 / -2 | (1) Add `_GROUP_KIND_PALETTE` constant + `_GROUP_DEFAULT_FILL` + `_GROUP_DEFAULT_BORDER` near `_inject_group_folders`. (2) Replace 2 hardcoded color sets (`fill.set("color", "#F5F5F5")` and `bs.set("color", "#000000")`) at lines ~1431/1435 with `_GROUP_KIND_PALETTE.get(group_kind, default)` lookup. |
| `tests/sync/test_groups_export_em_template.py` | +120 (3 new tests) | Append `test_per_dimension_fill_color`, `test_per_dimension_border_color`, `test_unknown_group_kind_falls_back_to_default`. |
| `metadata.txt` | 1 line | Bump `version=5.5.0-alpha` → `version=5.5.1-alpha`. |
| `dev_logs/CHANGELOG.md` | +18 | Prepend `## [5.5.1-alpha] - 2026-05-09` bilingual section. |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | +30 | New "Phase 2 — AI08-F2 Per-dimension visual style" section. |

### Explicitly NOT touched (out of scope per spec §9)

- `modules/s3dgraphy/sync/group_store.py` — D4-A: `_emit_group_node` keeps `<y:NodeLabel backgroundColor="#CCFFFF">` as the s3dgraphy round-trip discriminator. F2 does NOT touch the round-trip channel.
- `modules/s3dgraphy/sync/group_projector.py` — F2 only consumes `group_kind`; nothing changes here.
- `modules/s3dgraphy/sync/graph_projector.py` — `_merge_groups` already attaches `attributes["group_kind"]`; F2 just reads it.
- `gui/dialog_paradata_manager.py` + `modules/s3dgraphy/s3dgraphy_dot_bridge.py` — UI unchanged (the user picks dimensions via existing AI06 checkboxes; colors apply automatically).
- `scripts/s3dgraphy_sync.py` — CLI unchanged.
- `tests/sync/fixtures/mini_volterra_baseline_ai03.graphml` — AC-2 baseline byte-identical (default `groups=None` means no folders are emitted, so the palette is never consulted).
- `requirements.txt` — no new dependencies.

---

## Test strategy

All new tests live in the **existing** file `tests/sync/test_groups_export_em_template.py` (already created in AI06 Group D.1, currently has 5 tests). Three new tests appended:

- **L4 EM template compliance** (same level as AI06's existing tests):
  - `test_per_dimension_fill_color` — pins AC-1 + AC-4 (per-dim fill matches palette + alpha suffix is `80`)
  - `test_per_dimension_border_color` — pins AC-2 (per-dim border matches palette)
  - `test_unknown_group_kind_falls_back_to_default` — pins AC-3 (defensive default)

**Critical regression guards** (run after every commit Group A):

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v       # AC-6 (AI03)
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

Decision-pinning matrix:

| Decision / Acceptance | Pinning test |
|---|---|
| D1 palette (8 entries) | `test_per_dimension_fill_color` (asserts each of the 8 entries) |
| D2-C fill 50% alpha + border colored | `test_per_dimension_fill_color` (alpha) + `test_per_dimension_border_color` |
| D2-C label background unchanged | existing `test_group_visual_matches_em_template` (AI06) — must stay green |
| D3 hardcoded dict location | `test_per_dimension_fill_color` imports `_GROUP_KIND_PALETTE` from `graphml_writer` |
| D4-A only export path | `test_groups_dialog_smoke.py` (AI06, indirectly: GroupStore output unchanged) |
| AC-3 unknown kind fallback | `test_unknown_group_kind_falls_back_to_default` |
| AC-6 AC-2 byte-identical | existing `test_ai03_export_byte_identical.py` |

Test count progression:
- Baseline (post-AI06): 176 passed, 3 skipped
- Post-Group A: 179 passed, 3 skipped (+3 new tests)
- Post-Group B: 179 passed, 3 skipped (no new tests)

---

## Group 0 — Pre-flight & rollback safety

### Task 0.1: Verify clean starting point + push pending commits

**Files:** none (git operation)

- [ ] **Step 1: Confirm starting point**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git status --short | grep -vE '^\?\?'
git log --oneline -3
git rev-list --left-right --count HEAD...@{u}
```

Expected: tracked changes empty, last commit is `ecfb1788 docs(spec): AI08-F2 …` or later, `1\t0` ahead-behind (the spec commit is unpushed).

- [ ] **Step 2: Push the spec commit**

```bash
git push origin Stratigraph_00001
```

Expected: 1 commit pushed (`ecfb1788`).

- [ ] **Step 3: Verify**

```bash
git rev-list --left-right --count HEAD...@{u}
```

Expected: `0\t0`.

### Task 0.2: Create AI08-F2 rollback tag

**Files:** none (git operation)

- [ ] **Step 1: Create annotated tag**

```bash
git tag -a pre-ai08f2-palette -m "Pre-flight rollback tag for AI08-F2 / per-dimension visual style"
git tag -l | grep -E "pre-ai0|phase2"
```

Expected output (8 lines):
```
phase2-ai03-graphml-delegation-5.2.0-alpha
phase2-ai04-bridge-bidirectional-5.3.0-alpha
phase2-ai05-paradata-store-5.4.0-alpha
phase2-ai06-node-grouping-5.5.0-alpha
pre-ai03-graphml-delegation
pre-ai04-bridge
pre-ai05-paradata
pre-ai06-grouping
pre-ai08f2-palette
```

(9 lines total — 4 phase2 + 5 pre-ai0X.)

- [ ] **Step 2: Push the tag**

```bash
git push origin pre-ai08f2-palette
git ls-remote --tags origin 2>&1 | grep "refs/tags/pre-ai08f2-palette$"
```

Expected: 1 matching line.

### Task 0.3: Bump version to 5.5.1-alpha

**Files:**
- Modify: `metadata.txt`

- [ ] **Step 1: Read current version**

```bash
grep -n "^version=" metadata.txt
```

Expected: `version=5.5.0-alpha`.

- [ ] **Step 2: Edit `metadata.txt` — change exactly the line `version=5.5.0-alpha` to `version=5.5.1-alpha`**

Use the Edit tool. Do not touch anything else.

- [ ] **Step 3: Verify**

```bash
grep "^version=" metadata.txt
```

Expected: `version=5.5.1-alpha`.

- [ ] **Step 4: Run baseline sanity tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `176 passed, 3 skipped`.

- [ ] **Step 5: Commit**

```bash
git add metadata.txt
git commit -m "$(cat <<'EOF'
chore(metadata): bump version to 5.5.1-alpha for AI08-F2

Phase 2 / AI08-F2 — per-dimension visual style for group folders
in the Extended Matrix export. Adds a hardcoded
_GROUP_KIND_PALETTE in graphml_writer.py mapping each of the 8
dimensions (area / struttura / attivita / settore / ambient /
saggio / quad_par / adhoc) to a (fill_rgba_50pct, border_solid)
tuple. The AI06 single-color rendering becomes per-dimension
distinct, with 50% alpha fill so epoch swimlane rows stay visible
through the group rectangle.

Target tag: phase2-ai08f2-per-dim-visual-5.5.1-alpha.

Spec: docs/superpowers/specs/2026-05-09-ai08f2-per-dim-visual-design.md
Plan: docs/superpowers/plans/2026-05-09-ai08f2-per-dim-visual.md
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

---

## Group A — Palette + tests

### Task A.1: TDD — failing tests + implementation + commit

**Files:**
- Modify: `tests/sync/test_groups_export_em_template.py` (append 3 tests)
- Modify: `modules/s3dgraphy/sync/graphml_writer.py` (add constants + lookup)

- [ ] **Step 1: Append the 3 failing tests**

Append to `tests/sync/test_groups_export_em_template.py` (after the existing 5 tests):

```python
# ---------------------------------------------------------------------------
# AI08-F2 — Per-dimension visual style
# ---------------------------------------------------------------------------

@pytest.fixture
def expected_palette():
    """The pinned palette from spec §3.1 (D1-A pastel-soft + D2-C 50% alpha)."""
    return {
        "area":      ("#FFE0E680", "#C84A5F"),
        "struttura": ("#FFE6CC80", "#C66B33"),
        "attivita":  ("#FFF5CC80", "#A89A33"),
        "settore":   ("#E6FFCC80", "#6BC633"),
        "ambient":   ("#CCFFE680", "#33A86B"),
        "saggio":    ("#CCF5FF80", "#3389A8"),
        "quad_par":  ("#E0CCFF80", "#6633C6"),
        "adhoc":     ("#F5F5F580", "#666666"),
    }


def _seed_all_dimensions(db, sito):
    """Set us_table.<col>=<value> for one row each of the 7 SQL dimensions."""
    conn = sqlite3.connect(db)
    rows = list(conn.execute(
        "SELECT id_us FROM us_table WHERE sito=? LIMIT 7", (sito,)))
    pairs = [
        ("area",      "A1"),
        ("struttura", "basilica"),
        ("attivita",  "1"),
        ("settore",   "N"),
        ("ambient",   "stanza-1"),
        ("saggio",    "S1"),
        ("quad_par",  "Q1"),
    ]
    for (id_us,), (col, val) in zip(rows, pairs):
        conn.execute(
            f"UPDATE us_table SET {col}=? WHERE id_us=?",
            (val, id_us))
    conn.commit()
    conn.close()


def test_per_dimension_fill_color(mini_volterra, tmp_path, expected_palette):
    """AC-1 + AC-4: each rendered group folder's <y:Fill color> matches the
    palette entry for its group_kind, and the alpha suffix is always '80'
    (50% transparency, D2-C)."""
    sito = _read_sito(mini_volterra)
    _seed_all_dimensions(mini_volterra, sito)

    out = tmp_path / "out.graphml"
    _export_with_groups(
        mini_volterra, sito, out,
        ["area", "struttura", "attivita", "settore",
         "ambient", "saggio", "quad_par"])

    tree = ET.parse(str(out))
    folders = [n for n in tree.iter(f"{NS}node")
               if n.get("yfiles.foldertype") == "group"
               and n.get("id", "").startswith("grp_")]
    assert len(folders) >= 7, (
        f"expected >=7 group folders (one per seeded dim), got "
        f"{len(folders)}")

    # For each folder: read <y:NodeLabel> text (group name) and verify
    # its <y:Fill color> matches one of the expected palette entries.
    fills_by_label = {}
    for folder in folders:
        nl = folder.find(f".//{Y}GroupNode/{Y}NodeLabel")
        fill = folder.find(f".//{Y}GroupNode/{Y}Fill")
        assert nl is not None and fill is not None
        fills_by_label[(nl.text or "").strip()] = fill.get("color")

    # Each label maps to a known seeded value; resolve back to dim:
    label_to_dim = {
        "A1":       "area",
        "basilica": "struttura",
        "1":        "attivita",
        "N":        "settore",
        "stanza-1": "ambient",
        "S1":       "saggio",
        "Q1":       "quad_par",
    }
    for label, color in fills_by_label.items():
        dim = label_to_dim.get(label)
        if dim is None:
            continue  # unrelated folder (shouldn't happen)
        expected_fill, _ = expected_palette[dim]
        assert color == expected_fill, (
            f"folder '{label}' (group_kind={dim}): "
            f"expected fill={expected_fill}, got {color}")
        # AC-4: alpha suffix == '80'
        assert color.endswith("80"), (
            f"fill {color} is missing the 50% alpha suffix '80'")


def test_per_dimension_border_color(mini_volterra, tmp_path, expected_palette):
    """AC-2: each rendered group folder's <y:BorderStyle color> matches
    the palette entry for its group_kind."""
    sito = _read_sito(mini_volterra)
    _seed_all_dimensions(mini_volterra, sito)

    out = tmp_path / "out.graphml"
    _export_with_groups(
        mini_volterra, sito, out,
        ["area", "struttura", "attivita", "settore",
         "ambient", "saggio", "quad_par"])

    tree = ET.parse(str(out))
    folders = [n for n in tree.iter(f"{NS}node")
               if n.get("yfiles.foldertype") == "group"
               and n.get("id", "").startswith("grp_")]

    label_to_dim = {
        "A1": "area", "basilica": "struttura", "1": "attivita",
        "N": "settore", "stanza-1": "ambient", "S1": "saggio",
        "Q1": "quad_par",
    }
    for folder in folders:
        nl = folder.find(f".//{Y}GroupNode/{Y}NodeLabel")
        bs = folder.find(f".//{Y}GroupNode/{Y}BorderStyle")
        assert nl is not None and bs is not None
        label = (nl.text or "").strip()
        dim = label_to_dim.get(label)
        if dim is None:
            continue
        _, expected_border = expected_palette[dim]
        assert bs.get("color") == expected_border, (
            f"folder '{label}' (group_kind={dim}): "
            f"expected border={expected_border}, got {bs.get('color')}")
        assert bs.get("type") == "dashed"


def test_unknown_group_kind_falls_back_to_default(mini_volterra, tmp_path):
    """AC-3: a group with an unrecognized group_kind gets the default
    (#F5F5F580 fill + #000000 border). Synthesized via direct call to
    _inject_group_folders with a fake snapshot — bypasses the projector."""
    from modules.s3dgraphy.sync.graphml_writer import (
        _inject_group_folders, _GROUP_KIND_PALETTE,
        _GROUP_DEFAULT_FILL, _GROUP_DEFAULT_BORDER,
    )
    # Sanity: the default values match the spec §3.1
    assert _GROUP_DEFAULT_FILL == "#F5F5F580"
    assert _GROUP_DEFAULT_BORDER == "#000000"
    # And "totally_bogus" is not in the palette
    assert "totally_bogus" not in _GROUP_KIND_PALETTE

    # First do a real export so we have a valid GraphML to inject into
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)
    out = tmp_path / "out.graphml"
    _export_with_groups(mini_volterra, sito, out, ["struttura"])

    # Read the EMIDs of 2 strat US already in the output (member candidates)
    tree = ET.parse(str(out))
    NS_local = "{http://graphml.graphdrawing.org/xmlns}"
    Y_local = "{http://www.yworks.com/xml/graphml}"
    emid_kid = None
    for k in tree.getroot().findall(f"{NS_local}key"):
        if k.get("attr.name") == "EMID":
            emid_kid = k.get("id")
            break
    assert emid_kid is not None
    emids = []
    for n in tree.iter(f"{NS_local}node"):
        for d in n.findall(f"{NS_local}data"):
            if d.get("key") == emid_kid and d.text:
                emids.append(d.text.strip())
    candidate_emids = [e for e in emids
                        if not (e or "").startswith("grp_")][:2]
    assert len(candidate_emids) >= 2

    # Build a fake snapshot with an unknown group_kind
    class _FakeNode:
        def __init__(self):
            self.node_id = "test-bogus-uuid"
            self.name = "BogusGroup"
            self.attributes = {
                "group_kind": "totally_bogus",
                "sito":       sito,
                "name":       "BogusGroup",
            }
    fake_snapshot = [_FakeNode()]
    fake_members = {"test-bogus-uuid": candidate_emids}

    # Inject into a fresh copy
    out2 = tmp_path / "out_bogus.graphml"
    import shutil
    shutil.copy2(out, out2)
    # Strip pre-existing grp_* folder so the inject finds clean strat
    tree2 = ET.parse(str(out2))
    parent_of = {c: p for p in tree2.iter() for c in p}
    for f in list(tree2.iter(f"{NS_local}node")):
        if f.get("id", "").startswith("grp_"):
            par = parent_of.get(f)
            if par is not None:
                par.remove(f)
    tree2.write(str(out2), encoding="UTF-8",
                xml_declaration=True, pretty_print=True)

    _inject_group_folders(fake_snapshot, fake_members, out2)

    # Read back the output and verify default colors applied
    tree3 = ET.parse(str(out2))
    bogus_folders = [n for n in tree3.iter(f"{NS_local}node")
                     if n.get("yfiles.foldertype") == "group"
                     and n.get("id", "") == "grp_test-bogus-uuid"]
    assert len(bogus_folders) == 1
    folder = bogus_folders[0]
    fill = folder.find(f".//{Y_local}GroupNode/{Y_local}Fill")
    bs = folder.find(f".//{Y_local}GroupNode/{Y_local}BorderStyle")
    assert fill is not None and bs is not None
    assert fill.get("color") == _GROUP_DEFAULT_FILL
    assert bs.get("color") == _GROUP_DEFAULT_BORDER
```

(Note: this code uses helpers `mini_volterra`, `_read_sito`, `_seed`, `_export_with_groups`, `NS`, `Y` already defined at the top of the existing `test_groups_export_em_template.py` from AI06 D.1. No new fixtures or helpers required.)

- [ ] **Step 2: Run the new tests, expect failure**

```bash
PYTHONPATH="$PWD" python -m pytest \
    tests/sync/test_groups_export_em_template.py::test_per_dimension_fill_color \
    tests/sync/test_groups_export_em_template.py::test_per_dimension_border_color \
    tests/sync/test_groups_export_em_template.py::test_unknown_group_kind_falls_back_to_default \
    -v 2>&1 | tail -10
```

Expected:
- `test_per_dimension_fill_color` and `test_per_dimension_border_color` FAIL with assertion errors (the actual fill is `#F5F5F5` not `#FFE6CC80`, and border is `#000000` not `#C66B33`).
- `test_unknown_group_kind_falls_back_to_default` FAIL with `ImportError` on `_GROUP_KIND_PALETTE` (the constant doesn't exist yet).

This confirms the tests are wired up correctly — the implementation is the next step.

- [ ] **Step 3: Locate the existing fill/border lines in `graphml_writer.py`**

```bash
grep -n 'fill.set("color", "#F5F5F5")\|bs.set("color", "#000000")' \
    modules/s3dgraphy/sync/graphml_writer.py
```

Expected: 2 hits, around lines 1431 and 1435 (inside `_inject_group_folders`).

- [ ] **Step 4: Add the `_GROUP_KIND_PALETTE` constant + defaults**

In `modules/s3dgraphy/sync/graphml_writer.py`, find the line `def _inject_group_folders(` (around line 1264). Insert the constant block IMMEDIATELY ABOVE that line:

```python
# AI08-F2: per-dimension palette. Pastel-soft (D1-A) with 50% alpha
# fill (D2-C) so the epoch swimlane rows underneath stay visible,
# plus a darker solid border. Keys are group_kind values produced
# by group_projector.build_groups_from_sql + the "adhoc" kind from
# user-authored GroupStore entries.
_GROUP_KIND_PALETTE: dict = {
    # group_kind     : (fill_rgba_50pct,    border_solid)
    "area":            ("#FFE0E680",         "#C84A5F"),
    "struttura":       ("#FFE6CC80",         "#C66B33"),
    "attivita":        ("#FFF5CC80",         "#A89A33"),
    "settore":         ("#E6FFCC80",         "#6BC633"),
    "ambient":         ("#CCFFE680",         "#33A86B"),
    "saggio":          ("#CCF5FF80",         "#3389A8"),
    "quad_par":        ("#E0CCFF80",         "#6633C6"),
    "adhoc":           ("#F5F5F580",         "#666666"),
}
_GROUP_DEFAULT_FILL = "#F5F5F580"
_GROUP_DEFAULT_BORDER = "#000000"


def _inject_group_folders(
    ...
```

(The exact `def _inject_group_folders(` signature and body is unchanged — the constants go in the empty space above the function.)

- [ ] **Step 5: Replace the 2 hardcoded color sets**

Find this block in `_inject_group_folders` (around lines 1430-1437):

```python
        fill = etree.SubElement(gn, f"{{{NS_Y}}}Fill")
        fill.set("color", "#F5F5F5")
        fill.set("transparent", "false")

        bs = etree.SubElement(gn, f"{{{NS_Y}}}BorderStyle")
        bs.set("color", "#000000")
        bs.set("type", "dashed")
        bs.set("width", "1.0")
```

Replace it with this (uses the `attrs` variable which is already in scope at line 1370):

```python
        # AI08-F2: per-dimension palette lookup (D2-C). Default falls
        # back to AI06 grey + black for unknown group_kind values.
        group_kind = attrs.get("group_kind", "")
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

- [ ] **Step 6: Re-run the 3 new tests, expect green**

```bash
PYTHONPATH="$PWD" python -m pytest \
    tests/sync/test_groups_export_em_template.py::test_per_dimension_fill_color \
    tests/sync/test_groups_export_em_template.py::test_per_dimension_border_color \
    tests/sync/test_groups_export_em_template.py::test_unknown_group_kind_falls_back_to_default \
    -v 2>&1 | tail -6
```

Expected: `3 passed`.

- [ ] **Step 7: Run all AI06 group tests to confirm no regression**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_groups_export_em_template.py -v 2>&1 | tail -10
```

Expected: `8 passed` (5 AI06 + 3 new).

- [ ] **Step 8: AC-2 baseline (CRITICAL — must stay green)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -2
```

Expected: `1 passed`.

- [ ] **Step 9: All 11 critical regression guards**

```bash
PYTHONPATH="$PWD" python -m pytest \
    tests/sync/test_ai03_export_byte_identical.py \
    tests/sync/test_round_trip.py \
    tests/sync/test_idempotent_ingest.py \
    tests/sync/test_cli_helper.py \
    tests/sync/test_paradata_store.py \
    tests/sync/test_round_trip_with_paradata.py \
    tests/sync/test_paradata_idempotent.py \
    tests/sync/test_strategy_a_no_regression.py \
    tests/sync/test_groups_export_em_template.py \
    tests/sync/test_round_trip_with_groups.py \
    tests/sync/test_groups_idempotent.py \
    -q 2>&1 | tail -3
```

Expected: all green.

- [ ] **Step 10: Full suite — 176 → 179**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `179 passed, 3 skipped`.

- [ ] **Step 11: Commit**

```bash
git add modules/s3dgraphy/sync/graphml_writer.py \
        tests/sync/test_groups_export_em_template.py
git commit -m "$(cat <<'EOF'
feat(graphml_writer): per-dimension palette for group folders (AI08-F2)

Introduces a hardcoded module-level palette
_GROUP_KIND_PALETTE in graphml_writer.py mapping each of the 8
grouping dimensions to a (fill_rgba_50pct, border_solid) tuple:

  area      → #FFE0E680 / #C84A5F
  struttura → #FFE6CC80 / #C66B33
  attivita  → #FFF5CC80 / #A89A33
  settore   → #E6FFCC80 / #6BC633
  ambient   → #CCFFE680 / #33A86B
  saggio    → #CCF5FF80 / #3389A8
  quad_par  → #E0CCFF80 / #6633C6
  adhoc     → #F5F5F580 / #666666

The Stage 4e post-processor _inject_group_folders now reads
group_kind from each ActivityNodeGroup's attributes dict and looks
up the palette to populate <y:Fill color> and <y:BorderStyle color>.
50% alpha (suffix 0x80) on fills lets the epoch swimlane rows show
through the group rectangle.

Unknown / missing group_kind falls back to (#F5F5F580, #000000) —
AI06 grey at 50% alpha + black border (defensive default).

Label background (#EBEBEB), Geometry, Shape, State unchanged
(D2-C: only Fill+Border vary).

Out of scope: group_store._emit_group_node (the s3dgraphy
round-trip channel) keeps its #CCFFFF backgroundColor for the
GraphMLImporter discriminator (D4-A).

3 new L4 tests:
  - test_per_dimension_fill_color (AC-1 + AC-4 alpha suffix)
  - test_per_dimension_border_color (AC-2)
  - test_unknown_group_kind_falls_back_to_default (AC-3)

AC-2 byte-identical baseline GREEN (default groups=None → no
folders → no palette lookup). All 11 critical regression guards
green.

Tests: 179/179 pass + 3 skipped.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task A.2: Stability sweep (no commit)

**Files:** none (verification only)

- [ ] **Step 1: Full suite × 3 for stability**

```bash
for i in 1 2 3; do
    PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -1
done
```

Expected: 3 × `179 passed, 3 skipped`.

- [ ] **Step 2: AC-2 baseline × 5**

```bash
for i in 1 2 3 4 5; do
    PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -q 2>&1 | tail -1
done
```

Expected: 5 × `1 passed`.

- [ ] **Step 3: Co-author trailer scan across the new commit**

```bash
git log phase2-ai06-node-grouping-5.5.0-alpha..HEAD --format=%B | grep -c "Co-Authored-By"
```

Expected: `0`.

If any check fails, STOP and investigate before proceeding to Group B.

---

## Group B — Release packaging

### Task B.1: Dev-log entry

**Files:**
- Modify: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

- [ ] **Step 1: Append the AI08-F2 section at END of file**

Use the Edit tool to add at the bottom of `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`:

```markdown

---

# Phase 2 — AI08-F2 Per-dimension visual style for group folders

**Date:** 2026-05-09
**Tag:** `phase2-ai08f2-per-dim-visual-5.5.1-alpha`
**Spec:** `docs/superpowers/specs/2026-05-09-ai08f2-per-dim-visual-design.md`
**Plan:** `docs/superpowers/plans/2026-05-09-ai08f2-per-dim-visual.md`

## What was built

Sub-feature spec of AI08 (split per Q0 = B in brainstorming session).
Adds distinct visual style per `group_kind` to the Extended Matrix
export — each of the 8 grouping dimensions (area / struttura /
attivita / settore / ambient / saggio / quad_par / adhoc) now
renders with its own pastel-soft fill (50% alpha) and matching
darker solid border.

**`_GROUP_KIND_PALETTE`** — new module-level constant in
`modules/s3dgraphy/sync/graphml_writer.py` mapping each dimension
to a `(fill_rgba_50pct, border_solid)` tuple.

**`_inject_group_folders`** — Stage 4e post-processor reads
`group_kind` from `ActivityNodeGroup.attributes` and looks up the
palette to populate `<y:Fill color>` and `<y:BorderStyle color>`.
Unknown / missing `group_kind` falls back to AI06 default colors.

50% alpha on fills (yEd `#RRGGBBAA` format with `AA=0x80`) means
the epoch swimlane rows underneath stay visible through the group
rectangle. Border colors are solid (no alpha) so the dashed
silhouette of each group remains crisp.

## Out of scope (untouched)

- `group_store._emit_group_node` keeps `<y:NodeLabel backgroundColor="#CCFFFF">`
  as the s3dgraphy round-trip discriminator. F2 only colors the
  user-visible export path (`graphml_writer._inject_group_folders`).
- AI07 (`LocationNodeGroup` migration) still deferred (memory note
  `project_ai07_locationnodegroup_deferral.md`; reactivation
  deadline 2026-05-23).
- AI08-F1 (hierarchical nesting) and AI08-F3 (auto-layout heuristics)
  remain separate spec/release targets.

## Test counts

- Baseline (post-AI06): 176 passed, 3 skipped
- Post-Group A: 179 passed, 3 skipped (+3 new tests)
- Post-Group B: 179 passed, 3 skipped (no new tests)

Final: **179 passed + 3 skipped** (Qt-headless smoke).

## Acceptance criteria

All 9 ACs from spec §7 satisfied. AC-2 byte-identical baseline
stayed green (default `groups=None` → palette never consulted).

## Manual smoke gate (Group B.3)

User-driven validation in QGIS — see plan §B.3.
```

- [ ] **Step 2: Verify**

```bash
tail -40 docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md
```

Expected: AI08-F2 section visible at the end.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md
git commit -m "$(cat <<'EOF'
docs(dev-log): Phase 2 / AI08-F2 per-dimension visual style entry

Records AI08-F2 outcome: hardcoded _GROUP_KIND_PALETTE mapping the
8 grouping dimensions to (fill_rgba_50pct, border_solid) tuples,
applied in _inject_group_folders Stage 4e post-processor.

Test counts at Group boundaries documented (176 → 179 + 3 skipped
unchanged).

Carry-overs documented: F1 hierarchical nesting + F3 auto-layout
remain separate targets; AI07 LocationNodeGroup still deferred.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task B.2: CHANGELOG bilingual entry

**Files:**
- Modify: `dev_logs/CHANGELOG.md`

- [ ] **Step 1: Read top of file**

```bash
head -30 dev_logs/CHANGELOG.md
```

Identify the title and the existing `## [5.5.0-alpha]` section.

- [ ] **Step 2: Prepend the new section**

Insert immediately after the title line:

```markdown
## [5.5.1-alpha] - 2026-05-09

### Italiano

- **Phase 2 / AI08-F2 — Stile visivo per dimensione nei group folder.** Ogni dimensione di raggruppamento (area / struttura / attivita / settore / ambient / saggio / quad_par / adhoc) ora ha un fill pastello distinto al 50% di trasparenza più un bordo solido colorato della stessa famiglia. Il fill 50% lascia intravedere le righe delle epoche dietro il rettangolo del gruppo.
- **Palette hardcoded** in `modules/s3dgraphy/sync/graphml_writer.py` come constante `_GROUP_KIND_PALETTE`. Niente file di config — 8 entry, ognuna `(fill_rgba_50pct, border_solid)`.
- **Default invariato.** Senza checkbox spuntate (`groups=None`) il pulsante verde produce lo stesso GraphML byte-identico al baseline AC-2. La palette si attiva solo quando i gruppi sono materializzati.
- **Background label** (`#EBEBEB`) e geometry restano AI06. Solo `<y:Fill>` e `<y:BorderStyle>` cambiano per dimensione.
- **Round-trip preservato.** L'output AI06 importava i folder via `yfiles.foldertype="group"` + prefix `grp_*` (lxml-based, color-agnostic) — nessun impatto su `sql_apply_groups`.

### English

- **Phase 2 / AI08-F2 — Per-dimension visual style for group folders.** Each grouping dimension (area / struttura / attivita / settore / ambient / saggio / quad_par / adhoc) now has its own pastel fill at 50% transparency plus a matching solid darker border. The 50% alpha lets the epoch row swimlanes show through the group rectangle.
- **Hardcoded palette** in `modules/s3dgraphy/sync/graphml_writer.py` as the `_GROUP_KIND_PALETTE` constant. No config file — 8 entries, each `(fill_rgba_50pct, border_solid)`.
- **Default unchanged.** Without checked checkboxes (`groups=None`) the green Export button produces the same GraphML byte-identical to the AC-2 baseline. The palette only kicks in when groups are materialised.
- **Label background** (`#EBEBEB`) and geometry remain as in AI06. Only `<y:Fill>` and `<y:BorderStyle>` vary per dimension.
- **Round-trip preserved.** The AI06 import path identifies group folders by `yfiles.foldertype="group"` + `grp_*` id prefix (lxml-based, color-agnostic) — no impact on `sql_apply_groups`.

```

(Keep the trailing blank line.)

- [ ] **Step 3: Verify**

```bash
head -45 dev_logs/CHANGELOG.md
```

Confirm new block on top, existing 5.5.0-alpha intact below.

- [ ] **Step 4: Commit**

```bash
git add dev_logs/CHANGELOG.md
git commit -m "$(cat <<'EOF'
docs(changelog): 5.5.1-alpha — AI08-F2 per-dim visual style (IT + EN)

Bilingual entry summarising the AI08-F2 release:
- New _GROUP_KIND_PALETTE in graphml_writer.py (8 entries,
  pastel-soft fill at 50% alpha + matching solid darker border).
- _inject_group_folders applies the palette per group_kind.
- Default groups=None unchanged → AC-2 byte-identical preserved.
- Label background and geometry remain as AI06; only Fill +
  BorderStyle vary per dimension.
- Round-trip path unaffected (color-agnostic identification by
  yfiles.foldertype + grp_* prefix).
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task B.3: Manual smoke gate + tag + push

**Files:** none (USER-driven manual validation; then git operations).

This step is **user-driven**. The dispatching agent waits for the user's "ok smoked, proceed" before triggering the tag.

- [ ] **Step 1: Final controller checks**

```bash
git status --short | grep -vE '^\?\?'   # must be empty
git log --oneline phase2-ai06-node-grouping-5.5.0-alpha..HEAD | wc -l
git log phase2-ai06-node-grouping-5.5.0-alpha..HEAD --format=%B | grep -c "Co-Authored-By"
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -1
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -q 2>&1 | tail -1
grep "^version=" metadata.txt
```

Expected:
- empty status
- ~5-6 commits since AI06 tag
- 0 trailers
- `179 passed, 3 skipped`
- `1 passed` (AC-2)
- `version=5.5.1-alpha`

- [ ] **Step 2: USER manual smoke gate**

User: restart QGIS, open a project with SQLite DB containing populated grouping columns. Click the green "Esporta Extended Matrix" button. In the dialog:
- Verify "Group US by" panel auto-checks the populated dimensions (AI06 unchanged).
- Spunta multiple dimensioni (es. struttura + attivita + adhoc).
- Click Export.

Open the exported GraphML in **yEd**. Verify:
1. **Each group folder has a distinct pastel fill** (orange-ish for struttura, yellow-ish for attivita, grey for adhoc, etc.).
2. **The fill is 50% transparent** — the epoch row swimlane underneath the folder is visible (the band colors of the rows show through).
3. **Each border color matches the family of its fill** (orange border on the orange-fill folder, yellow on yellow, etc.) — solid, dashed style.
4. **Label background** is grey (`#EBEBEB`) — same as AI06.
5. **No layout shift** — folders are positioned exactly as in AI06.

Optional CLI check:
```bash
python scripts/s3dgraphy_sync.py export \
    --db <my-db> --sito <my-site> --mapping pyarchinit_us_mapping \
    --output /tmp/test_palette.graphml \
    --group-by struttura,attivita,adhoc
grep -c "color=\"#FFE6CC80\"" /tmp/test_palette.graphml   # expect ≥1 (struttura fill)
grep -c "color=\"#FFF5CC80\"" /tmp/test_palette.graphml   # expect ≥1 (attivita fill)
```

User writes back **"ok smoked, proceed"** when satisfied.

- [ ] **Step 3: Create the release tag**

```bash
git tag -a phase2-ai08f2-per-dim-visual-5.5.1-alpha \
    -m "Phase 2 / AI08-F2: per-dimension visual style (pastel-soft fill at 50% alpha + matching solid darker border for each of the 8 grouping dimensions)"
git tag -l | grep -E "phase2|pre-ai08"
```

Expected (5 lines for phase2 + N for pre-aiNN):
```
phase2-ai03-graphml-delegation-5.2.0-alpha
phase2-ai04-bridge-bidirectional-5.3.0-alpha
phase2-ai05-paradata-store-5.4.0-alpha
phase2-ai06-node-grouping-5.5.0-alpha
phase2-ai08f2-per-dim-visual-5.5.1-alpha
pre-ai08f2-palette
...
```

- [ ] **Step 4: Push branch + tag**

```bash
git push origin Stratigraph_00001
git push origin phase2-ai08f2-per-dim-visual-5.5.1-alpha
```

Expected:
- branch push: ~5-6 commits to `origin/Stratigraph_00001`.
- tag push: `[new tag] phase2-ai08f2-per-dim-visual-5.5.1-alpha`.

- [ ] **Step 5: Verify on remote**

```bash
git ls-remote --tags origin 2>&1 | grep "phase2-ai08f2" | head -2
```

Expected: 2 lines (the tag commit + its `^{}` deref).

- [ ] **Step 6: Final state check**

```bash
git rev-list --left-right --count HEAD...@{u}   # expect "0\t0"
```

---

## Self-review checklist (run inline before delivering the plan)

Reviewed against the spec on 2026-05-09:

**1. Spec coverage**

- §1 Overview → addressed by file structure + Group A narrative.
- §2 D1–D4 → each decision pinned by a task:
  - D1 palette → A.1 Step 4 (the constant block has all 8 entries verbatim from spec §3.1)
  - D2-C extent → A.1 Step 5 (only `<y:Fill>` color and `<y:BorderStyle>` color change; label bg untouched)
  - D3 location → A.1 Step 4 (constant lives in `graphml_writer.py` next to `_inject_group_folders`)
  - D4-A scope → "Explicitly NOT touched" (group_store left alone)
- §3 Components: §3.1 `_GROUP_KIND_PALETTE` constant → A.1 Step 4; §3.2 `_inject_group_folders` modification → A.1 Step 5; §3.3 NOT touched → file structure section.
- §4 Data flow → covered by the Group A narrative (snapshot → inject → palette lookup).
- §5 Error handling → AC-3 test (`test_unknown_group_kind_falls_back_to_default`) pins the defensive default.
- §6 Testing: 3 new L4 tests + 11 critical regression guards. Test count 176 → 179 documented.
- §7 Acceptance criteria: AC-1/2/3/4 → A.1 tests; AC-5 → existing AI06 test (label bg unchanged); AC-6 → A.1 Step 8 + A.2; AC-7 → A.1 Step 9 + A.2; AC-8 → A.1 Step 10 + A.2; AC-9 → B.3 manual smoke.
- §8 Release plan → Group 0 (3 tasks) / Group A (2 tasks) / Group B (3 tasks) — matches.
- §9 Out of scope → "Explicitly NOT touched" + the dev-log entry's "Out of scope" subsection.
- §10 Risks → mitigations baked in (AC-2 stays green via opt-in default; manual smoke gate covers yEd alpha rendering).

**2. Placeholder scan**

No `TBD`, `TODO`, `FIXME`, `implement later`, `Add appropriate error handling`, `Similar to Task N` placeholders. Every step has explicit code or commands. The "Note" in A.1 Step 1 about reused fixtures references already-existing helpers (`mini_volterra`, `_read_sito`, `_seed`, `_export_with_groups`, `NS`, `Y`) defined in the same test file by AI06 D.1 — these names are real, not placeholders.

**3. Type consistency**

- `_GROUP_KIND_PALETTE: dict` with values `(fill_rgba_50pct, border_solid)` — consistent across A.1 Step 4 (definition), A.1 Step 5 (usage), and the test assertions (A.1 Step 1 `expected_palette` fixture).
- `_GROUP_DEFAULT_FILL = "#F5F5F580"` and `_GROUP_DEFAULT_BORDER = "#000000"` — consistent across A.1 Step 4 (definition) and the unknown-kind test (A.1 Step 1 imports them and asserts the values).
- `attrs.get("group_kind", "")` — uses the same `attrs` variable already in scope at line 1370 (verified via Read tool); no new variable introduced.
- `expected_palette` fixture in A.1 Step 1 has 8 entries; A.1 Step 4 constant has 8 entries; entries are identical hex values.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-09-ai08f2-per-dim-visual.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — Dispatch a fresh subagent per Group with two-stage review (spec compliance → code quality) between Groups. Group A is the only code-touching Group; Group 0 is git/admin and Group B is docs+tag.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints. Given the small scope (~6 commits), inline is reasonable and saves the subagent dispatch overhead.

**Which approach?**
