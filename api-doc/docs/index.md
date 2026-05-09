---
hide:
  - navigation
  - toc
---

<div class="hero" markdown>

# PyArchInit API Reference

Auto-generated reference for the [**PyArchInit**](https://www.pyarchinit.org/) QGIS plugin —
the open-source toolkit for archaeological data management, harris-matrix
analysis, and Extended Matrix integration.

<div class="badges" markdown>
![QGIS](https://img.shields.io/badge/QGIS-≥3.22-589632?logo=qgis&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-GPL%20v2-blue)
![Docs](https://img.shields.io/badge/built%20with-mkdocs--material-526CFE?logo=materialformkdocs&logoColor=white)
</div>

</div>

<div class="stats-banner" markdown>

<div class="stat" markdown>
<span class="num">558</span>
<span class="label">Python files</span>
</div>

<div class="stat" markdown>
<span class="num">634</span>
<span class="label">Classes</span>
</div>

<div class="stat" markdown>
<span class="num">5,228</span>
<span class="label">Methods</span>
</div>

<div class="stat" markdown>
<span class="num">818</span>
<span class="label">Functions</span>
</div>

</div>

## What is PyArchInit?

PyArchInit is a comprehensive QGIS plugin (**≥ 3.22**) for archaeological
fieldwork: stratigraphic recording, finds inventory, burials, periodization,
and full Extended Matrix integration via the bidirectional **s3dgraphy
bridge**. It supports both **PostgreSQL/PostGIS** and **SQLite/Spatialite**
backends, with a multi-language UI in 10 languages.

This site documents the **internal Python API**: every class, function, and
module across the plugin codebase. It is regenerated from source-tree
docstrings each time the codebase ships a new milestone.

## Quick navigation

<div class="grid cards" markdown>

-   :material-source-branch:{ .lg .middle } **s3dgraphy bridge**

    ---

    Bidirectional sync with the Extended Matrix data model — `GraphProjector`,
    `GraphIngestor`, `ParadataStore`, `GroupStore`, vocabulary, edge styling
    and per-dimension visual rules.

    [:octicons-arrow-right-24: Browse the bridge](s3dgraphy.md)

-   :material-database:{ .lg .middle } **Database layer**

    ---

    SQLAlchemy entities and table structures for sites, stratigraphic units,
    finds, burials, samples, periodization. Multi-backend
    (PostgreSQL/Spatialite).

    [:octicons-arrow-right-24: Database modules](database.md)

-   :material-form-select:{ .lg .middle } **Tabs (form controllers)**

    ---

    The 48 form controllers under `tabs/` that drive every CRUD dialog —
    Site, US/USM, Inventory, Tombs, Pottery, Pdf export, Movecost, etc.

    [:octicons-arrow-right-24: Tab controllers](tabs.md)

-   :material-cog:{ .lg .middle } **GUI components**

    ---

    Backup/restore dialogs, image viewers, settings screens, the
    StratiGraph sync panel, and shared widgets.

    [:octicons-arrow-right-24: GUI modules](gui.md)

-   :material-cloud-sync:{ .lg .middle } **StratiGraph sync engine**

    ---

    Bundle creation, manifest generation, validation, sync queue and
    state machine for offline-first field workflows.

    [:octicons-arrow-right-24: StratiGraph](stratigraph.md)

-   :material-database-arrow-up:{ .lg .middle } **Storage backends**

    ---

    Pluggable media backends: local, S3, Cloudinary, Dropbox, Google
    Drive, WebDAV, HTTP, UNIBO file manager.

    [:octicons-arrow-right-24: Storage](storage.md)

-   :material-file-document-outline:{ .lg .middle } **Reports & utility**

    ---

    PDF report generation (ReportLab), drawing utilities, matrix exports,
    image processing helpers and i18n scaffolding.

    [:octicons-arrow-right-24: Utility](utility.md)

-   :material-book-open-variant:{ .lg .middle } **Full API index**

    ---

    Searchable A→Z list of every public class and top-level function in
    the codebase.

    [:octicons-arrow-right-24: API index](API_INDEX.md)

</div>

## Quickstart

```python
# Programmatic projection: pyarchinit SQLite → s3dgraphy.Graph
from modules.s3dgraphy.sync.graph_projector import GraphProjector

projector = GraphProjector()
graph = projector.populate_graph(
    db_path="/path/to/pyarchinit.sqlite",
    sito="Test_Site",
    include_paradata=True,
)

print(f"Projected {len(graph.nodes)} nodes, {len(graph.edges)} edges")
```

```python
# Export Extended Matrix as GraphML for yEd
from modules.s3dgraphy.sync.graphml_writer import export_graphml

result = export_graphml(
    db_path="/path/to/pyarchinit.sqlite",
    sito="Test_Site",
    output_path="/tmp/extended_matrix.graphml",
    group_dimension="struttura",     # or area / attivita / settore / ...
)

print(f"Exported {result.node_count} nodes, "
      f"{result.is_after_edges} 'is_after' edges, "
      f"{len(result.warnings)} warnings")
```

## Recent additions

The latest milestones are documented in the [**changelog**](CHANGELOG.md).
Highlights include the full Phase 2 s3dgraphy bridge stack:

- **AI03 — GraphML delegation** (5.2.0-alpha)
- **AI04 — bidirectional bridge** (5.3.0-alpha)
- **AI05 — paradata store** (5.4.0-alpha)
- **AI06 — node grouping** (5.5.0-alpha)
- **AI08-F2 — per-dimension visual style** (5.5.1-alpha)
- Hot-fix release **5.5.2-alpha** for multi-dim export + per-US fields

## How this site is built

This site is generated from the Python source-tree by an AST walker that
extracts docstrings and signatures. The Markdown is then rendered with
[**mkdocs-material**](https://squidfunk.github.io/mkdocs-material/), with a
custom palette inspired by the warm tones of archaeological strata.

| Component | Tool |
|---|---|
| Source extraction | Python `ast` module |
| Markdown rendering | [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) |
| Search | Lunr (en + it stemmers) |
| Hosting | [Read the Docs](https://readthedocs.org/) |

## Contributing

Improvements to docstrings flow into this reference automatically on the
next regeneration. To suggest changes to the rendering or theme,
[edit the source on GitHub](https://github.com/pyarchinit/pyarchinit-api-docs)
and open a pull request.
