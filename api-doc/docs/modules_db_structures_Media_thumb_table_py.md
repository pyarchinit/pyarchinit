# modules/db/structures/Media_thumb_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Media_thumb_table

*No description available.*
Defines the SQLAlchemy table schema for `media_thumb_table`, which stores metadata and file path information for media files and their associated thumbnails. The table includes columns for identifiers (`id_media_thumb`, `id_media`), media type and file type classification, original and resized file paths, and a UUID for entity association. A unique constraint named `ID_media_thumb_unico` is enforced on the `media_thumb_filename` column to prevent duplicate thumbnail entries.

