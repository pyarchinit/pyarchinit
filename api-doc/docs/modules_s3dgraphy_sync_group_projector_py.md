# modules/s3dgraphy/sync/group_projector.py

## Overview

This file contains 4 documented elements.

## Functions

### dimensions_with_data(db_path, sito)

Return subset of {area, struttura, attivita, settore,
ambient, saggio, quad_par} that has at least one non-empty
value in us_table for *sito*. Used by the dialog UI to
pre-check the right boxes (D2).

**Parameters:**
- `db_path`
- `sito`

### build_groups_from_sql(db_path, sito, dimensions)

For each requested dimension, scan us_table for distinct
non-empty values within sito, and emit one GroupSpec per
(dimension, value) pair.

UUID generation: deterministic UUID5 from
(sito, group_kind, name) so re-export produces identical
UUIDs (AC-7 idempotent invariant).

Unknown dimension names (typos) are silently skipped (logged).

**Parameters:**
- `db_path`
- `sito`
- `dimensions`

### merge_adhoc_groups(sql_specs, store)

Append GroupSpec instances from groups_{sito}.graphml.

Collision policy: if an ad-hoc group has the same name as an
SQL-derived group (regardless of group_kind), the ad-hoc is
SKIPPED and a warning is logged. SQL "wins". This matches
spec §10 D6 risk mitigation.

**Parameters:**
- `sql_specs`
- `store`

## Classes

### GroupSpec

Pre-render specification of a group.

Resolved to ActivityNodeGroup by GraphProjector._merge_groups.

