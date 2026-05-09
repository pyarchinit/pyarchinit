# modules/db/structures_metadata/Media_thumb_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Media_thumb_table

*No description available.*
A SQLAlchemy table definition class representing thumbnail records associated with media files. It exposes a single class method, `define_table`, which constructs and returns a `Table` object named `'media_thumb_table'` containing columns for the thumbnail's unique identifier (`id_media_thumb`), a reference to the originating media file (`id_media`), media type, original and thumbnail filenames, file extension, file paths for both the original and resized versions, and a StratiGraph UUID (`entity_uuid`). A unique constraint named `'ID_media_thumb_unico'` is enforced on the `media_thumb_filename` column to prevent duplicate thumbnail filename entries.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object named `'media_thumb_table'` bound to the provided `metadata`, representing thumbnail records for media files. The table includes columns for a primary key (`id_media_thumb`), a reference to the originating media file (`id_media`), media type, original and thumbnail filenames, file extension, file paths for both the original and resized versions, and a StratiGraph UUID (`entity_uuid`). A unique constraint named `'ID_media_thumb_unico'` is enforced on the `media_thumb_filename` column.

