# modules/s3dgraphy/sync/vocab_provider.py

## Overview

This file contains 13 documented elements.

## Functions

### _default_bundled_dir()

Locate the bundled JSON_config/ inside ext_libs/s3dgraphy/.

### _default_overrides_dir()

User-writable overrides location.

### get_default_provider()

*No description available.*
## Classes

### VocabProvider

Process-wide vocabulary provider with hot-reload.

**Inherits from**: QObject if _HAS_QT else object

#### Methods

##### __init__(self, bundled_dir, overrides_dir, parent)

*No description available.*
##### _on_directory_changed(self, path)

*No description available.*
##### get_unit_types(self, *args, **kwargs)

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
##### versions(self)

*No description available.*
