# modules/db/structures/Media_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Media_table

*No description available.*
Defines the SQLAlchemy table schema for `media_table`, which stores metadata records describing media files within the pyarchinit database. Each record captures attributes including a unique integer primary key (`id_media`), media type, filename, file type, file path, description, tags, and an entity UUID. A unique constraint named `ID_media_unico` is enforced on the `filepath` column to prevent duplicate file path entries.

