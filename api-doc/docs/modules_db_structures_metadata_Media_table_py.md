# modules/db/structures_metadata/Media_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Media_table

*No description available.*
Defines the SQLAlchemy table schema for storing media files associated with archaeological records. The class exposes a single class method, `define_table(cls, metadata)`, which constructs and returns a `Table` object named `'media_table'` containing columns for a primary key (`id_media`), media type, filename, file extension (`filetype`, max 10 characters), file path, description (`descrizione`), tags, and a StratiGraph UUID (`entity_uuid`). A unique constraint (`ID_media_unico`) is enforced on the `filepath` column to prevent duplicate file path entries.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object named `'media_table'` bound to the provided `metadata`, representing media files associated with archaeological records. The table includes columns for a primary key (`id_media`), media type, filename, file extension (`filetype`, max 10 characters), file path, description (`descrizione`), tags, and a StratiGraph UUID (`entity_uuid`). A unique constraint named `'ID_media_unico'` is enforced on the `filepath` column to prevent duplicate file path entries.

