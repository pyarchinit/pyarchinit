# modules/stratigraph/uuid_manager.py

## Overview

This file contains 6 documented elements.

## Functions

### generate_uuid()

Generate a new UUID v4 string.

Returns:
    str: A new UUID v4 in lowercase hyphenated format.

### validate_uuid(value)

Validate that a string is a properly formatted UUID v4.

Args:
    value: The value to validate.

Returns:
    bool: True if value is a valid UUID v4 string.

**Parameters:**
- `value`

### ensure_uuid(record)

Ensure a record has a valid entity_uuid, generating one if missing.

Checks the record's entity_uuid attribute. If it is None, empty,
or not a valid UUID v4, a new UUID is generated and assigned.

Args:
    record: Any object with an entity_uuid attribute.

Returns:
    str: The (possibly newly assigned) UUID.

**Parameters:**
- `record`

### build_uri(entity_type, entity_uuid, base_uri)

Construct a persistent URI for an entity.

Args:
    entity_type: The entity type slug (e.g. 'stratigraphic-unit')
        or the table name (e.g. 'us_table').
    entity_uuid: The entity's UUID.
    base_uri: Optional base URI. Defaults to DEFAULT_BASE_URI.

Returns:
    str: A URI in the format {base_uri}{type}/{uuid}

**Parameters:**
- `entity_type`
- `entity_uuid`
- `base_uri`

### get_entity_type_for_table(table_name)

Get the entity type slug for a given table name.

Args:
    table_name: The database table name.

Returns:
    str: The entity type slug, or the table name itself if not mapped.

**Parameters:**
- `table_name`

