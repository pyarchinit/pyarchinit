# modules/db/entities/MEDIAVIEW.py

## Overview

This file contains 4 documented elements.

## Classes

### MEDIAVIEW

*No description available.*
A plain Python data class that represents a media view record, encapsulating metadata for a media thumbnail and its associated entity. It stores attributes including `id_media_thumb`, `id_media`, `filepath`, `path_resize`, `entity_type`, `id_media_m`, and `id_entity`. The `__repr__` method returns a formatted string representation of all stored field values for identification and debugging purposes.

**Inherits from**: object

#### Methods

##### __init__(self, id_media_thumb, id_media, filepath, path_resize, entity_type, id_media_m, id_entity)

## `__init__` — `MEDIAVIEW`

Initializes a new instance of the `MEDIAVIEW` class by assigning the provided arguments to their corresponding instance attributes. Accepts seven parameters — `id_media_thumb`, `id_media`, `filepath`, `path_resize`, `entity_type`, `id_media_m`, and `id_entity` — each stored directly on the instance without transformation. This constructor establishes the core data fields representing a media view record, including identifiers, file paths, and entity metadata.

##### __repr__(self)

*No description available.*
Returns an unambiguous string representation of the `MEDIAVIEW` object. The output follows the format `<MEDIAVIEW('id_media_thumb', 'id_media', 'filepath', 'path_resize', 'entity_type', 'id_media_m', 'id_entity')>`, embedding the instance's corresponding field values in that order. This method is intended for debugging and logging purposes.

