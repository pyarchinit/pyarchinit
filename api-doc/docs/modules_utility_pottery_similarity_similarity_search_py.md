# modules/utility/pottery_similarity/similarity_search.py

## Overview

This file contains 17 documented elements.

## Classes

### PotterySimilaritySearchEngine

Main search engine for pottery visual similarity.

Coordinates:
- Embedding model selection and generation
- FAISS index management
- Database metadata tracking
- Search operations with threshold filtering

#### Methods

##### __init__(self, db_manager)

Initialize the search engine.

Args:
    db_manager: PyArchInit database manager instance

##### search_similar(self, query_image_path, model_name, search_type, threshold, auto_crop, edge_preprocessing, segment_decoration, remove_background, custom_prompt, return_top_scores)

Find all images similar to query above threshold.

Args:
    query_image_path: Path to query image
    model_name: Embedding model to use ('clip', 'dinov2', 'openai')
    search_type: Type of search ('general', 'decoration', 'shape')
    threshold: Minimum similarity (0-1)
    auto_crop: If True, auto-crop to region with most detail
    edge_preprocessing: If True, use edge-based preprocessing
    segment_decoration: If True, mask non-decorated areas
    remove_background: If True, remove photo background
    custom_prompt: Custom prompt for semantic search (OpenAI only)
    return_top_scores: If True, returns (results, top_5_scores) tuple

Returns:
    List of dicts with:
    - pottery_id: int
    - media_id: int
    - similarity: float (0-1)
    - similarity_percent: float (0-100)
    - image_path: str (if available)
    - pottery_data: dict (form, decoration, etc.)
    OR tuple (results, top_scores) if return_top_scores=True

##### search_similar_by_pottery_id(self, pottery_id, model_name, search_type, threshold)

Find similar pottery starting from existing record.

If the pottery has multiple images, searches with ALL of them and
returns the best matches (highest similarity) for each found pottery.

Args:
    pottery_id: ID of pottery record (id_rep)
    model_name: Embedding model
    search_type: Type of search
    threshold: Minimum similarity

Returns:
    List of similar pottery (excluding the query pottery itself)

##### search_by_text(self, text_query, model_name, search_type, threshold, return_top_scores)

Search for pottery by text description (semantic search).
Only works with OpenAI model - generates embedding from text and searches index.

Args:
    text_query: Text description of what to search for
    model_name: Must be 'openai' for text search
    search_type: Type of search (for index selection)
    threshold: Minimum similarity (0-1)
    return_top_scores: If True, returns (results, top_5_scores) tuple

Returns:
    List of matching pottery with similarity scores
    OR tuple (results, top_scores) if return_top_scores=True

##### build_index_for_model(self, model_name, search_type, progress_callback)

Build/rebuild index for specific model and search type.

Args:
    model_name: Embedding model to use
    search_type: Type of search
    progress_callback: Optional callback(current, total, message)

Returns:
    True if successful

##### update_index_incremental(self, model_name, search_type, progress_callback)

Update index with only new/changed/deleted images.

Detects:
- NEW: images in DB not in index
- MODIFIED: images where file hash changed
- DELETED: images in index but no longer in DB or file missing

Args:
    model_name: Embedding model
    search_type: Type of search
    progress_callback: Optional progress callback

Returns:
    Dict with counts: {'added': int, 'updated': int, 'removed': int}

##### get_indexing_status(self)

Return status of all indexes.

Returns:
    Dict with counts, status, and info for each model/search_type

### PotterySimilarityWorker

Background worker for similarity search and index building.

Signals:
    search_complete: Emitted when search finishes with results list
    index_progress: Emitted during indexing (current, total, message)
    error_occurred: Emitted on error with message
    operation_complete: Emitted when any operation completes

**Inherits from**: QThread

#### Methods

##### __init__(self, search_engine, operation)

Initialize worker.

Args:
    search_engine: PotterySimilaritySearchEngine instance
    operation: Operation type ('search', 'search_by_id', 'build_index', 'update_index')
    **kwargs: Operation-specific arguments

##### run(self)

Execute operation in background

##### cancel(self)

Cancel ongoing operation

### PotterySimilarityWorker

Placeholder for non-QGIS environments

#### Methods

##### __init__(self)

*No description available.*
Placeholder initializer for non-QGIS environments that unconditionally raises a `RuntimeError`. Accepts any positional and keyword arguments but performs no initialization logic. This constructor exists solely to signal that `PotterySimilarityWorker` cannot be instantiated outside of a QGIS/PyQt environment.

## Functions

### get_thumb_resize_path()

Read THUMB_RESIZE path from pyarchinit config.cfg file.
This is the base directory where resized images are stored.

**Returns:** `Optional[str]`

### build_full_image_path(relative_path, base_path)

Build full image path from relative path_resize and config THUMB_RESIZE.

Args:
    relative_path: Filename from media_thumb_table.path_resize
    base_path: Base directory (THUMB_RESIZE from config)

Returns:
    Full absolute path to image file

**Parameters:**
- `relative_path: str`
- `base_path: Optional[str]`

**Returns:** `str`

