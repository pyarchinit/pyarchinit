# `modules/s3dgraphy/sync/` — pyArchInit ↔ s3dgraphy bridge

This folder is the **PyArchInit-side** of the bridge. Most of it is
slated to move into the `s3dgraphy.sync` package proper (upstream issue
[#10](https://github.com/zalmoxes-laran/s3Dgraphy/issues/10), draft PR
[#11](https://github.com/zalmoxes-laran/s3Dgraphy/pull/11)). After the
move, this folder becomes a thin shim that re-exports
`from s3dgraphy.sync import *` and registers the Qt-aware callbacks the
upstream library deliberately doesn't carry.

## Workspace root: `PYARCHINIT_WORKSPACE_DIR`

`_workspace.py::_resolve_workspace_root()` reads **one channel only**:

```python
os.environ.get("PYARCHINIT_WORKSPACE_DIR")  # falls back to ~/pyarchinit/pyarchinit_DB_folder
```

The QSettings tier was removed in commit `06565e1e` so the s3dgraphy
sync code stays free of any Qt dependency (s3dgraphy policy: zero
`qgis.*` / `PyQt*` imports, see issue #10 review).

**That single env var is the entire host-app contract.** PyArchInit
mirrors `QSettings("pyarchinit/paradata_workspace")` → env var at two
points — if you change the workspace handling, edit *both*:

| Mirror point | File | Purpose |
|---|---|---|
| 1. boot | `pyarchinitPlugin.py::initGui` | seed env var from QSettings at plugin start, so the very first sync call sees the configured path |
| 2. config save | `gui/pyarchinitConfigDialog.py` (`_on_workspace_edit_finished` / `_on_workspace_browse` / `_on_workspace_reset`, each call `_propagate_workspace_to_env()`) | re-mirror env var on every user-visible workspace change inside the same session |

Why two sites: (1) covers cold-start state (env var blank, QSettings
populated from a previous session); (2) keeps the env var current while
the dialog is open and the user clicks "Browse" or "Reset" without
restarting QGIS.

For headless / CLI / test callers, set `PYARCHINIT_WORKSPACE_DIR` in
the environment and don't touch QSettings — the sync layer never reads
QSettings directly, only the env var.

## yEd-raw override hook

`graph_ingestor.py` defines `register_yed_override_hook(hook)` /
`clear_yed_override_hook()` for the same reason: when an inbound import
came from a yEd-raw GraphML and PyArchInit needs to ask the user how
to resolve column overrides, the **dialog** is registered by
`pyarchinitPlugin.py::initGui` via `gui/yed_override_hook.py`.
Headless callers leave the hook unset and get the yE-D defaults.

## Related upstream PRs

- [#11 — Move pyArchInit's sync module into `s3dgraphy.sync`
  (Qt-decoupled)](https://github.com/zalmoxes-laran/s3Dgraphy/pull/11)
- [#12 — `PyArchInitImporter`: PostgreSQL backend via
  `connection_url=`](https://github.com/zalmoxes-laran/s3Dgraphy/pull/12)
