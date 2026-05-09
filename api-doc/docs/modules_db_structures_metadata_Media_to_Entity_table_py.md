# modules/db/structures_metadata/Media_to_Entity_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Media_to_Entity_table

*No description available.*
Defines the SQLAlchemy table schema for `media_to_entity_table`, which maps relationships between media files and archaeological entities. The table stores identifying information for both sides of the relationship, including the entity's ID, type, source table name, and UUID, alongside the media file's ID, file path, and name. A unique constraint (`ID_mediaToEntity_unico`) enforces that each combination of `id_entity`, `entity_type`, and `id_media` remains distinct within the table.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object named `'media_to_entity_table'` bound to the provided `metadata`, representing the relationships between media files and archaeological entities. The table includes columns for a primary key (`id_mediaToEntity`), entity identifiers (`id_entity`, `entity_type`, `table_name`, `entity_uuid`), and media file attributes (`id_media`, `filepath`, `media_name`). A unique constraint named `'ID_mediaToEntity_unico'` is enforced on the combination of `id_entity`, `entity_type`, and `id_media` to prevent duplicate media-entity associations.

