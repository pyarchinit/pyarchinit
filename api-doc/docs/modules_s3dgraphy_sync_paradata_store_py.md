# modules/s3dgraphy/sync/paradata_store.py

## Overview

This file contains 25 documented elements.

## Functions

### _sito_slug(sito)

Filename-safe lowercase slug for a sito identifier.

**Parameters:**
- `sito`

## Classes

### ParadataStoreError

Base for ParadataStore errors.

**Inherits from**: GraphSyncError

### ParadataReadError

File parse / schema error during read().

**Inherits from**: ParadataStoreError

### ParadataWriteError

File write / atomic-rename failure during write().

**Inherits from**: ParadataStoreError

### ParadataValidationError

Caller passed bogus data to add_author/license/embargo/etc.

**Inherits from**: ParadataStoreError

### ParadataNotFoundError

Required file missing where caller expected it.

**Inherits from**: ParadataStoreError

### ParadataStore

Site-scoped CRUD for paradata.graphml.

Args:
    db_path: filesystem path to the pyarchinit SQLite DB; the
        paradata file lives in the same directory.
    sito: site identifier (a value from `us_table.sito`).

Raises on instantiation: nothing (lazy file checks; read/write
perform actual I/O).

#### Methods

##### __init__(self, db_path, sito)

*No description available.*
##### file_path(self)

Resolved paradata file path for this (db, sito) pair.

##### exists(self)

Whether the paradata file is present on disk.

##### sito(self)

*No description available.*
##### read(self)

Return a Graph populated with only the paradata-family
nodes from the file. Returns empty Graph when file absent.

##### _hydrate_paradata_attrs(self, graph)

Re-parse the paradata file and merge the JSON-blob
``pyarchinit.paradata_attrs`` data values back onto each
node's ``.attributes`` dict. This is how high-level helpers
(orcid, role, spdx_id, url, until_date, reason) survive a
round-trip — s3dgraphy's importer strips unknown <data>
keys, so we serialise them in our own JSON blob.

##### write(self, graph)

Atomic write: serialise to .tmp, embed AI04 data keys,
os.replace() to final path. Original file untouched on
failure.

Uses a custom minimal-GraphML serializer (rather than the
full ``GraphMLExporter``) because the latter only emits
paradata image nodes when they sit inside a
``ParadataNodeGroup`` attached to a stratigraphic unit; the
site-level paradata file holds isolated AuthorNode /
LicenseNode / EmbargoNode nodes with no stratigraphic
anchors, so the heavyweight exporter would silently drop
them. The minimal output we emit here uses the
``_s3d_node_type:`` round-trip marker (Signal 1 in the
importer's ``_detect_paradata_image_type``), so
``GraphMLImporter`` reconstructs the right subclass on
read().

##### _write_minimal_graphml(self, graph, out_path)

Emit a minimal GraphML file containing only the paradata
nodes from *graph*. Each node carries the round-trip
``_s3d_node_type:<NodeType>`` marker in its description so
``GraphMLImporter`` rebuilds the right subclass.

##### _emit_paradata_node(graph_el, node, type_name, ns_graphml, ns_y)

Append a single paradata <node> to *graph_el*.

##### add_node(self, node)

Append *node* to the paradata graph + write.

##### remove_node(self, node_uuid)

Idempotent removal: no error if node_uuid not found.

##### find(self, node_type, **kwargs)

Return matching nodes from the file. Empty list if none.

##### add_author(self, name, orcid, role)

Create + persist an AuthorNode. Returns the new node_uuid.

##### list_authors(self)

Return [{node_uuid, name, orcid, role}, ...].

##### add_license(self, spdx_id, url)

Create + persist a LicenseNode.

##### list_licenses(self)

*No description available.*
##### add_embargo(self, until_date, reason)

Create + persist an EmbargoNode.

##### list_embargos(self)

*No description available.*
