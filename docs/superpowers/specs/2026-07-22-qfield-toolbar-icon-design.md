# QField import — toolbar icon (design)

**Date**: 2026-07-22
**Status**: approved
**Scope**: add the existing "Importa da QField (GPKG)" action to the pyArchInit
toolbar with a dedicated icon, in the analysis-tools dropdown (the section
hosting GeoArchaeo, MoveCost, Palimpsest, TOPS, …).

## Background

The QField import feature (pipeline + CLI + dialog) shipped code-complete on
2026-07-21. Its entry point is menu-only: `actionQFieldImport` is created in
`_init_migrations_menu()` (`pyarchinitPlugin.py`, "Importa da QField (GPKG)"
block) with no icon and added via `iface.addPluginToMenu`. The user wants it
reachable from the toolbar like the other analysis tools.

The importer reads a **QField project folder** (recursive `rglob("*.gpkg")`),
not a zip archive. Zip support is explicitly out of scope here (possible
follow-up: auto-extract to a temp dir).

## Design

### 1. Icon

New files in `resources/icons/`:

- `qfield_import.svg` — authored source (kept in repo, like `palimpsest.svg`)
- `qfield_import.png` — 512×512 render used by the code

Style: custom QField-evoking design — QField green (`#79c945`), stylized
field/pin motif with a downward import arrow. No use of the official QField
logo (third-party trademark). Rendered locally SVG→PNG; no new dependencies.

### 2. Wiring — single code-site, not per-locale

Instead of duplicating the QAction in the 4 language blocks of `initGui()`
(the MoveCost/Palimpsest pattern), reuse the fact that
`_init_migrations_menu()` runs exactly once, *after* the active language
block has built the toolbar (same precedent as the StratiGraph Sync toolbar
button, wired in `_init_stratigraph_sync()`).

In the existing "Importa da QField (GPKG)" block of `_init_migrations_menu()`:

1. construct the action with `QIcon(<filepath>/resources/icons/qfield_import.png)`;
2. append it to the analysis dropdown:
   ```python
   if hasattr(self, 'analysisToolButton'):
       self.analysisToolButton.addAction(self.actionQFieldImport)
   ```
   The `hasattr` guard keeps the menu entry working even if a future init
   path skips the toolbar.

Trade-off accepted: the label stays "Importa da QField (GPKG)" in all
languages — identical to today's menu-only behavior, no regression.

### 3. Unload

No change needed. The menu entry is already removed in `unload()`
(`removePluginMenu` for `actionQFieldImport`), and actions inside the
toolbar's `QToolButton`s are torn down with the toolbar itself (GeoArchaeo /
MoveCost have no dedicated `removeToolBarIcon` either).

### 4. Verification

- `python -m py_compile pyarchinitPlugin.py`
- existing qfield test suite still green (no new tests: pure Qt wiring,
  not exercisable headless)
- visual check in QGIS on next plugin reload (user)
