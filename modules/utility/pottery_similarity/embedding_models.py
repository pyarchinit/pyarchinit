"""
Embedding Models for Pottery Visual Similarity Search

This module provides abstract base class and implementations for
different embedding models: CLIP, DINOv2, OpenAI Vision API.

Author: Enzo Cocca <enzo.ccc@gmail.com>
"""

import os
import sys
import json
import subprocess
import tempfile
from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np


class EmbeddingModel(ABC):
    """Abstract base class for embedding models"""

    @abstractmethod
    def get_embedding(self, image_path: str, search_type: str = 'general') -> Optional[np.ndarray]:
        """
        Generate embedding for a single image.

        Args:
            image_path: Path to the image file
            search_type: Type of search ('general', 'decoration', 'shape')

        Returns:
            numpy array of embeddings or None if failed
        """
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Return the embedding dimension for this model"""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return model identifier"""
        pass

    @property
    @abstractmethod
    def supported_search_types(self) -> List[str]:
        """Return list of supported search types"""
        pass

    def normalize_similarity(self, raw_score: float) -> float:
        """
        Normalize raw similarity score to 0-100% scale.
        Override in subclasses for model-specific normalization.
        """
        return max(0.0, min(100.0, raw_score * 100.0))


class CLIPEmbeddingModel(EmbeddingModel):
    """CLIP model via sentence-transformers (local, runs in subprocess)"""

    EMBEDDING_DIM = 512  # CLIP ViT-B/32

    def __init__(self, venv_python: str = None):
        self.venv_python = venv_python or self._find_venv_python()
        self._runner_script = self._get_runner_script_path()

    def _find_venv_python(self) -> str:
        """Find the pottery_venv Python executable"""
        venv_path = os.path.expanduser('~/pyarchinit/bin/pottery_venv/bin/python')
        if os.path.exists(venv_path):
            return venv_path
        # Fallback to system python
        return sys.executable

    def _get_runner_script_path(self) -> str:
        """Get path to the embedding runner script"""
        return os.path.expanduser('~/pyarchinit/bin/pottery_embedding_runner.py')

    @property
    def model_name(self) -> str:
        return 'clip'

    @property
    def supported_search_types(self) -> List[str]:
        return ['general', 'decoration', 'shape']

    def get_embedding_dimension(self) -> int:
        return self.EMBEDDING_DIM

    def get_embedding(self, image_path: str, search_type: str = 'general') -> Optional[np.ndarray]:
        """Generate CLIP embedding via subprocess"""
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            return None

        if not os.path.exists(self._runner_script):
            print(f"Embedding runner script not found: {self._runner_script}")
            return None

        try:
            # Create temp file for output
            with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as tmp:
                output_path = tmp.name

            cmd = [
                self.venv_python,
                self._runner_script,
                '--image', image_path,
                '--model', 'clip',
                '--search-type', search_type,
                '--output', output_path
            ]

            # Clean environment: remove QGIS Python paths that interfere with venv
            clean_env = os.environ.copy()
            clean_env.pop('PYTHONHOME', None)
            clean_env.pop('PYTHONPATH', None)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                env=clean_env
            )

            if result.returncode != 0:
                print(f"CLIP embedding failed: {result.stderr}")
                return None

            # Load embedding from temp file
            if os.path.exists(output_path):
                embedding = np.load(output_path)
                os.unlink(output_path)
                return embedding.astype(np.float32)

            return None

        except subprocess.TimeoutExpired:
            print("CLIP embedding timed out")
            return None
        except Exception as e:
            print(f"Error generating CLIP embedding: {e}")
            return None

    def normalize_similarity(self, raw_score: float) -> float:
        """CLIP similarity: map [0.5, 1.0] to [0, 100]"""
        return max(0.0, min(100.0, (raw_score - 0.5) * 200.0))


class DINOv2EmbeddingModel(EmbeddingModel):
    """DINOv2 (Meta) for self-supervised visual features (local, runs in subprocess)"""

    EMBEDDING_DIM = 768  # DINOv2 ViT-B/14

    def __init__(self, venv_python: str = None):
        self.venv_python = venv_python or self._find_venv_python()
        self._runner_script = self._get_runner_script_path()

    def _find_venv_python(self) -> str:
        """Find the pottery_venv Python executable"""
        venv_path = os.path.expanduser('~/pyarchinit/bin/pottery_venv/bin/python')
        if os.path.exists(venv_path):
            return venv_path
        return sys.executable

    def _get_runner_script_path(self) -> str:
        """Get path to the embedding runner script"""
        return os.path.expanduser('~/pyarchinit/bin/pottery_embedding_runner.py')

    @property
    def model_name(self) -> str:
        return 'dinov2'

    @property
    def supported_search_types(self) -> List[str]:
        return ['general', 'decoration', 'shape']

    def get_embedding_dimension(self) -> int:
        return self.EMBEDDING_DIM

    def get_embedding(self, image_path: str, search_type: str = 'general') -> Optional[np.ndarray]:
        """Generate DINOv2 embedding via subprocess"""
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            return None

        if not os.path.exists(self._runner_script):
            print(f"Embedding runner script not found: {self._runner_script}")
            return None

        try:
            with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as tmp:
                output_path = tmp.name

            cmd = [
                self.venv_python,
                self._runner_script,
                '--image', image_path,
                '--model', 'dinov2',
                '--search-type', search_type,
                '--output', output_path
            ]

            # Clean environment: remove QGIS Python paths that interfere with venv
            clean_env = os.environ.copy()
            clean_env.pop('PYTHONHOME', None)
            clean_env.pop('PYTHONPATH', None)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # DINOv2 may take longer
                env=clean_env
            )

            if result.returncode != 0:
                print(f"DINOv2 embedding failed: {result.stderr}")
                return None

            if os.path.exists(output_path):
                embedding = np.load(output_path)
                os.unlink(output_path)
                return embedding.astype(np.float32)

            return None

        except subprocess.TimeoutExpired:
            print("DINOv2 embedding timed out")
            return None
        except Exception as e:
            print(f"Error generating DINOv2 embedding: {e}")
            return None

    def normalize_similarity(self, raw_score: float) -> float:
        """DINOv2 similarity: map [0.4, 1.0] to [0, 100]"""
        return max(0.0, min(100.0, (raw_score - 0.4) * 166.67))


class OpenAIVisionEmbeddingModel(EmbeddingModel):
    """OpenAI Vision API for embeddings (cloud)"""

    EMBEDDING_DIM = 1536  # text-embedding-3-small

    def __init__(self, api_key: str = None):
        self.api_key = api_key or self._load_api_key()
        self._client = None

    def _load_api_key(self) -> Optional[str]:
        """Load API key from file"""
        key_path = os.path.expanduser('~/pyarchinit/bin/gpt_api_key.txt')
        if os.path.exists(key_path):
            with open(key_path, 'r') as f:
                return f.read().strip()
        return None

    def _get_client(self):
        """Lazy load OpenAI client"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("OpenAI library not installed")
                return None
        return self._client

    @property
    def model_name(self) -> str:
        return 'openai'

    @property
    def supported_search_types(self) -> List[str]:
        # OpenAI provides general embeddings only
        return ['general']

    def get_embedding_dimension(self) -> int:
        return self.EMBEDDING_DIM

    def get_embedding(self, image_path: str, search_type: str = 'general') -> Optional[np.ndarray]:
        """Generate embedding via OpenAI API using image description"""
        if not self.api_key:
            print("OpenAI API key not configured")
            return None

        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            return None

        client = self._get_client()
        if client is None:
            return None

        try:
            import base64

            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            # Determine mime type
            ext = os.path.splitext(image_path)[1].lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')

            # First, get image description using GPT-4 Vision
            description_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this pottery image in detail for similarity search. "
                                        "Focus on: shape, form, decoration patterns, surface treatment, "
                                        "color, and any distinctive features. Be concise but thorough."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )

            description = description_response.choices[0].message.content

            # Now generate embedding from description
            embedding_response = client.embeddings.create(
                model="text-embedding-3-small",
                input=description
            )

            embedding = np.array(embedding_response.data[0].embedding, dtype=np.float32)
            return embedding

        except Exception as e:
            print(f"Error generating OpenAI embedding: {e}")
            return None

    def normalize_similarity(self, raw_score: float) -> float:
        """OpenAI embeddings: map [0, 1] to [0, 100]"""
        return max(0.0, min(100.0, raw_score * 100.0))


def get_available_models() -> dict:
    """
    Return dictionary of available embedding models with their info.

    Returns:
        dict: {model_name: {'class': ModelClass, 'dim': int, 'search_types': list, 'local': bool}}
    """
    return {
        'clip': {
            'class': CLIPEmbeddingModel,
            'dim': CLIPEmbeddingModel.EMBEDDING_DIM,
            'search_types': ['general', 'decoration', 'shape'],
            'local': True,
            'description': 'CLIP (OpenAI) - Local, fast, general purpose'
        },
        'dinov2': {
            'class': DINOv2EmbeddingModel,
            'dim': DINOv2EmbeddingModel.EMBEDDING_DIM,
            'search_types': ['general', 'decoration', 'shape'],
            'local': True,
            'description': 'DINOv2 (Meta) - Local, excellent for visual details'
        },
        'openai': {
            'class': OpenAIVisionEmbeddingModel,
            'dim': OpenAIVisionEmbeddingModel.EMBEDDING_DIM,
            'search_types': ['general'],
            'local': False,
            'description': 'OpenAI Vision - Cloud, requires API key'
        }
    }


def get_model_instance(model_name: str, **kwargs) -> Optional[EmbeddingModel]:
    """
    Factory function to get an embedding model instance.

    Args:
        model_name: Name of the model ('clip', 'dinov2', 'openai')
        **kwargs: Additional arguments for the model constructor

    Returns:
        EmbeddingModel instance or None if model not found
    """
    models = get_available_models()
    if model_name not in models:
        print(f"Unknown model: {model_name}. Available: {list(models.keys())}")
        return None

    model_class = models[model_name]['class']
    return model_class(**kwargs)
