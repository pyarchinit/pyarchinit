# modules/s3dgraphy/sync/ingest_result.py

## Overview

This file contains 3 documented elements.

## Classes

### ConflictResolution

Outcome of a single field-level conflict during ingest.

AI04 always uses GRAPH_WINS (the bridge prototype implements
'last writer wins' policy from parent spec §6.4). DB_WINS and
SKIPPED are reserved for AI06+ pluggable resolvers.

**Inherits from**: str, Enum

### ConflictRecord

A single field-level conflict detected during ingestion.

A row is inserted into IngestResult.conflicts when the graph
node has a value different from the DB row for one of the
MAPPED_COLUMNS and the resolver decides how to merge.

### IngestResult

Aggregated outcome of GraphIngestor.populate_list().

Counters and the conflict / error lists let callers (CLI, UI,
test) summarise the ingestion without re-walking the graph.

