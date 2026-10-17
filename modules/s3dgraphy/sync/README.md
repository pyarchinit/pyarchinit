# `modules/s3dgraphy/sync/` — pyArchInit ↔ s3dgraphy bridge

The sync layer lives in the library: `s3dgraphy.sync` (moved there from
this folder in s3dgraphy 1.6.0 — issue
[#10](https://github.com/zalmoxes-laran/s3Dgraphy/issues/10), PR
[#11](https://github.com/zalmoxes-laran/s3Dgraphy/pull/11), merged
2026-06-03) and `s3dgraphy.rapporti`. Every caller imports those
modules from the library ("one bridge", spec 2026-10-07). This folder
keeps only the pyArchInit layer:

| Module | Role |
|---|---|
| `graph_projector.py` | the library projector plus the host passes (epochs, descriptions, duplicate edges) |
| `graph_ingestor.py` | graph → SQL writer: synthetic guard, cross-site copy, node_uuid identity, PG sequence resync, yEd override hook |
| `continuity_generator.py` | «Genera continuità»: one CON record per unit living across periods |
| `paradata_edge_resolver.py` | `generic_connection` (`>>`) → the specific paradata edge, from the connections datamodel |
| `vocab_provider.py` | Qt-aware vocabulary provider (signal + hot reload) |
| `em_native_import.py` | an em.json written by EMStudio → pyArchInit records |
| `em_media_import.py` | the files an em.json cites → pyArchInit media |
| `em_sources.py` | memory of the imported em.json, restored at export |

## Workspace root: `PYARCHINIT_WORKSPACE_DIR`

The library's `s3dgraphy.sync._workspace._resolve_workspace_root()`
reads **one channel only** (s3dgraphy keeps no `qgis.*` / `PyQt*`
import, so there is no QSettings tier):

```python
os.environ.get("PYARCHINIT_WORKSPACE_DIR")  # else ~/pyarchinit/pyarchinit_DB_folder
```

That fallback is the pyArchInit-4 folder, so pyArchInit must **always**
seed the variable. The root matters only with PostgreSQL (paradata and
group files go to `<root>/<host_port_db>/<site>/`); with SQLite the
files sit next to the `.sqlite`.

**That single env var is the entire host-app contract.** pyArchInit
writes it at three points — if you change the workspace handling, edit
all of them:

| Point | File | What it does |
|---|---|---|
| 1. import | root `__init__.py` | `os.environ.setdefault(...)` to `<PYARCHINIT_HOME>/pyarchinit_DB_folder` (`~/pyarchinit_5`); a value set outside QGIS wins |
| 2. boot | `pyarchinitPlugin.py::initGui` | copies the QSettings override `pyarchinit/paradata_workspace`, when there is one |
| 3. settings | `gui/pyarchinitConfigDialog.py` (`_propagate_workspace_to_env`, on edit / Browse / Reset) | goes through `modules/utility/pyarchinit_home.mirror_workspace`: a blank value returns to the data home instead of dropping the variable |

The standalone CLIs (`scripts/s3dgraphy_sync.py`,
`scripts/import_yed_graphml.py`) seed the variable themselves; tests
and headless callers set it in the environment. Nothing in the sync
layer reads QSettings.

## yEd-raw override hook

`graph_ingestor.py` defines `register_yed_override_hook(hook)` /
`clear_yed_override_hook()` for the same reason: when an inbound import
came from a yEd-raw GraphML and pyArchInit needs to ask the user how
to resolve column overrides, the **dialog** is registered by
`pyarchinitPlugin.py::initGui` via `gui/yed_override_hook.py`.
Headless callers leave the hook unset and get the yE-D defaults.

## Upstream history

- [#11 — Move pyArchInit's sync module into `s3dgraphy.sync`
  (Qt-decoupled)](https://github.com/zalmoxes-laran/s3Dgraphy/pull/11) — merged 2026-06-03
- [#12 — `PyArchInitImporter`: PostgreSQL backend via
  `connection_url=`](https://github.com/zalmoxes-laran/s3Dgraphy/pull/12) — merged 2026-06-03
