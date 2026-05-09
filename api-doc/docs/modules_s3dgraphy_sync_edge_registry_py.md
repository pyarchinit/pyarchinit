# modules/s3dgraphy/sync/edge_registry.py

## Overview

This file contains 4 documented elements.

## Functions

### _load_visual_rules()

Load em_visual_rules.json once. Returns None on failure.

### _load_connections_datamodel()

Load s3Dgraphy_connections_datamodel.json once.

### resolve_edge_style(edge_type)

Return the style dict for *edge_type*, or None if not known.

Lookup order:
    1. _PYARCHINIT_EDGE_OVERRIDES (override-wins)
    2. em_visual_rules.json edge_style.{edge_type}.style
    3. None (caller uses default)

Returned dict shape: {"color": "#RRGGBB", "line_style": "solid"|"dashed"|"dotted",
                      "width": int}

**Parameters:**
- `edge_type`

### is_paradata_edge(edge_type)

True iff *edge_type* is a paradata-flow edge (rendered dashed in
the AI03 post-processor; excluded from rapporti round-trip in AI04).

Uses the connections datamodel when available — paradata edges have
`allowed_connections.source` or `.target` containing PropertyNode /
DocumentNode / ExtractorNode / CombinerNode. Falls back to the
hardcoded `_HARDCODED_PARADATA_EDGES` set when the datamodel is
unavailable.

**Parameters:**
- `edge_type`

