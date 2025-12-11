"""
FAISS Index Manager for Pottery Visual Similarity Search

Manages FAISS indexes for different embedding models and search types.
Handles index creation, persistence, and similarity search operations.
Supports incremental updates (add/remove/update individual embeddings).

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

    Uses IndexIDMap to allow incremental updates (add/remove by media_id).
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
        self.id_mappings: Dict[str, Dict] = {}  # media_id -> {pottery_id, image_hash}
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
        """Create a new FAISS index with ID mapping for incremental updates"""
        if not HAS_FAISS:
            raise RuntimeError("FAISS not installed")

        # Use IndexIDMap wrapping IndexFlatIP for cosine similarity
        # IndexIDMap allows us to use media_id as the ID for each vector
        # This enables add/remove operations by ID
        base_index = faiss.IndexFlatIP(dimension)
        index = faiss.IndexIDMap(base_index)
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
                     embedding: np.ndarray, pottery_id: int, media_id: int,
                     image_hash: str = None) -> bool:
        """
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

            # Use media_id as the FAISS ID (allows removal/update by ID)
            ids = np.array([media_id], dtype=np.int64)

            # Add to FAISS index with ID
            index.add_with_ids(embedding, ids)

            # Update mapping: media_id -> {pottery_id, image_hash}
            key = self._get_index_key(model_name, search_type)
            mapping[media_id] = {
                'pottery_id': pottery_id,
                'media_id': media_id,
                'image_hash': image_hash
            }
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
                    # idx is the media_id (we use IndexIDMap with media_id as ID)
                    media_id = int(idx)
                    if media_id in mapping:
                        info = mapping[media_id]
                        results.append({
                            'pottery_id': info['pottery_id'],
                            'media_id': media_id,
                            'similarity': similarity,
                            'faiss_idx': media_id
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

        Uses IndexIDMap.remove_ids() for direct removal.

        Args:
            model_name: Embedding model name
            search_type: Search type
            media_id: Media file ID to remove

        Returns:
            True if successfully removed
        """
        if not HAS_FAISS:
            return False

        key = self._get_index_key(model_name, search_type)
        index, mapping = self.get_index(model_name, search_type)

        if index is None:
            return False

        try:
            # Remove from FAISS index using remove_ids
            ids_to_remove = np.array([media_id], dtype=np.int64)
            n_removed = index.remove_ids(ids_to_remove)

            # Remove from mapping
            if media_id in mapping:
                del mapping[media_id]
                self.id_mappings[key] = mapping

            if n_removed > 0:
                self._modified_indexes.add(key)
                return True

            return False

        except Exception as e:
            print(f"Error removing embedding: {e}")
            return False

    def rebuild_index(self, model_name: str, search_type: str,
                     embeddings: List[Tuple[np.ndarray, int, int, str]]) -> bool:
        """
        Rebuild entire index from scratch.

        Args:
            model_name: Embedding model name
            search_type: Search type
            embeddings: List of (embedding, pottery_id, media_id, image_hash) tuples
                       image_hash can be None

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

            for item in embeddings:
                # Handle both old format (3 items) and new format (4 items)
                if len(item) == 4:
                    embedding, pottery_id, media_id, image_hash = item
                else:
                    embedding, pottery_id, media_id = item
                    image_hash = None

                if embedding.ndim == 1:
                    embedding = embedding.reshape(1, -1)
                embedding = embedding.astype(np.float32)

                # Use media_id as the FAISS ID
                ids = np.array([media_id], dtype=np.int64)
                index.add_with_ids(embedding, ids)

                # Mapping: media_id -> {pottery_id, media_id, image_hash}
                mapping[media_id] = {
                    'pottery_id': pottery_id,
                    'media_id': media_id,
                    'image_hash': image_hash
                }

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

    def get_indexed_media_ids(self, model_name: str, search_type: str) -> set:
        """Get set of media_ids currently in the index"""
        key = self._get_index_key(model_name, search_type)
        _, mapping = self.get_index(model_name, search_type)
        return set(mapping.keys())

    def get_indexed_hashes(self, model_name: str, search_type: str) -> Dict[int, str]:
        """Get dict of media_id -> image_hash for all indexed images"""
        key = self._get_index_key(model_name, search_type)
        _, mapping = self.get_index(model_name, search_type)
        return {
            media_id: info.get('image_hash')
            for media_id, info in mapping.items()
            if info.get('image_hash')
        }

    def update_embedding(self, model_name: str, search_type: str,
                        embedding: np.ndarray, pottery_id: int, media_id: int,
                        image_hash: str = None) -> bool:
        """
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
        """
        # Remove old embedding
        self.remove_embedding(model_name, search_type, media_id)
        # Add new embedding
        return self.add_embedding(model_name, search_type, embedding, pottery_id, media_id, image_hash)


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
