# modules/db/entities/MEDIA.py

## Overview

This file contains 4 documented elements.

## Classes

### MEDIA

*No description available.*
A data class representing a media record, encapsulating metadata associated with a media file. It stores attributes including a numeric identifier (`id_media`), media type (`mediatype`), filename, file type, file path, description (`descrizione`), and tags. A universally unique identifier (`entity_uuid`) is automatically generated via `uuid.uuid4()` if one is not explicitly provided at instantiation.

**Inherits from**: object

#### Methods

##### __init__(self, id_media, mediatype, filename, filetype, filepath, descrizione, tags, entity_uuid)

## `__init__` — `MEDIA` Class Constructor

Initializes a new `MEDIA` instance by assigning the provided media metadata to the corresponding instance attributes. Accepts `id_media`, `mediatype`, `filename`, `filetype`, `filepath`, `descrizione`, and `tags` as required parameters, along with an optional `entity_uuid` parameter. If `entity_uuid` is not supplied or evaluates to a falsy value, a new UUID4 string is automatically generated and assigned via `uuid.uuid4()`.

##### __repr__(self)

*No description available.*
Returns an unambiguous string representation of the `MEDIA` object. The returned string follows the format `<MEDIA('id_media', 'mediatype', 'filename', filetype, 'filepath', 'descrizione')>`, incorporating the instance's `id_media`, `mediatype`, `filename`, `filetype`, `filepath`, and `descrizione` fields. This method is intended for debugging and logging purposes, providing a readable summary of the object's core attributes.

