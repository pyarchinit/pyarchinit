# modules/db/entities/POTTERY_EMBEDDING_METADATA.py

## Overview

This file contains 5 documented elements.

## Classes

### POTTERY_EMBEDDING_METADATA

Entity class for tracking pottery image embeddings.
Used by the visual similarity search system to track which images
have been indexed for each model and search type.

**Inherits from**: object

#### Methods

##### __init__(self, id_embedding, id_rep, id_media, image_hash, model_name, search_type, embedding_version, created_at)

Initializes a `POTTERY_EMBEDDING_METADATA` instance by assigning all provided arguments to their corresponding instance attributes. The parameters include `id_embedding` (primary key), `id_rep` (foreign key to `pottery_table.id_rep`), `id_media` (foreign key to `media_table.id_media`), `image_hash` (SHA256 hash of the image file), `model_name` (the embedding model, e.g. `'clip'`, `'openai'`, or `'dinov2'`), `search_type` (e.g. `'general'`, `'decoration'`, or `'shape'`), `embedding_version` (a version string for model updates), and `created_at` (the timestamp of embedding creation). This record is used by the visual similarity search system to track which images have been indexed for each model and search type.

##### __repr__(self)

Returns an unambiguous string representation of the `POTTERY_EMBEDDING_METADATA` object. The output follows the format `<POTTERY_EMBEDDING_METADATA('id_embedding', 'id_rep', 'id_media', 'image_hash', 'model_name', 'search_type', 'embedding_version', 'created_at')>`, embedding all eight identifying fields of the instance into the string. This method is automatically invoked by `repr()` and is intended for debugging and logging purposes.

##### as_dict(self)

Return entity as dictionary

