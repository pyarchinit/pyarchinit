"""
FAISS Index Manager for Pottery Visual Similarity Search

Manages FAISS indexes for different embedding models and search types.
Handles index creation, persistence, and similarity search operations.

Author: Enzo Cocca <enzo.ccc@gmail.com>
"""

import os
import json
import pickle
import hashlib
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import numpy as np

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    print("FAISS not installed. Install with: pip install faiss-cpu")


class PotterySimilarityIndexManager:
    """
    Manages FAISS indexes for pottery similarity search.

    Each combination of (model_name, search_type) has its own index.
    Indexes are stored in ~/pyarchinit/bin/pottery_similarity/
    """

    INDEX_BASE_PATH = os.path.join(
        os.path.expanduser('~/pyarchinit'),
        'bin', 'pottery_similarity'
    )

    # Embedding dimensions for each model
    MODEL_DIMENSIONS = {
        'clip': 512,
        'dinov2': 768,
        'openai': 1536
    }

    def __init__(self, db_manager=None):
        """
        Initialize the index manager.

        Args:
            db_manager: Optional PyArchInit database manager for metadata operations
        """
        self.db_manager = db_manager
        self.indexes: Dict[str, faiss.Index] = {}  # Cache loaded indexes
        self.id_mappings: Dict[str, Dict] = {}  # FAISS index pos -> (pottery_id, media_id)
        self._modified_indexes = set()  # Track which indexes need saving

        # Ensure index directory exists
        os.makedirs(self.INDEX_BASE_PATH, exist_ok=True)

    def _get_index_key(self, model_name: str, search_type: str) -> str:
        """Generate unique key for model/search_type combination"""
        return f"{model_name}_{search_type}"

    def _get_index_paths(self, model_name: str, search_type: str) -> Tuple[str, str]:
        """Get paths for FAISS index and mapping pickle files"""
        key = self._get_index_key(model_name, search_type)
        index_path = os.path.join(self.INDEX_BASE_PATH, f"{key}.faiss")
        mapping_path = os.path.join(self.INDEX_BASE_PATH, f"{key}_mapping.pkl")
        return index_path, mapping_path

    def _get_dimension(self, model_name: str) -> int:
        """Get embedding dimension for model"""
        return self.MODEL_DIMENSIONS.get(model_name, 512)

    def _create_index(self, dimension: int) -> 'faiss.Index':
        """Create a new FAISS index"""
        if not HAS_FAISS:
            raise RuntimeError("FAISS not installed")

        # Use IndexFlatIP for cosine similarity (with normalized vectors)
        # Inner product on normalized vectors = cosine similarity
        index = faiss.IndexFlatIP(dimension)
        return index

    def get_index(self, model_name: str, search_type: str) -> Tuple[Optional['faiss.Index'], Dict]:
        """
        Load or create FAISS index for model/search_type combination.

        Args:
            model_name: Embedding model name ('clip', 'dinov2', 'openai')
            search_type: Search type ('general', 'decoration', 'shape')

        Returns:
            Tuple of (FAISS index, id_mapping dict)
        """
        if not HAS_FAISS:
            return None, {}

        key = self._get_index_key(model_name, search_type)

        # Return cached if available
        if key in self.indexes:
            return self.indexes[key], self.id_mappings.get(key, {})

        index_path, mapping_path = self._get_index_paths(model_name, search_type)

        # Try to load existing index
        if os.path.exists(index_path) and os.path.exists(mapping_path):
            try:
                index = faiss.read_index(index_path)
                with open(mapping_path, 'rb') as f:
                    mapping = pickle.load(f)
                self.indexes[key] = index
                self.id_mappings[key] = mapping
                return index, mapping
            except Exception as e:
                print(f"Error loading index {key}: {e}")

        # Create new index
        dimension = self._get_dimension(model_name)
        index = self._create_index(dimension)
        mapping = {}

        self.indexes[key] = index
        self.id_mappings[key] = mapping

        return index, mapping

    def add_embedding(self, model_name: str, search_type: str,
                     embedding: np.ndarray, pottery_id: int, media_id: int) -> bool:
        """
        Add embedding to appropriate index.

        Args:
            model_name: Embedding model name
            search_type: Search type
            embedding: Normalized embedding vector
            pottery_id: Pottery record ID (id_rep)
            media_id: Media file ID (id_media)

        Returns:
            True if successful
        """
        if not HAS_FAISS:
            return False

        index, mapping = self.get_index(model_name, search_type)
        if index is None:
            return False

        try:
            # Ensure embedding is 2D and float32
            if embedding.ndim == 1:
                embedding = embedding.reshape(1, -1)
            embedding = embedding.astype(np.float32)

            # Get current index position
            idx = index.ntotal

            # Add to FAISS index
            index.add(embedding)

            # Update mapping
            key = self._get_index_key(model_name, search_type)
            mapping[idx] = {'pottery_id': pottery_id, 'media_id': media_id}
            self.id_mappings[key] = mapping

            # Mark as modified
            self._modified_indexes.add(key)

            return True

        except Exception as e:
            print(f"Error adding embedding: {e}")
            return False

    def search(self, model_name: str, search_type: str,
              query_embedding: np.ndarray, threshold: float = 0.7,
              max_results: int = 1000) -> List[Dict]:
        """
        Search for similar images above threshold.

        Args:
            model_name: Embedding model name
            search_type: Search type
            query_embedding: Query embedding vector (normalized)
            threshold: Minimum similarity threshold (0-1)
            max_results: Maximum number of results to return

        Returns:
            List of dicts with pottery_id, media_id, similarity score
        """
        if not HAS_FAISS:
            return []

        index, mapping = self.get_index(model_name, search_type)
        if index is None or index.ntotal == 0:
            return []

        try:
            # Ensure query is 2D and float32
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)
            query_embedding = query_embedding.astype(np.float32)

            # Search ALL vectors in index
            k = min(max_results, index.ntotal)
            scores, indices = index.search(query_embedding, k)

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0:  # Invalid index
                    continue

                # FAISS returns inner product, which for normalized vectors = cosine similarity
                # Similarity should be in [0, 1] for normalized vectors
                similarity = float(score)

                if similarity >= threshold:
                    if idx in mapping:
                        info = mapping[idx]
                        results.append({
                            'pottery_id': info['pottery_id'],
                            'media_id': info['media_id'],
                            'similarity': similarity,
                            'faiss_idx': int(idx)
                        })

            # Sort by similarity descending
            results.sort(key=lambda x: x['similarity'], reverse=True)

            return results

        except Exception as e:
            print(f"Error searching index: {e}")
            return []

    def remove_embedding(self, model_name: str, search_type: str, media_id: int) -> bool:
        """
        Remove embedding from index by media_id.

        Note: FAISS doesn't support direct removal, so we mark it as invalid
        and rebuild periodically.

        Args:
            model_name: Embedding model name
            search_type: Search type
            media_id: Media file ID to remove

        Returns:
            True if found and marked for removal
        """
        key = self._get_index_key(model_name, search_type)
        mapping = self.id_mappings.get(key, {})

        # Find and mark for removal
        for idx, info in list(mapping.items()):
            if info.get('media_id') == media_id:
                mapping[idx]['removed'] = True
                self._modified_indexes.add(key)
                return True

        return False

    def rebuild_index(self, model_name: str, search_type: str,
                     embeddings: List[Tuple[np.ndarray, int, int]]) -> bool:
        """
        Rebuild entire index from scratch.

        Args:
            model_name: Embedding model name
            search_type: Search type
            embeddings: List of (embedding, pottery_id, media_id) tuples

        Returns:
            True if successful
        """
        if not HAS_FAISS:
            print("[DEBUG] rebuild_index: FAISS not available")
            return False

        print(f"[DEBUG] rebuild_index called with {len(embeddings)} embeddings")

        if not embeddings:
            print("[DEBUG] rebuild_index: No embeddings to index!")
            return True

        try:
            dimension = self._get_dimension(model_name)
            print(f"[DEBUG] Creating index with dimension {dimension}")
            index = self._create_index(dimension)
            mapping = {}

            for i, (embedding, pottery_id, media_id) in enumerate(embeddings):
                if embedding.ndim == 1:
                    embedding = embedding.reshape(1, -1)
                embedding = embedding.astype(np.float32)

                index.add(embedding)
                mapping[i] = {'pottery_id': pottery_id, 'media_id': media_id}

            key = self._get_index_key(model_name, search_type)
            self.indexes[key] = index
            self.id_mappings[key] = mapping
            self._modified_indexes.add(key)

            print(f"[DEBUG] rebuild_index complete: index.ntotal = {index.ntotal}, mapping size = {len(mapping)}")
            return True

        except Exception as e:
            print(f"Error rebuilding index: {e}")
            import traceback
            traceback.print_exc()
            return False

    def save_indexes(self) -> bool:
        """
        Persist all modified indexes to disk.

        Returns:
            True if all saves successful
        """
        if not HAS_FAISS:
            print("[DEBUG] save_indexes: FAISS not available")
            return False

        print(f"[DEBUG] save_indexes: {len(self._modified_indexes)} indexes to save")

        success = True
        for key in list(self._modified_indexes):  # Use list() to avoid modification during iteration
            if key in self.indexes:
                try:
                    parts = key.split('_')
                    model_name = parts[0]
                    search_type = '_'.join(parts[1:])

                    index_path, mapping_path = self._get_index_paths(model_name, search_type)

                    index = self.indexes[key]
                    mapping = self.id_mappings.get(key, {})

                    print(f"[DEBUG] Saving {key}: index.ntotal={index.ntotal}, mapping_len={len(mapping)}")
                    print(f"[DEBUG] Index path: {index_path}")

                    # Save FAISS index
                    faiss.write_index(index, index_path)

                    # Save mapping
                    with open(mapping_path, 'wb') as f:
                        pickle.dump(mapping, f)

                    print(f"[DEBUG] Saved {key} successfully")

                except Exception as e:
                    print(f"Error saving index {key}: {e}")
                    import traceback
                    traceback.print_exc()
                    success = False

        self._modified_indexes.clear()
        return success

    def get_index_stats(self) -> Dict:
        """
        Get statistics about all indexes.

        Returns:
            Dict with counts and info for each index
        """
        stats = {}

        for model in ['clip', 'dinov2', 'openai']:
            for search_type in ['general', 'decoration', 'shape']:
                key = self._get_index_key(model, search_type)
                index_path, mapping_path = self._get_index_paths(model, search_type)

                stat = {
                    'exists': os.path.exists(index_path),
                    'count': 0,
                    'dimension': self._get_dimension(model)
                }

                if key in self.indexes:
                    stat['count'] = self.indexes[key].ntotal
                    stat['loaded'] = True
                elif os.path.exists(index_path):
                    try:
                        index = faiss.read_index(index_path)
                        stat['count'] = index.ntotal
                        stat['loaded'] = False
                    except:
                        pass

                stats[key] = stat

        return stats

    def clear_index(self, model_name: str, search_type: str) -> bool:
        """
        Clear an index completely.

        Args:
            model_name: Embedding model name
            search_type: Search type

        Returns:
            True if successful
        """
        key = self._get_index_key(model_name, search_type)
        index_path, mapping_path = self._get_index_paths(model_name, search_type)

        # Remove from cache
        if key in self.indexes:
            del self.indexes[key]
        if key in self.id_mappings:
            del self.id_mappings[key]

        # Remove files
        try:
            if os.path.exists(index_path):
                os.remove(index_path)
            if os.path.exists(mapping_path):
                os.remove(mapping_path)
            return True
        except Exception as e:
            print(f"Error clearing index {key}: {e}")
            return False

    def clear_all_indexes(self) -> bool:
        """Clear all indexes"""
        success = True
        for model in ['clip', 'dinov2', 'openai']:
            for search_type in ['general', 'decoration', 'shape']:
                if not self.clear_index(model, search_type):
                    success = False
        return success


def compute_image_hash(image_path: str) -> Optional[str]:
    """
    Compute SHA256 hash of an image file for change detection.

    Args:
        image_path: Path to image file

    Returns:
        SHA256 hex string or None if error
    """
    try:
        sha256 = hashlib.sha256()
        with open(image_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"Error computing hash: {e}")
        return None
