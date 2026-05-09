# modules/db/structures_metadata/Media_to_Entity_table_view.py

## Overview

This file contains 3 documented elements.

## Classes

### Media_to_Entity_table_view

*No description available.*
A SQLAlchemy table definition class that maps the `mediaentity_view` database view, representing relationships between media thumbnails and archaeological entities. It exposes a single class method, `define_table`, which constructs and returns a `Table` object bound to the provided `metadata`, declaring columns for thumbnail identifiers (`id_media_thumb`), original media references (`id_media`, `id_media_m`), file paths (`filepath`, `path_resize`), the archaeological entity type (`entity_type`), and the related entity identifier (`id_entity`). The primary key of the view is `id_media_thumb`.

#### Methods

##### define_table(self, metadata)

Defines and returns a SQLAlchemy `Table` object named `'mediaentity_view'` bound to the provided `metadata`, representing a database view that maps media thumbnails to their associated archaeological entities. The table includes columns for the thumbnail identifier (`id_media_thumb`, primary key), original media file references (`id_media`, `filepath`), a resized thumbnail path (`path_resize`), the archaeological entity type (`entity_type`), a secondary media reference (`id_media_m`), and the related entity identifier (`id_entity`). This is a class method that accepts a `metadata` argument used to register the table definition within the SQLAlchemy metadata context.

