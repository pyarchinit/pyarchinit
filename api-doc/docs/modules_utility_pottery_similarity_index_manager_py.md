# modules/utility/pottery_similarity/index_manager.py

## Overview

This file contains 17 documented elements.

## Classes

### PotterySimilarityIndexManager

Manages FAISS indexes for pottery similarity search.

Each combination of (model_name, search_type) has its own index.
Indexes are stored in ~/pyarchinit/bin/pottery_similarity/

Uses IndexIDMap to allow incremental updates (add/remove by media_id).

#### Methods

##### __init__(self, db_manager)

Initialize the index manager.

Args:
    db_manager: Optional PyArchInit database manager for metadata operations

##### get_index(self, model_name, search_type)

Load or create FAISS index for model/search_type combination.

Args:
    model_name: Embedding model name ('clip', 'dinov2', 'openai')
    search_type: Search type ('general', 'decoration', 'shape')

Returns:
    Tuple of (FAISS index, id_mapping dict)

##### add_embedding(self, model_name, search_type, embedding, pottery_id, media_id, image_hash)

Add embedding to appropriate index.

Args:
    model_name: Embedding model name
    search_type: Search type
    embedding: Normalized embedding vector
    pottery_id: Pottery record ID (id_rep)
    media_id: Media file ID (id_media) - used as FAISS ID
    image_hash: Optional SHA256 hash of image for change detection

Returns:
    True if successful

##### search(self, model_name, search_type, query_embedding, threshold, max_results)

Search for similar images above threshold.

Args:
    model_name: Embedding model name
    search_type: Search type
    query_embedding: Query embedding vector (normalized)
    threshold: Minimum similarity threshold (0-1)
    max_results: Maximum number of results to return

Returns:
    List of dicts with pottery_id, media_id, similarity score

##### get_top_scores(self, model_name, search_type, query_embedding, top_k)

Get top K similarity scores without filtering by threshold.
Useful for showing users what scores are available.

Returns:
    List of top K similarity scores (0-1 range)

##### remove_embedding(self, model_name, search_type, media_id)

Remove embedding from index by media_id.

Uses IndexIDMap.remove_ids() for direct removal.

Args:
    model_name: Embedding model name
    search_type: Search type
    media_id: Media file ID to remove

Returns:
    True if successfully removed

##### rebuild_index(self, model_name, search_type, embeddings)

Rebuild entire index from scratch.

Args:
    model_name: Embedding model name
    search_type: Search type
    embeddings: List of (embedding, pottery_id, media_id, image_hash) tuples
               image_hash can be None

Returns:
    True if successful

##### save_indexes(self)

Persist all modified indexes to disk.

Returns:
    True if all saves successful

##### get_index_stats(self)

Get statistics about all indexes.

Returns:
    Dict with counts and info for each index

##### clear_index(self, model_name, search_type)

Clear an index completely.

Args:
    model_name: Embedding model name
    search_type: Search type

Returns:
    True if successful

##### clear_all_indexes(self)

Clear all indexes

##### get_indexed_media_ids(self, model_name, search_type)

Get set of media_ids currently in the index

##### get_indexed_hashes(self, model_name, search_type)

Get dict of media_id -> image_hash for all indexed images

##### update_embedding(self, model_name, search_type, embedding, pottery_id, media_id, image_hash)

Update existing embedding (remove old, add new).

Args:
    model_name: Embedding model name
    search_type: Search type
    embedding: New embedding vector
    pottery_id: Pottery record ID
    media_id: Media file ID
    image_hash: New image hash

Returns:
    True if successful

## Functions

### compute_image_hash(image_path)

Compute SHA256 hash of an image file for change detection.

Args:
    image_path: Path to image file

Returns:
    SHA256 hex string or None if error

**Parameters:**
- `image_path: str`

**Returns:** `Optional[str]`

