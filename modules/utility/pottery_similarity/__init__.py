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

__all__ = [
    'EmbeddingModel',
    'CLIPEmbeddingModel',
    'DINOv2EmbeddingModel',
    'OpenAIVisionEmbeddingModel',
    'get_available_models',
    'PotterySimilarityIndexManager',
    'PotterySimilaritySearchEngine',
    'PotterySimilarityWorker'
]
