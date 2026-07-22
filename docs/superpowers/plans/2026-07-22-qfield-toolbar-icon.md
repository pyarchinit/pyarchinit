# QField Import Toolbar Icon Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Surface the existing "Importa da QField (GPKG)" action in the pyArchInit toolbar's analysis-tools dropdown with a dedicated custom icon.

**Architecture:** Two self-contained changes: (1) new icon assets in `resources/icons/` (authored SVG + 512×512 PNG rendered locally with PySide6 QtSvg); (2) a single-site wiring change in `_init_migrations_menu()` in `pyarchinitPlugin.py`, which runs once after the active language block has built the toolbar — so no per-locale duplication. Spec: `docs/superpowers/specs/2026-07-22-qfield-toolbar-icon-design.md`.

**Tech Stack:** Python 3 / QGIS plugin (qgis.PyQt), PySide6 QtSvg (asset generation only, not a runtime dependency).

## Global Constraints

- Icon style: custom QField-evoking design, QField green `#79c945`; do NOT use the official QField logo (third-party trademark).
- PNG must be 512×512 with transparency (matches `palimpsest.png` sibling).
- Wiring is a single code-site in `_init_migrations_menu()`; do NOT touch the 4 language blocks of `initGui()`.
- Action label stays exactly `"Importa da QField (GPKG)"` (unchanged, all languages).
- No `unload()` changes (menu removal already exists; QToolButton actions die with the toolbar).
- No new runtime dependencies.
- Verification interpreter: `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3`.
- Repo root: `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit` (referred to as `$REPO` below; use `git -C "$REPO"`, never `cd`).
- No AI-attribution lines in commit messages.

---

### Task 1: Icon assets (`qfield_import.svg` + `qfield_import.png`)

**Files:**
- Create: `resources/icons/qfield_import.svg`
- Create: `resources/icons/qfield_import.png`
- Scratch (NOT committed): `<scratchpad>/render_icon.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `resources/icons/qfield_import.png` — the exact path Task 2's `QIcon` loads.

- [ ] **Step 1: Author the SVG source**

Write `resources/icons/qfield_import.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <!-- QField-green rounded tile -->
  <rect x="16" y="16" width="480" height="480" rx="96" fill="#79c945"/>
  <!-- map pin descending into the tray = import from the field -->
  <path d="M256 76c-66 0-120 54-120 120 0 92 120 184 120 184s120-92 120-184c0-66-54-120-120-120zm0 172a52 52 0 1 1 0-104 52 52 0 0 1 0 104z" fill="#ffffff"/>
  <!-- import tray -->
  <path d="M108 348v48a28 28 0 0 0 28 28h240a28 28 0 0 0 28-28v-48" fill="none" stroke="#ffffff" stroke-width="34" stroke-linecap="round"/>
</svg>
```

Minor coordinate tuning is allowed if the render looks unbalanced, but keep the pin+tray motif, the `#79c945` tile, and white foreground.

- [ ] **Step 2: Write the render script (scratchpad, not the repo)**

Write `<scratchpad>/render_icon.py`:

```python
import sys
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtCore import Qt
from PySide6.QtSvg import QSvgRenderer

app = QGuiApplication(sys.argv)
renderer = QSvgRenderer(sys.argv[1])
if not renderer.isValid():
    sys.exit("invalid SVG")
img = QImage(512, 512, QImage.Format.Format_ARGB32)
img.fill(Qt.GlobalColor.transparent)
p = QPainter(img)
renderer.render(p)
p.end()
if not img.save(sys.argv[2]):
    sys.exit("PNG save failed")
print("saved", sys.argv[2])
```

- [ ] **Step 3: Render SVG → PNG**

Run:
```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 "<scratchpad>/render_icon.py" \
  "$REPO/resources/icons/qfield_import.svg" \
  "$REPO/resources/icons/qfield_import.png"
```
Expected output: `saved .../resources/icons/qfield_import.png`

- [ ] **Step 4: Verify PNG dimensions and eyeball the result**

Run: `sips -g pixelWidth -g pixelHeight "$REPO/resources/icons/qfield_import.png"`
Expected: `pixelWidth: 512`, `pixelHeight: 512`.
Then Read the PNG file (it renders as an image) and confirm: green rounded tile, white pin, white tray, no clipping.

- [ ] **Step 5: Commit**

```bash
git -C "$REPO" add resources/icons/qfield_import.svg resources/icons/qfield_import.png
git -C "$REPO" commit -m "feat(qfield): add qfield_import toolbar icon (SVG source + 512px PNG)"
```

---

### Task 2: Toolbar wiring in `_init_migrations_menu()`

**Files:**
- Modify: `pyarchinitPlugin.py` — the `# --- Importa da QField (GPKG) ---` block inside `_init_migrations_menu()` (currently lines ~2816–2824).

**Interfaces:**
- Consumes: `resources/icons/qfield_import.png` from Task 1; module-level `filepath` (pyarchinitPlugin.py:48); module-level `QIcon` import (line 26); existing `self.analysisToolButton` built by the active language block of `initGui()`.
- Produces: `self.actionQFieldImport` with icon, present in both the plugin menu (as today) and the analysis-tools toolbar dropdown.

- [ ] **Step 1: Record the test baseline (pre-change)**

Run: `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m pytest "$REPO/tests/qfield/" -q 2>&1 | tail -3`
Note the pass/fail counts — this is the baseline the post-change run must match.

- [ ] **Step 2: Apply the wiring edit**

In `pyarchinitPlugin.py`, replace this exact block:

```python
            # --- Importa da QField (GPKG) --------------------------------
            self.actionQFieldImport = QAction(
                "Importa da QField (GPKG)",
                self.iface.mainWindow())
            self.actionQFieldImport.triggered.connect(
                self._open_qfield_import)
            self.iface.addPluginToMenu(
                "&pyArchInit - Archaeological GIS Tools",
                self.actionQFieldImport)
```

with:

```python
            # --- Importa da QField (GPKG) --------------------------------
            icon_qfield = '{}{}'.format(
                filepath, os.path.join(os.sep, 'resources', 'icons',
                                       'qfield_import.png'))
            self.actionQFieldImport = QAction(
                QIcon(icon_qfield),
                "Importa da QField (GPKG)",
                self.iface.mainWindow())
            self.actionQFieldImport.triggered.connect(
                self._open_qfield_import)
            self.iface.addPluginToMenu(
                "&pyArchInit - Archaeological GIS Tools",
                self.actionQFieldImport)
            # toolbar: analysis-tools dropdown (GeoArchaeo, MoveCost, ...);
            # guard because the toolbar is built by initGui's language block
            if hasattr(self, 'analysisToolButton'):
                self.analysisToolButton.addAction(self.actionQFieldImport)
```

- [ ] **Step 3: Compile-check**

Run: `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m py_compile "$REPO/pyarchinitPlugin.py" && echo COMPILE_OK`
Expected: `COMPILE_OK`

- [ ] **Step 4: Regression run of the qfield suite**

Run: `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m pytest "$REPO/tests/qfield/" -q 2>&1 | tail -3`
Expected: identical pass/fail counts to the Step 1 baseline (this change is Qt wiring only; the suite must be untouched by it).

- [ ] **Step 5: Commit**

```bash
git -C "$REPO" add pyarchinitPlugin.py
git -C "$REPO" commit -m "feat(qfield): QField import action in analysis toolbar dropdown with icon"
```

---

## Post-plan (not tasks — session-level follow-ups)

- Invoke `tutorial-updater` then `stratigraph-changelog` agents (CLAUDE.md rule: UI-visible change → both).
- Visual verification in QGIS on next plugin reload is the user's step.
