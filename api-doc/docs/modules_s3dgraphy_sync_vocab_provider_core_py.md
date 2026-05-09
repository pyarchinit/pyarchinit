# modules/s3dgraphy/sync/vocab_provider_core.py

## Overview

This file contains 15 documented elements.

## Functions

### _vtuple(s)

Parse a 'M.N.P' version string into a comparable tuple.

**Parameters:**
- `s`

### _first_existing(directory, names)

*No description available.*
**Parameters:**
- `directory`
- `names`

### _merge_dicts(base, override)

Per top-level key merge. override beats base; missing keys preserved.

**Parameters:**
- `base`
- `override`

## Classes

### VocabProviderCore

Parses the s3dgraphy JSON pillars; query API for client tools.

#### Methods

##### __init__(self, bundled_dir, overrides_dir, min_versions)

*No description available.*
##### _enforce_minimum_versions(self)

*No description available.*
##### versions(self)

*No description available.*
##### reload(self)

*No description available.*
##### _load_with_override(self, names)

*No description available.*
##### get_unit_types(self, family)

*No description available.*
##### get_edge_types(self)

*No description available.*
##### get_legal_targets_for(self, source_type, edge_name)

*No description available.*
##### get_paradata_types(self)

*No description available.*
##### get_visual_rule(self, node_type)

*No description available.*
##### get_cidoc_mapping(self, type_abbreviation)

*No description available.*
