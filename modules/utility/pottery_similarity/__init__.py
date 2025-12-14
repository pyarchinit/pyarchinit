"""
Pottery Visual Similarity Search Module

This module provides AI-powered visual similarity search for pottery images
using multiple embedding models (CLIP, DINOv2, OpenAI Vision API).

Features:
- Multiple embedding models support
- Configurable similarity threshold
- Different search types (decoration, shape, general)
- FAISS-based fast similarity search
- Background index building

Author: Enzo Cocca <enzo.ccc@gmail.com>
"""

from .embedding_models import (
    EmbeddingModel,
    CLIPEmbeddingModel,
    DINOv2EmbeddingModel,
    OpenAIVisionEmbeddingModel,
    get_available_models
)
from .index_manager import PotterySimilarityIndexManager
from .similarity_search import (
    PotterySimilaritySearchEngine,
    PotterySimilarityWorker
)
from .embedding_index_updater import (
    EmbeddingIndexUpdater,
    get_embedding_updater,
    set_auto_update_enabled,
    set_auto_update_models
)

__all__ = [
    'EmbeddingModel',
    'CLIPEmbeddingModel',
    'DINOv2EmbeddingModel',
    'OpenAIVisionEmbeddingModel',
    'get_available_models',
    'PotterySimilarityIndexManager',
    'PotterySimilaritySearchEngine',
    'PotterySimilarityWorker',
    'EmbeddingIndexUpdater',
    'get_embedding_updater',
    'set_auto_update_enabled',
    'set_auto_update_models'
]
