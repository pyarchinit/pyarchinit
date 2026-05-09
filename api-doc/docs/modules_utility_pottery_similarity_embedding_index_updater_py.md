# modules/utility/pottery_similarity/embedding_index_updater.py

## Overview

This file contains 15 documented elements.

## Classes

### EmbeddingIndexUpdater

Manages automatic updates to FAISS indexes when pottery images change.

This class provides hooks that should be called when:
- An image is added to a pottery record (on_image_added)
- An image is removed from a pottery record (on_image_removed)
- An image file is modified (on_image_modified)

Updates are performed asynchronously in a background thread to avoid
blocking the UI.

**Inherits from**: <ast.IfExp object at 0x10f321b80>

#### Methods

##### __init__(self, db_manager, enabled, models, search_types)

Initialize the index updater.

Args:
    db_manager: PyArchInit database manager
    enabled: Whether auto-update is enabled
    models: List of models to update ('clip', 'dinov2', 'openai')
    search_types: List of search types ('general', 'decoration', 'shape')

##### set_enabled(self, enabled)

Enable or disable automatic index updates

##### set_models(self, models)

Set which models to update automatically

##### on_image_added(self, pottery_id, media_id, image_path, async_update)

Called when an image is linked to a pottery record.

Args:
    pottery_id: The pottery record ID (id_rep)
    media_id: The media record ID (id_media)
    image_path: Optional full path to image (will be looked up if not provided)
    async_update: If True, update in background thread

Returns:
    True if update was initiated/completed successfully

##### on_image_removed(self, pottery_id, media_id, async_update)

Called when an image is unlinked from a pottery record.

Args:
    pottery_id: The pottery record ID (id_rep)
    media_id: The media record ID (id_media)
    async_update: If True, update in background thread

Returns:
    True if update was initiated/completed successfully

##### on_image_modified(self, pottery_id, media_id, image_path, async_update)

Called when an image file is modified (re-uploaded/replaced).

Args:
    pottery_id: The pottery record ID (id_rep)
    media_id: The media record ID (id_media)
    image_path: Optional full path to image
    async_update: If True, update in background thread

Returns:
    True if update was initiated/completed successfully

##### get_status(self)

Get current status of the updater

### EmbeddingUpdateWorker

Background worker for embedding updates

**Inherits from**: QThread

#### Methods

##### __init__(self, updater, operation)

Initializes an `EmbeddingUpdateWorker` instance by calling the parent `QThread` constructor and storing the provided arguments as instance attributes. Accepts an `EmbeddingIndexUpdater` instance and an operation dictionary, assigning them to `self.updater` and `self.operation` respectively.

##### run(self)

Execute the update operation

## Functions

### get_embedding_updater(db_manager)

Get the singleton EmbeddingIndexUpdater instance.

Args:
    db_manager: PyArchInit database manager (only needed on first call)

Returns:
    EmbeddingIndexUpdater instance

**Parameters:**
- `db_manager`

**Returns:** `EmbeddingIndexUpdater`

### set_auto_update_enabled(enabled)

Enable or disable automatic index updates globally

**Parameters:**
- `enabled: bool`

### set_auto_update_models(models)

Set which models to update automatically

**Parameters:**
- `models: List[str]`

