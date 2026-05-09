# PyArchInit — API Reference

Auto-generated API reference site for the [PyArchInit](https://www.pyarchinit.org/)
QGIS plugin. The site lives in this `api-doc/` subtree of the main plugin
repository — Read the Docs builds it from the `.readthedocs.yaml` at the
repo root.

## Live site

**https://pyarchinit.readthedocs.io/** (once published on RTD)

## Local preview

From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r api-doc/requirements.txt

mkdocs serve -f api-doc/mkdocs.yml  # http://127.0.0.1:8000/
```

## Build a static site

```bash
mkdocs build -f api-doc/mkdocs.yml
# Output in api-doc/site/  (gitignored)
```

## How the docs are regenerated

The Markdown sources under `docs/` are produced from the plugin source-tree
by AST walkers. On a new milestone:

1. Run the regenerator over `modules/`, `tabs/`, `gui/` (see
   `docs/CHANGELOG.md` for the script invocations).
2. Update `API_INDEX.md` and the per-area pages (`gui.md`, `tabs.md`,
   `database.md`, `s3dgraphy.md`, `stratigraph.md`, `storage.md`,
   `utility.md`, `misc.md`).
3. Bump the stats banner numbers in `docs/index.md`.
4. Commit + push — Read the Docs auto-builds the live site on push.

## Theme

[mkdocs-material](https://squidfunk.github.io/mkdocs-material/) with a
custom palette in `docs/assets/extra.css`. Light + dark modes auto-toggle
on system preference and can be overridden via the header switch.

## License

GPL v2 (same as the parent plugin).
