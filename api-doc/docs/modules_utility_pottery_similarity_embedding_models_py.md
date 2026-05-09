# modules/utility/pottery_similarity/embedding_models.py

## Overview

This file contains 38 documented elements.

## Classes

### EmbeddingModel

Abstract base class for embedding models

**Inherits from**: ABC

#### Methods

##### get_embedding(self, image_path, search_type, auto_crop, edge_preprocessing)

Generate embedding for a single image.

Args:
    image_path: Path to the image file
    search_type: Type of search ('general', 'decoration', 'shape')
    auto_crop: If True, auto-crop to region with most detail (for decoration)
    edge_preprocessing: If True, use edge-based preprocessing (better for textures)

Returns:
    numpy array of embeddings or None if failed

##### get_embedding_dimension(self)

Return the embedding dimension for this model

##### model_name(self)

Return model identifier

##### supported_search_types(self)

Return list of supported search types

##### normalize_similarity(self, raw_score)

Normalize raw similarity score to 0-100% scale.
Override in subclasses for model-specific normalization.

### CLIPEmbeddingModel

CLIP model via sentence-transformers (local, runs in subprocess)

**Inherits from**: EmbeddingModel

#### Methods

##### __init__(self, venv_python)

Initializes a CLIP model instance that runs via sentence-transformers in a subprocess. Accepts an optional `venv_python` parameter specifying the path to the Python executable; if not provided, the path is resolved automatically by calling `_find_venv_python()`. Also sets the `_runner_script` attribute by invoking `_get_runner_script_path()`.

##### model_name(self)

*No description available.*
**Signature:** `model_name(self) -> str`

A read-only property that returns the name of the embedding model used by this component. Returns the string `'clip'`, identifying CLIP as the underlying model. This property is part of the class interface alongside `supported_search_types` and the embedding runner script path.

##### supported_search_types(self)

*No description available.*
**Type:** Property

Returns a list of search type identifiers supported by the CLIP model. The returned list contains three string values: `'general'`, `'decoration'`, and `'shape'`. This property can be used to determine which search type values are valid inputs for methods such as `get_embedding`.

##### get_embedding_dimension(self)

*No description available.*
Returns the dimensionality of the embedding vectors produced by this model as an integer. The value is retrieved from the class-level constant `EMBEDDING_DIM`.

##### get_embedding(self, image_path, search_type, auto_crop, edge_preprocessing, segment_decoration, remove_background, custom_prompt)

Generate CLIP embedding via subprocess

Args:
    image_path: Path to image file
    search_type: 'general', 'decoration', or 'shape'
    auto_crop: Crop to region with most detail
    edge_preprocessing: Use edge-based preprocessing for decoration
    segment_decoration: Mask non-decorated areas (isolate decoration only)
    remove_background: Remove photo background from pottery
    custom_prompt: Ignored for CLIP (only used by OpenAI)

##### normalize_similarity(self, raw_score)

CLIP similarity: map [0.5, 1.0] to [0, 100]

### DINOv2EmbeddingModel

DINOv2 (Meta) for self-supervised visual features (local, runs in subprocess)

**Inherits from**: EmbeddingModel

#### Methods

##### __init__(self, venv_python)

Initializes a DINOv2 local embedding instance configured to run in a subprocess. Sets `venv_python` to the provided Python executable path, or resolves it automatically via `_find_venv_python()` if none is supplied. Also resolves and stores the runner script path by calling `_get_runner_script_path()`.

##### model_name(self)

*No description available.*
**Signature:** `model_name(self) -> str`

A read-only property that returns the name of the embedding model used by this component. Returns the string `'dinov2'`, identifying the DINOv2 model as the underlying vision model. This property is defined as a `@property` and takes no additional parameters.

##### supported_search_types(self)

*No description available.*
**Type:** Property

Returns a list of search type identifiers supported by the DINOv2 model. The supported values are `'general'`, `'decoration'`, and `'shape'`. This property can be used to validate or enumerate the search types accepted by the `get_embedding` method.

##### get_embedding_dimension(self)

*No description available.*
Returns the dimensionality of the embedding vectors produced by this model as an integer. The value is retrieved from the class-level constant `EMBEDDING_DIM`.

##### get_embedding(self, image_path, search_type, auto_crop, edge_preprocessing, segment_decoration, remove_background, custom_prompt)

Generate DINOv2 embedding via subprocess

Args:
    image_path: Path to image file
    search_type: 'general', 'decoration', or 'shape'
    auto_crop: Crop to region with most detail
    edge_preprocessing: Use edge-based preprocessing for decoration
    segment_decoration: Mask non-decorated areas (isolate decoration only)
    remove_background: Remove photo background from pottery
    custom_prompt: Ignored for DINOv2 (only used by OpenAI)

##### normalize_similarity(self, raw_score)

DINOv2 similarity: map [0.4, 1.0] to [0, 100]

### OpenAIVisionEmbeddingModel

OpenAI Vision API for embeddings (cloud) with specialized prompts

**Inherits from**: EmbeddingModel

#### Methods

##### __init__(self, api_key)

*No description available.*
Initializes the instance by accepting an optional API key string. If no `api_key` is provided, the key is automatically retrieved by calling `_load_api_key()`. The resolved key is stored in `self.api_key`, and `self._client` is initialized to `None`.

##### model_name(self)

*No description available.*
**Signature:** `model_name(self) -> str`

A read-only property that returns the name identifier of the underlying model provider. Always returns the string `'openai'`.

##### supported_search_types(self)

*No description available.*
**Type:** Property

Returns a list of search type identifiers supported by the OpenAI model implementation. The property provides the three supported types: `'general'`, `'decoration'`, and `'shape'`, each corresponding to a specialized prompt variant. This list can be used to validate or enumerate the search modes available for embedding and querying operations.

##### get_embedding_dimension(self)

*No description available.*
Returns the dimensionality of the embedding vectors produced by this model as an integer. The value is retrieved from the class-level constant `EMBEDDING_DIM`.

##### get_embedding(self, image_path, search_type, auto_crop, edge_preprocessing, segment_decoration, remove_background, custom_prompt)

Generate embedding via OpenAI API using specialized prompts
Note: auto_crop, edge_preprocessing, segment_decoration, remove_background are ignored
for OpenAI (uses text description approach, not image preprocessing)

Args:
    custom_prompt: If provided, uses this prompt instead of the search_type preset.
                  This allows semantic searches like "ceramica con decorazione a bande".

##### normalize_similarity(self, raw_score)

OpenAI embeddings: map [0, 1] to [0, 100]

### KhutmCLIPEmbeddingModel

KhutmML-CLIP: Fine-tuned CLIP model for archaeological pottery.

This model uses a CLIP base with a fine-tuned projection layer
trained specifically on pottery images from PyArchInit.

**Inherits from**: EmbeddingModel

#### Methods

##### __init__(self, venv_python, model_dir)

Initializes a `KhutmCLIP` instance by setting the virtual environment Python executable path and the model directory, falling back to `_find_venv_python()` and `MODEL_DIR` respectively if no values are provided. It then checks for the availability of a fine-tuned model via `_check_model_available()` and stores the result in `_model_available`. A status message is printed to indicate whether a fine-tuned model was found at the resolved `model_dir` or whether training is required.

##### model_name(self)

*No description available.*
**Type:** `property`  
**Returns:** `str`

A read-only property that returns the identifier string for this model. The value is always `'khutm_clip'`, representing the fixed name of the underlying CLIP-based model. This property provides a consistent reference to the model's name across the class.

##### supported_search_types(self)

*No description available.*
**Type:** Property

Returns a list of search type identifiers supported by the `khutm_clip` model. The property provides the fixed set of three supported categories: `'general'`, `'decoration'`, and `'shape'`. This read-only property can be used to determine which search modes are valid for use with this model.

##### get_embedding_dimension(self)

*No description available.*
Returns the embedding dimension size used by the model, as defined by the class-level constant `EMBEDDING_DIM`. This value represents the fixed dimensionality of the embedding vectors produced by the model.

##### is_available(self)

Check if the model is available for use

##### get_embedding(self, image_path, search_type, auto_crop, edge_preprocessing, segment_decoration, remove_background, custom_prompt)

Generate embedding using KhutmML-CLIP fine-tuned model.

Falls back to regular CLIP if fine-tuned model not available.

##### normalize_similarity(self, raw_score)

Same normalization as CLIP

## Functions

### get_available_models()

Return dictionary of available embedding models with their info.

Returns:
    dict: {model_name: {'class': ModelClass, 'dim': int, 'search_types': list, 'local': bool}}

**Returns:** `dict`

### get_model_instance(model_name)

Factory function to get an embedding model instance.

Args:
    model_name: Name of the model ('clip', 'dinov2', 'openai')
    **kwargs: Additional arguments for the model constructor

Returns:
    EmbeddingModel instance or None if model not found

**Parameters:**
- `model_name: str`

**Returns:** `Optional[EmbeddingModel]`

