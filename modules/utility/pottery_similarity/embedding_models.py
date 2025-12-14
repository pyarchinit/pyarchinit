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
    def get_embedding(self, image_path: str, search_type: str = 'general',
                      auto_crop: bool = False, edge_preprocessing: bool = False) -> Optional[np.ndarray]:
        """
        Generate embedding for a single image.

        Args:
            image_path: Path to the image file
            search_type: Type of search ('general', 'decoration', 'shape')
            auto_crop: If True, auto-crop to region with most detail (for decoration)
            edge_preprocessing: If True, use edge-based preprocessing (better for textures)

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

    def get_embedding(self, image_path: str, search_type: str = 'general',
                      auto_crop: bool = False, edge_preprocessing: bool = False,
                      segment_decoration: bool = False, remove_background: bool = False,
                      custom_prompt: str = '') -> Optional[np.ndarray]:
        """Generate CLIP embedding via subprocess

        Args:
            image_path: Path to image file
            search_type: 'general', 'decoration', or 'shape'
            auto_crop: Crop to region with most detail
            edge_preprocessing: Use edge-based preprocessing for decoration
            segment_decoration: Mask non-decorated areas (isolate decoration only)
            remove_background: Remove photo background from pottery
            custom_prompt: Ignored for CLIP (only used by OpenAI)
        """
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

            # Add optional preprocessing flags
            if auto_crop:
                cmd.append('--auto-crop')
            if edge_preprocessing:
                cmd.extend(['--preprocessing', 'edge'])
            if segment_decoration:
                cmd.append('--segment-decoration')
            if remove_background:
                cmd.append('--remove-background')

            # Clean environment: remove QGIS Python paths that interfere with venv
            clean_env = os.environ.copy()
            for var in ['PYTHONHOME', 'PYTHONPATH', 'PYTHONEXECUTABLE']:
                clean_env.pop(var, None)

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

    def get_embedding(self, image_path: str, search_type: str = 'general',
                      auto_crop: bool = False, edge_preprocessing: bool = False,
                      segment_decoration: bool = False, remove_background: bool = False,
                      custom_prompt: str = '') -> Optional[np.ndarray]:
        """Generate DINOv2 embedding via subprocess

        Args:
            image_path: Path to image file
            search_type: 'general', 'decoration', or 'shape'
            auto_crop: Crop to region with most detail
            edge_preprocessing: Use edge-based preprocessing for decoration
            segment_decoration: Mask non-decorated areas (isolate decoration only)
            remove_background: Remove photo background from pottery
            custom_prompt: Ignored for DINOv2 (only used by OpenAI)
        """
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

            # Add optional preprocessing flags
            if auto_crop:
                cmd.append('--auto-crop')
            if edge_preprocessing:
                cmd.extend(['--preprocessing', 'edge'])
            if segment_decoration:
                cmd.append('--segment-decoration')
            if remove_background:
                cmd.append('--remove-background')

            # Clean environment: remove QGIS Python paths that interfere with venv
            clean_env = os.environ.copy()
            for var in ['PYTHONHOME', 'PYTHONPATH', 'PYTHONEXECUTABLE']:
                clean_env.pop(var, None)

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
    """OpenAI Vision API for embeddings (cloud) with specialized prompts"""

    EMBEDDING_DIM = 1536  # text-embedding-3-small

    # Specialized prompts for different search types
    PROMPTS = {
        'decoration': """Analyze ONLY the DECORATION of this pottery. Describe in detail:
1. Type of decorative motifs (geometric, figurative, abstract, naturalistic)
2. Specific patterns (bands, spirals, zigzags, crosshatch, chevrons, waves)
3. Decorative technique (painted, incised, impressed, stamped, relief, appliqué)
4. Position of decoration (rim, body, base, handles)
5. Color and pigments used in decoration
6. Style or cultural attribution if recognizable

DO NOT describe: overall shape, size, clay color, or non-decorated areas.
Focus EXCLUSIVELY on decorative elements.""",

        'shape': """Analyze ONLY the SHAPE and FORM of this pottery. Describe in detail:
1. Vessel type (bowl, jar, amphora, cup, plate, jug, etc.)
2. Overall profile (globular, cylindrical, conical, biconical, carinated)
3. Rim type (everted, inverted, straight, thickened, rolled)
4. Base type (flat, rounded, pointed, ring, pedestal)
5. Handles/attachments (vertical, horizontal, loop, lug, none)
6. Proportions (height vs width, neck vs body ratio)
7. Wall thickness and curvature

DO NOT describe: decoration, color, surface treatment, or painted elements.
Focus EXCLUSIVELY on morphological features.""",

        'general': """Describe this pottery for archaeological similarity search:
1. Vessel shape and type
2. Decoration patterns and techniques
3. Surface treatment (burnished, slipped, glazed, rough)
4. Fabric/clay characteristics visible
5. Any distinctive or diagnostic features
6. Possible cultural/chronological attribution

Be detailed but concise, focusing on features useful for finding similar pottery."""
    }

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
        # Now supports all search types with specialized prompts
        return ['general', 'decoration', 'shape']

    def get_embedding_dimension(self) -> int:
        return self.EMBEDDING_DIM

    def get_embedding(self, image_path: str, search_type: str = 'general',
                      auto_crop: bool = False, edge_preprocessing: bool = False,
                      segment_decoration: bool = False, remove_background: bool = False,
                      custom_prompt: str = '') -> Optional[np.ndarray]:
        """Generate embedding via OpenAI API using specialized prompts
        Note: auto_crop, edge_preprocessing, segment_decoration, remove_background are ignored
        for OpenAI (uses text description approach, not image preprocessing)

        Args:
            custom_prompt: If provided, uses this prompt instead of the search_type preset.
                          This allows semantic searches like "ceramica con decorazione a bande".
        """
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

            # Use custom prompt if provided, otherwise use search_type preset
            if custom_prompt:
                prompt = f"""Analizza questa ceramica e descrivi se e come corrisponde a questa richiesta:
"{custom_prompt}"

Descrivi in dettaglio le caratteristiche rilevanti per questa ricerca:
- Elementi che corrispondono alla richiesta
- Caratteristiche visive specifiche (decorazione, forma, texture, colore)
- Qualsiasi dettaglio distintivo

Sii dettagliato ma conciso."""
            else:
                prompt = self.PROMPTS.get(search_type, self.PROMPTS['general'])

            # Get image description using GPT-4 Vision with specialized prompt
            description_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
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
                max_tokens=400
            )

            description = description_response.choices[0].message.content

            # Generate embedding from description
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


class KhutmCLIPEmbeddingModel(EmbeddingModel):
    """
    KhutmML-CLIP: Fine-tuned CLIP model for archaeological pottery.

    This model uses a CLIP base with a fine-tuned projection layer
    trained specifically on pottery images from PyArchInit.
    """

    EMBEDDING_DIM = 512  # Same as CLIP
    MODEL_DIR = os.path.expanduser('~/pyarchinit/bin/models/khutm_clip')

    def __init__(self, venv_python: str = None, model_dir: str = None):
        self.venv_python = venv_python or self._find_venv_python()
        self.model_dir = model_dir or self.MODEL_DIR
        self._model_available = self._check_model_available()

        if self._model_available:
            print(f"[KhutmCLIP] Fine-tuned model found at {self.model_dir}")
        else:
            print(f"[KhutmCLIP] No fine-tuned model found. Train with khutm_clip_trainer.py")

    def _find_venv_python(self) -> str:
        """Find the pottery_venv Python executable"""
        venv_path = os.path.expanduser('~/pyarchinit/bin/pottery_venv/bin/python')
        if os.path.exists(venv_path):
            return venv_path
        return sys.executable

    def _check_model_available(self) -> bool:
        """Check if fine-tuned model is available"""
        proj_path = os.path.join(self.model_dir, 'khutm_clip_final_projection.pt')
        best_path = os.path.join(self.model_dir, 'best_model_projection.pt')
        return os.path.exists(proj_path) or os.path.exists(best_path)

    @property
    def model_name(self) -> str:
        return 'khutm_clip'

    @property
    def supported_search_types(self) -> List[str]:
        return ['general', 'decoration', 'shape']

    def get_embedding_dimension(self) -> int:
        return self.EMBEDDING_DIM

    def is_available(self) -> bool:
        """Check if the model is available for use"""
        return self._model_available

    def get_embedding(self, image_path: str, search_type: str = 'general',
                      auto_crop: bool = False, edge_preprocessing: bool = False,
                      segment_decoration: bool = False, remove_background: bool = False,
                      custom_prompt: str = '') -> Optional[np.ndarray]:
        """
        Generate embedding using KhutmML-CLIP fine-tuned model.

        Falls back to regular CLIP if fine-tuned model not available.
        """
        if not self._model_available:
            # Fall back to regular CLIP
            print("[KhutmCLIP] Fine-tuned model not available, using base CLIP")
            clip_model = CLIPEmbeddingModel(self.venv_python)
            return clip_model.get_embedding(
                image_path, search_type, auto_crop, edge_preprocessing,
                segment_decoration, remove_background, custom_prompt
            )

        # Use khutm_clip inference script
        runner_script = os.path.expanduser('~/pyarchinit/bin/khutm_clip_inference.py')

        # If inference script doesn't exist, fall back to creating embedding inline
        if not os.path.exists(runner_script):
            return self._generate_embedding_inline(
                image_path, search_type, auto_crop, edge_preprocessing,
                segment_decoration, remove_background
            )

        # Run inference via subprocess
        with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as tmp:
            output_path = tmp.name

        try:
            cmd = [
                self.venv_python, runner_script,
                '--image', image_path,
                '--model-dir', self.model_dir,
                '--search-type', search_type,
                '--output', output_path
            ]

            if auto_crop:
                cmd.append('--auto-crop')
            if edge_preprocessing:
                cmd.extend(['--preprocessing', 'edge'])
            if segment_decoration:
                cmd.append('--segment-decoration')
            if remove_background:
                cmd.append('--remove-background')

            # Clean environment to avoid QGIS Python interference
            clean_env = os.environ.copy()
            for var in ['PYTHONHOME', 'PYTHONPATH', 'PYTHONEXECUTABLE']:
                clean_env.pop(var, None)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                env=clean_env
            )

            if result.returncode == 0 and os.path.exists(output_path):
                embedding = np.load(output_path)
                return embedding.astype(np.float32)
            else:
                print(f"[KhutmCLIP] Error: {result.stderr}")
                # Fall back to inline generation
                return self._generate_embedding_inline(
                    image_path, search_type, auto_crop, edge_preprocessing,
                    segment_decoration, remove_background
                )

        except subprocess.TimeoutExpired:
            print("[KhutmCLIP] Timeout generating embedding")
            return None
        except Exception as e:
            print(f"[KhutmCLIP] Error: {e}")
            return None
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def _generate_embedding_inline(self, image_path: str, search_type: str,
                                    auto_crop: bool, edge_preprocessing: bool,
                                    segment_decoration: bool, remove_background: bool) -> Optional[np.ndarray]:
        """
        Generate embedding using inline Python (requires torch in current env).
        Falls back to CLIP if torch not available.
        """
        try:
            import torch
            import torch.nn.functional as F
            from sentence_transformers import SentenceTransformer
            from PIL import Image

            # Load base CLIP model
            device = 'cuda' if torch.cuda.is_available() else ('mps' if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() else 'cpu')
            clip_model = SentenceTransformer('clip-ViT-B-32', device=device)

            # Load projection layer
            proj_path = os.path.join(self.model_dir, 'khutm_clip_final_projection.pt')
            if not os.path.exists(proj_path):
                proj_path = os.path.join(self.model_dir, 'best_model_projection.pt')

            projection = torch.nn.Linear(512, 512).to(device)
            projection.load_state_dict(torch.load(proj_path, map_location=device))
            projection.eval()

            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')

            # Apply preprocessing based on search type
            # (simplified - full preprocessing in runner script)

            # Encode with CLIP
            with torch.no_grad():
                base_emb = clip_model.encode(image, convert_to_tensor=True)
                base_emb = base_emb.to(device)

                # Apply projection
                proj_emb = projection(base_emb.unsqueeze(0))
                proj_emb = F.normalize(proj_emb, p=2, dim=1)

            return proj_emb.squeeze().cpu().numpy().astype(np.float32)

        except ImportError:
            print("[KhutmCLIP] torch/sentence-transformers not available, using base CLIP")
            clip_model = CLIPEmbeddingModel(self.venv_python)
            return clip_model.get_embedding(
                image_path, search_type, auto_crop, edge_preprocessing,
                segment_decoration, remove_background
            )
        except Exception as e:
            print(f"[KhutmCLIP] Error in inline generation: {e}")
            return None

    def normalize_similarity(self, raw_score: float) -> float:
        """Same normalization as CLIP"""
        # KhutmCLIP typically produces higher similarity scores for pottery
        # Map [0.5, 1.0] to [0, 100] (pottery-optimized range)
        normalized = (raw_score - 0.5) * 200.0
        return max(0.0, min(100.0, normalized))


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
        },
        'khutm_clip': {
            'class': KhutmCLIPEmbeddingModel,
            'dim': KhutmCLIPEmbeddingModel.EMBEDDING_DIM,
            'search_types': ['general', 'decoration', 'shape'],
            'local': True,
            'description': 'KhutmML-CLIP - Fine-tuned for archaeological pottery',
            'requires_training': True
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
