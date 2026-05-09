# modules/db/entities/MEDIA_THUMB.py

## Overview

This file contains 4 documented elements.

## Classes

### MEDIA_THUMB

*No description available.*
A data container class representing a media thumbnail record. It stores identifying and file-related attributes for a thumbnail associated with a parent media item, including the media type, original filename, thumbnail filename, file type, file path, and resize path. Each instance is assigned a unique `entity_uuid` via `uuid.uuid4()` if one is not explicitly provided.

**Inherits from**: object

#### Methods

##### __init__(self, id_media_thumb, id_media, mediatype, media_filename, media_thumb_filename, filetype, filepath, path_resize, entity_uuid)

## `__init__` — `MEDIA_THUMB`

Initializes a `MEDIA_THUMB` instance by assigning the provided media thumbnail attributes to their corresponding instance fields. Accepts required parameters for `id_media_thumb`, `id_media`, `mediatype`, `media_filename`, `media_thumb_filename`, `filetype`, `filepath`, and `path_resize`, along with an optional `entity_uuid`. If `entity_uuid` is not provided or evaluates to falsy, a new UUID4 string is automatically generated and assigned.

##### __repr__(self)

*No description available.*
Returns an unambiguous string representation of the `MEDIA_THUMB` object. The output is formatted as `<MEDIA_THUMB('id_media_thumb', 'id_media', 'mediatype', 'media_filename', media_thumb_filename, 'filetype', 'filepath', 'path_resize')>`, embedding the instance's core fields in a fixed positional format. This method is intended for debugging and logging purposes.

