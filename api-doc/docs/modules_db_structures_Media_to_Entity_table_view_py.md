# modules/db/structures/Media_to_Entity_table_view.py

## Overview

This file contains 2 documented elements.

## Classes

### Media_to_Entity_table_view

*No description available.*
Defines the SQLAlchemy table metadata mapping for the `mediaentity_view` database view, which associates media thumbnails and their file paths with specific entities. The class declares a `Table` object with columns for media identifiers (`id_media_thumb`, `id_media`), file path information (`filepath`, `path_resize`), and entity references (`entity_type`, `id_entity`, `id_media_m`). Table creation is intentionally deferred and not executed at module import time.

