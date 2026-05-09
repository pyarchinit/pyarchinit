# modules/db/structures/Media_to_Entity_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Media_to_Entity_table

*No description available.*
Defines the SQLAlchemy table schema for `media_to_entity_table`, which maps media files to application entities. The table stores the relationship between an entity (identified by `id_entity`, `entity_type`, and `table_name`) and a media file (identified by `id_media`, `filepath`, and `media_name`), along with an optional `entity_uuid` field. A composite unique constraint named `ID_mediaToEntity_unico` is enforced on the combination of `id_entity`, `entity_type`, and `id_media` to prevent duplicate associations.

