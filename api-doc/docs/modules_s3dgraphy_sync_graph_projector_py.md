# modules/s3dgraphy/sync/graph_projector.py

## Overview

This file contains 10 documented elements.

## Functions

### _is_epoch_node(node)

Return True if node is an EpochNode. Defensive — avoids importing
EpochNode at module top because it forces s3dgraphy load too early.

**Parameters:**
- `node`

## Classes

### ProjectionError

Read-side failure during GraphProjector.populate_graph().

**Inherits from**: GraphSyncError

### GraphProjector

Stratigraphic-layer projection from PyArchInit DB to s3dgraphy Graph.

Usage:
    projector = GraphProjector()
    graph = projector.populate_graph(db_path, sito="Scavo archeologico")

The graph contains StratigraphicUnit / USM / USVs / USVn / USD /
SF / VSF / CON / DOC / Extractor / Combinar / property nodes plus
EpochNodes for the (periodo, fase) tuples present in the filtered
rows. Edges follow the rapporti column conventions decoded by
`_RAPPORTI_TO_EDGE_TYPE` and `_RAPPORTI_SHORTHAND` in
graphml_writer.py.

#### Methods

##### __init__(self, vocab_provider)

*No description available.*
##### populate_graph(self, db_path, sito, include_paradata, strict_schema, groups)

Build and return a s3dgraphy.Graph populated with the
stratigraphic rows of `sito` from the SQLite at `db_path`.

Args:
    db_path: filesystem path to the pyarchinit SQLite DB.
    sito: site identifier (`us_table.sito` value). Mandatory
        — multi-graph projections are out of scope for AI04.
    include_paradata: when True (default), merge any
        ``paradata.graphml`` produced by :class:`ParadataStore`
        for the (db, sito) pair. When False, return the pure
        stratigraphic layer (backward-compat for AI04 callers
        like ``graphml_writer.export_graphml``). On read errors
        we log a warning and fall back to strat-only — never
        fatal.
    strict_schema: when True (default), require that the
        Phase-1 migration has been applied (i.e.
        ``us_table.node_uuid`` exists) and propagate node-UUID
        attributes onto each StratigraphicUnit so AI04 can do a
        round-trip. When False, skip both the schema check and
        ``_propagate_node_uuid_and_us``: useful for the AI03
        strat-only export path (``graphml_writer.export_graphml``)
        which only needs labels/edges/swimlanes — node_uuid is
        irrelevant there and AC-2 fixtures pre-date the
        migration.

Returns:
    A populated `s3dgraphy.Graph`. Empty graph (zero nodes) is
    valid: it just means the site has no rows.

Raises:
    ProjectionError: on any failure reaching the DB or
        instantiating the in-memory graph.

##### _verify_node_uuid_column(self, db_path)

Ensure the Phase-1 migration that added ``us_table.node_uuid``
has been applied. Raises :class:`ProjectionError` otherwise.

Extracted from ``populate_graph`` in AI05 Group C step 2 so the
schema-check is testable in isolation and reusable by any future
method that touches strat tables.

##### _merge_paradata(self, graph, db_path, sito)

Read ``paradata.graphml`` for *sito* and add its nodes to
*graph*.

Non-fatal on read errors — logs a warning and returns. The
caller still gets the strat layer.

De-duplication: nodes whose ``node_id`` already exists on the
target graph are skipped (the strat layer wins). Edges from the
paradata graph are NOT merged here; AI05 Group C does
node-only merging because the paradata graph is currently
author/license/embargo nodes with no connecting edges.

##### _propagate_node_uuid_and_us(self, graph, db_path, sito)

Set attributes['node_uuid'], 'us' and the remaining mapped
columns on each StratigraphicUnit-family node.

Match nodes by `name` (the importer emits name=str(us_table.us))
within the requested sito. Idempotent: re-running yields the
same attribute values.

##### _enrich_into(self, graph, db_path, sito_filter)

Phase 2 / Strategy A — full-class implementation.

Body absorbed verbatim from the now-deleted standalone function
formerly named ``_enrich_pyarchinit_graph`` in ``graphml_writer``.

Bake epoch swimlanes + topological rapporti edges into *graph*.

The vendored s3dgraphy 0.1.40 PyArchInitImporter is incomplete:
it imports only US columns mapped in the JSON mapping (us_table
→ StratigraphicNode + PropertyNodes), and does NOT:

  * read periodizzazione_table → create EpochNodes
  * add ``has_first_epoch`` edges from each US to its periodo
  * parse the ``rapporti`` JSON column → create topological edges

Without those, the GraphMLExporter has no input for swimlanes
and no input for the TemporalInferenceEngine — both AI03
acceptance criteria fail. We perform the enrichment here, in
the orchestrator's filter+enrich layer, so the bridge stays a
one-call surface and so the test fixture remains pure
pyArchInit-shaped data.

Mutates the graph in place. No-op if the DB file lacks the
expected tables.

##### _merge_groups(self, graph, db_path, sito, dimensions)

Materialize ActivityNodeGroup nodes + is_in_activity edges
from SQL columns and ad-hoc store. Each group node carries
a ``group_kind`` attribute distinguishing the dimension.

