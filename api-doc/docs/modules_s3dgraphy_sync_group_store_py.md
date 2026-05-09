# modules/s3dgraphy/sync/group_store.py

## Overview

This file contains 25 documented elements.

## Functions

### _sito_slug(sito)

Filename-safe lowercase slug for a sito identifier (matches AI05).

**Parameters:**
- `sito`

## Classes

### GroupStoreError

Base for GroupStore errors.

**Inherits from**: GraphSyncError

### GroupReadError

File parse / schema error during read().

**Inherits from**: GroupStoreError

### GroupWriteError

File write / atomic-rename failure during write().

**Inherits from**: GroupStoreError

### GroupValidationError

Caller passed bogus data to add_group/add_us_to_group/etc.

**Inherits from**: GroupStoreError

### GroupNotFoundError

Required file or group_uuid missing where caller expected it.

**Inherits from**: GroupStoreError

### GroupStore

Site-scoped CRUD for groups.graphml.

#### Methods

##### __init__(self, db_path, sito)

*No description available.*
##### file_path(self)

*No description available.*
##### exists(self)

*No description available.*
##### sito(self)

*No description available.*
##### read(self)

Return a Graph populated only with ad-hoc group nodes from
the file. Returns empty Graph when file absent.

##### _hydrate_group_attrs(self, graph)

Re-parse the file and merge `pyarchinit.group_attrs` JSON
blob back onto each node's `.attributes` dict.

##### write(self, graph)

Atomic write via .tmp + os.replace.

##### _write_minimal_graphml(self, graph, out_path)

Emit a minimal GraphML containing only the group nodes.

##### _emit_group_node(graph_el, node, ns_graphml, ns_y)

Append a single group <node> with the EM canonical layout.

##### add_node(self, node)

Append *node* to the group graph + write.

##### remove_node(self, group_uuid)

Idempotent — no error if uuid not found.

##### find(self, group_kind, **kwargs)

Return matching group nodes.

##### add_group(self, name, group_kind, member_us_uuids, description)

Create + persist an ActivityNodeGroup. Returns uuid7.

##### list_groups(self)

Return [{group_uuid, name, group_kind, member_us_uuids, description}].

##### remove_group(self, group_uuid)

Alias for remove_node — high-level naming.

##### add_us_to_group(self, group_uuid, us_uuid)

Append us_uuid to the group's member list. Idempotent on
duplicate. Raises GroupNotFoundError if group_uuid unknown.

##### remove_us_from_group(self, group_uuid, us_uuid)

Idempotent — no error if us_uuid not in member list.

##### list_members(self, group_uuid)

Return the list of us_uuid strings of a group.

