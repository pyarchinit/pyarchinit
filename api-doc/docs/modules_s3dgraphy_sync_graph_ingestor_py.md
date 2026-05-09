# modules/s3dgraphy/sync/graph_ingestor.py

## Overview

This file contains 22 documented elements.

## Functions

### _apply_group_folders_to_sql(cur, graphml_path, sito)

Parse *graphml_path* for ``yfiles.foldertype="group"`` folder
nodes whose id starts with ``grp_`` and apply
``UPDATE us_table SET <kind>=<group_name>`` for every member US.

*cur* is an open SQLite cursor inside the caller's transaction —
we never commit / rollback here. A failure raises and the caller
rolls back.

Returns the number of UPDATEs queued. Folders without a
discoverable SQL ``group_kind`` (i.e. ad-hoc) are skipped entirely
— they never write to SQL regardless of caller flag (AC-14).

Member US identification: prefer ``pyarchinit.node_uuid`` (when
available, byte-identical match to the DB row); fall back to
``(pyarchinit.us, pyarchinit.area, sito)`` (always available
because the AI03 enrichment writes those onto every strat node
regardless of strict_schema).

**Parameters:**
- `cur`
- `graphml_path`
- `sito`

### _values_equal(col, a, b)

Loose equality matching the conventions in graphml_writer
enrichment. JSON-serialised columns (rapporti) get parse-then-compare.

**Parameters:**
- `col`
- `a`
- `b`

### _is_epoch_node_local(node)

*No description available.*
**Parameters:**
- `node`

### _hydrate_pyarchinit_data_keys(graph, graphml_path)

Re-parse the GraphML at *graphml_path* via lxml and merge the
pyarchinit-specific data keys (`pyarchinit.us`, `pyarchinit.area`,
`pyarchinit.unita_tipo`, etc.) into graph node attributes.

This is the IMPORT-side counterpart of
graphml_writer._embed_pyarchinit_data_keys. s3dgraphy's
GraphMLImporter strips unknown attributes; we recover the
pyarchinit-specific ones by reading the same XML directly.

No-op if the GraphML doesn't contain our custom data keys (older
files / files from non-pyarchinit producers).

**Parameters:**
- `graph`
- `graphml_path`

### _find_first_epoch(graph, node_uuid)

Walk has_first_epoch edges from *node_uuid* and return the
`(periodo, fase)` tuple of the linked EpochNode, or `(None, None)`.

s3dgraphy's GraphMLImporter strips most attributes but preserves
edge `edge_type`. The EpochNode keeps `node.name` (e.g. "XV secolo")
and any `attributes['periodo']` / `attributes['fase']` set by the
projector. When attrs are stripped, fall back to parsing from
EpochNode.node_id (which the projector formats as
`epoch_<periodo>_<fase>`).

**Parameters:**
- `graph`
- `node_uuid`

### _rewrite_rapporti_sito(rapporti_str, target_sito)

Parse a pyarchinit rapporti list-of-lists string and rewrite
the sito (4th element of each rapporto) to *target_sito*. Returns
the re-serialised string. Defensive — returns the input unchanged
if parsing fails.

**Parameters:**
- `rapporti_str`
- `target_sito`

### _build_rapporti_from_edges(graph, default_sito)

Walk graph.edges and return a dict {source_node_id: rapporti_list}
where each rapporti_list is the pyarchinit list-of-lists serialisation
`[[type, target_us, area, sito], …]`.

The `target_us` is extracted from the target node's name with the
unita_tipo prefix stripped. `area` defaults to '1' when the graph
didn't preserve it (compatible with most legacy pyarchinit data).

**Parameters:**
- `graph`
- `default_sito`

### _strip_us_prefix(name)

Strip the unita-tipo prefix from a node name.

Examples:
    "USM6"   → "6"
    "USV102" → "102"
    "US103a" → "103a"
    "D.4001" → "4001"
    "C.900"  → "900"
    "6"      → "6"  (no prefix → unchanged)

**Parameters:**
- `name`

### _resolve_unita_tipo(node, attrs)

Return the unita_tipo for *node*, prefering attrs (set by
GraphProjector) over s3dgraphy class name (when graphml round-trip
has stripped attrs).

**Parameters:**
- `node`
- `attrs`

## Classes

### GraphSyncError

Base class for all GraphProjector / GraphIngestor errors.

**Inherits from**: Exception

### GraphIngestError

Write-side failure. Always means DB rolled back to pre-call state.

**Inherits from**: GraphSyncError

### SchemaMismatchError

us_table.node_uuid column missing (Phase 1 migration not applied).

Hint: run scripts/migrations/2026_05_node_uuid_backfill.py --apply.

**Inherits from**: GraphIngestError

### UnknownUnitaTipoError

Graph node has unita_tipo not in the vocabulary.

Hint: run scripts/migrations/2026_05_us_vocabulary_alignment.py --apply.

**Inherits from**: GraphIngestError

### SiteMismatchError

Graph contains a node whose attributes['sito'] != populate_list(sito=...).

**Inherits from**: GraphIngestError

### MissingEpochError

One or more EpochNodes reference (periodo, fase) not present in
periodizzazione_table while create_missing_epochs=False.

The exception carries `missing: list[tuple[int, str]]` so callers
can show all the missing keys at once instead of one per call.

**Inherits from**: GraphIngestError

#### Methods

##### __init__(self, missing)

*No description available.*
### GraphIngestor

Persist a s3dgraphy Graph back to the PyArchInit SQL tables.

Single atomic transaction (BEGIN/COMMIT/ROLLBACK). Idempotent on
re-runs against the same input. AI04 always uses
ConflictResolution.GRAPH_WINS for value diffs.

#### Methods

##### __init__(self, conflict_resolver)

*No description available.*
##### populate_list(self, graph, db_path, sito, dry_run, create_missing_epochs, graphml_path, sql_apply_groups)

See spec §3.2 docstring for full contract.

When *graphml_path* is provided, AI04's custom data-keys
(`pyarchinit.us`, `pyarchinit.area`, etc. — see
graphml_writer._embed_pyarchinit_data_keys) are parsed from
the file and merged into graph node attributes, so the
round-trip preserves columns that s3dgraphy's own importer
would otherwise drop.

AI06 D.2: when *sql_apply_groups* is True (default False), the
importer parses group folder nodes (``yfiles.foldertype="group"``
with ``id="grp_..."``) from the GraphML at *graphml_path* (or
*graph* if it is itself a path-like) and queues
``UPDATE us_table SET <kind>=<group_name>`` for every member
US whose folder maps to a SQL-derived ``group_kind`` (the
basic 7: area / struttura / attivita / settore / ambient /
saggio / quad_par). Ad-hoc groups (group_kind not in this set)
never touch SQL — they always live in the GroupStore (AC-14).

Convenience: when *graph* is a Path-like (str or Path) instead
of a Graph, the importer auto-loads it as a Graph via
s3dgraphy's GraphMLImporter and uses the same path for
graphml_path. This lets callers pass just the .graphml file.

##### _verify_schema(self, db_path)

*No description available.*
##### _verify_sito(self, graph, sito)

Validate the sito parameter.

Note: AI04.1 changed semantics — we no longer raise on graph
nodes carrying a different sito. The user's workflow is "load
this graph and ingest into MY sito X", so we treat the
parameter as authoritative. The per-node loop overrides each
node's sito attribute to *sito* before INSERT/UPDATE.

##### _run(self, graph, db_path, sito, dry_run, create_missing_epochs, graphml_path, sql_apply_groups)

*No description available.*
