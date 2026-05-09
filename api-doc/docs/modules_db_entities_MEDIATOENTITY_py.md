# modules/db/entities/MEDIATOENTITY.py

## Overview

This file contains 4 documented elements.

## Classes

### MEDIATOENTITY

*No description available.*
Represents an association between a media asset and an entity, storing the relationship metadata required to link a media file to a specific record in a given database table. Each instance holds identifiers for both the entity (`id_entity`, `id_media`) and the entity's type and table name, along with the media file's path and name. A UUID is automatically generated for `entity_uuid` if one is not explicitly provided at instantiation.

**Inherits from**: object

#### Methods

##### __init__(self, id_mediaToEntity, id_entity, entity_type, table_name, id_media, filepath, media_name, entity_uuid)

Initializes a `MEDIATOENTITY` instance representing an association between a media item and an entity. Assigns the provided values to the corresponding instance attributes: `id_mediaToEntity`, `id_entity`, `entity_type`, `table_name`, `id_media`, `filepath`, and `media_name`. The `entity_uuid` attribute is set to the supplied value if provided, otherwise a new UUID4 string is generated automatically via `uuid.uuid4()`.

##### __repr__(self)

Returns a string representation of the `MEDIATOENTITY` object in a structured format.

The output string contains the following fields in order: `id_mediaToEntity`, `id_entity`, `entity_type`, `table_name`, `id_media`, `filepath`, and `media_name`, enclosed within `<MEDIATOENTITY(...)>` angle brackets. Integer fields (`id_mediaToEntity`, `id_entity`, `id_media`) are formatted as integers, while the remaining fields are formatted as strings.

