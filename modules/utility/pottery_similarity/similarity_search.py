"""
Pottery Similarity Search Engine

Main engine for visual similarity search of pottery images.
Coordinates embedding generation, index management, and search operations.

Author: Enzo Cocca <enzo.ccc@gmail.com>
"""

import os
import ast
from pathlib import Path
from typing import List, Dict, Optional, Callable
from datetime import datetime

try:
    from qgis.PyQt.QtCore import QThread, pyqtSignal
    HAS_QGIS = True
except ImportError:
    HAS_QGIS = False
    # Fallback for testing outside QGIS
    from threading import Thread
    QThread = Thread
    pyqtSignal = None

import numpy as np

from .embedding_models import (
    get_available_models,
    get_model_instance,
    EmbeddingModel
)
from .index_manager import PotterySimilarityIndexManager, compute_image_hash


def get_thumb_resize_path() -> Optional[str]:
    """
    Read THUMB_RESIZE path from pyarchinit config.cfg file.
    This is the base directory where resized images are stored.
    """
    config_path = Path.home() / 'pyarchinit' / 'pyarchinit_DB_folder' / 'config.cfg'
    if not config_path.exists():
        return None

    try:
        with open(config_path, 'r') as f:
            content = f.read().strip()
            config = ast.literal_eval(content)
            return config.get('THUMB_RESIZE', None)
    except Exception as e:
        print(f"Error reading config: {e}")
        return None


def build_full_image_path(relative_path: str, base_path: Optional[str] = None) -> str:
    """
    Build full image path from relative path_resize and config THUMB_RESIZE.

    Args:
        relative_path: Filename from media_thumb_table.path_resize
        base_path: Base directory (THUMB_RESIZE from config)

    Returns:
        Full absolute path to image file
    """
    if not relative_path:
        return ""

    if base_path is None:
        base_path = get_thumb_resize_path()

    if base_path is None:
        return relative_path  # Return as-is if no config

    return os.path.join(base_path, relative_path)


class PotterySimilaritySearchEngine:
    """
    Main search engine for pottery visual similarity.

    Coordinates:
    - Embedding model selection and generation
    - FAISS index management
    - Database metadata tracking
    - Search operations with threshold filtering
    """

    def __init__(self, db_manager=None):
        """
        Initialize the search engine.

        Args:
            db_manager: PyArchInit database manager instance
        """
        self.db_manager = db_manager
        self.index_manager = PotterySimilarityIndexManager(db_manager)
        self._models: Dict[str, EmbeddingModel] = {}  # Lazy-loaded models
        self._thumb_resize_path: Optional[str] = None  # Cached from config

    def _get_thumb_resize_path(self) -> Optional[str]:
        """Get cached THUMB_RESIZE path from config"""
        if self._thumb_resize_path is None:
            self._thumb_resize_path = get_thumb_resize_path()
        return self._thumb_resize_path

    def _build_image_path(self, relative_path: str) -> str:
        """Build full image path from relative path_resize"""
        return build_full_image_path(relative_path, self._get_thumb_resize_path())

    def _get_model(self, model_name: str) -> Optional[EmbeddingModel]:
        """Get or create embedding model instance"""
        if model_name not in self._models:
            model = get_model_instance(model_name)
            if model:
                self._models[model_name] = model
        return self._models.get(model_name)

    def search_similar(self,
                      query_image_path: str,
                      model_name: str = 'clip',
                      search_type: str = 'general',
                      threshold: float = 0.7,
                      auto_crop: bool = False,
                      edge_preprocessing: bool = False,
                      segment_decoration: bool = False,
                      remove_background: bool = False,
                      custom_prompt: str = '',
                      return_top_scores: bool = False):
        """
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
        """
        empty_result = ([], []) if return_top_scores else []

        if not os.path.exists(query_image_path):
            print(f"Query image not found: {query_image_path}")
            return empty_result

        # Get embedding model
        model = self._get_model(model_name)
        if model is None:
            print(f"Model not available: {model_name}")
            return empty_result

        # Check if search type is supported by model
        if search_type not in model.supported_search_types:
            print(f"Search type '{search_type}' not supported by {model_name}")
            search_type = 'general'

        # Generate query embedding with optional preprocessing
        query_embedding = model.get_embedding(
            query_image_path, search_type,
            auto_crop=auto_crop, edge_preprocessing=edge_preprocessing,
            segment_decoration=segment_decoration, remove_background=remove_background,
            custom_prompt=custom_prompt
        )
        if query_embedding is None:
            print("Failed to generate query embedding")
            return empty_result

        # Search index
        raw_results = self.index_manager.search(
            model_name, search_type,
            query_embedding, threshold
        )

        # Store embedding for top_scores calculation
        self._last_query_embedding = query_embedding

        # Enrich results with pottery data
        results = []
        for result in raw_results:
            enriched = {
                'pottery_id': result['pottery_id'],
                'media_id': result['media_id'],
                'similarity': result['similarity'],
                'similarity_percent': model.normalize_similarity(result['similarity'])
            }

            # Get image path (using media_id to get the SPECIFIC matched image) and pottery data from database
            if self.db_manager:
                try:
                    # Use media_id to get the exact image that matched, not just the first one
                    relative_path = self.db_manager.get_image_path_by_media_id(result['media_id'])
                    if relative_path:
                        # Build full path for local files, or cloudinary path
                        full_path = self._build_image_path(relative_path)
                        enriched['image_path'] = full_path
                        enriched['relative_path'] = relative_path  # Keep relative for Cloudinary

                    pottery = self.db_manager.get_pottery_by_id_rep(result['pottery_id'])
                    if pottery:
                        enriched['pottery_data'] = {
                            'id_number': getattr(pottery, 'id_number', ''),
                            'sito': getattr(pottery, 'sito', ''),
                            'area': getattr(pottery, 'area', ''),
                            'us': getattr(pottery, 'us', ''),
                            'anno': getattr(pottery, 'anno', ''),
                            'form': getattr(pottery, 'form', ''),
                            'specific_form': getattr(pottery, 'specific_form', ''),
                            'specific_shape': getattr(pottery, 'specific_shape', ''),
                            'ware': getattr(pottery, 'ware', ''),
                            'exdeco': getattr(pottery, 'exdeco', ''),
                            'intdeco': getattr(pottery, 'intdeco', ''),
                            'fabric': getattr(pottery, 'fabric', '')
                        }
                except Exception as e:
                    print(f"Error enriching result: {e}")

            results.append(enriched)

        if return_top_scores:
            # Get top 5 scores regardless of threshold for user feedback
            top_scores = self.index_manager.get_top_scores(model_name, search_type, query_embedding, 5)
            # Convert to percentages using model's normalization
            top_scores_percent = [model.normalize_similarity(s) for s in top_scores]
            print(f"[SEARCH_SIMILAR] Top 5 scores: {[f'{s:.1f}%' for s in top_scores_percent]}")
            return (results, top_scores_percent)

        return results

    def search_similar_by_pottery_id(self,
                                     pottery_id: int,
                                     model_name: str = 'clip',
                                     search_type: str = 'general',
                                     threshold: float = 0.7) -> List[Dict]:
        """
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
        """
        if not self.db_manager:
            print("Database manager required for this operation")
            return []

        # Get ALL images for this pottery
        all_images = self.db_manager.get_all_pottery_images(pottery_id)
        if not all_images:
            print(f"No images found for pottery {pottery_id}")
            return []


        # Search with each image and collect all results
        all_results = {}  # pottery_id -> best result

        for img_info in all_images:
            relative_path = img_info.get('path_resize')
            if not relative_path:
                continue

            # Build full path
            image_path = self._build_image_path(relative_path)
            if not os.path.exists(image_path):
                continue


            # Search
            results = self.search_similar(image_path, model_name, search_type, threshold)

            # Merge results, keeping the best similarity for each pottery
            for result in results:
                pid = result['pottery_id']
                if pid == pottery_id:
                    continue  # Skip self

                if pid not in all_results or result['similarity'] > all_results[pid]['similarity']:
                    all_results[pid] = result

        # Convert to list and sort by similarity
        final_results = list(all_results.values())
        final_results.sort(key=lambda x: x['similarity'], reverse=True)


        return final_results

    def search_by_text(self,
                      text_query: str,
                      model_name: str = 'openai',
                      search_type: str = 'general',
                      threshold: float = 0.7,
                      return_top_scores: bool = False):
        """
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
        """
        empty_result = ([], []) if return_top_scores else []

        if not text_query:
            print("Empty text query")
            return empty_result

        if model_name != 'openai':
            print("Text search only supported with OpenAI model")
            return empty_result

        # Get OpenAI model
        model = self._get_model('openai')
        if model is None:
            print("OpenAI model not available")
            return empty_result

        try:
            # Generate embedding directly from text using OpenAI
            from openai import OpenAI

            # Load API key
            api_key_path = os.path.expanduser("~/pyarchinit/bin/gpt_api_key.txt")
            if not os.path.exists(api_key_path):
                print(f"OpenAI API key not found at {api_key_path}")
                return empty_result

            with open(api_key_path, 'r') as f:
                api_key = f.read().strip()

            client = OpenAI(api_key=api_key)

            # Generate text embedding directly from the search query
            embedding_response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text_query
            )
            query_embedding = np.array(embedding_response.data[0].embedding, dtype=np.float32)

            print(f"[SEARCH_BY_TEXT] Generated embedding for: '{text_query[:50]}...'")
            print(f"[SEARCH_BY_TEXT] Embedding shape: {query_embedding.shape}")

        except Exception as e:
            print(f"Failed to generate text embedding: {e}")
            return empty_result

        # Search index with the text embedding
        print(f"[SEARCH_BY_TEXT] Searching index: model={model_name}, type={search_type}, threshold={threshold}")

        # Debug: check index status
        index, mapping = self.index_manager.get_index(model_name, search_type)
        if index is None:
            print(f"[SEARCH_BY_TEXT] ERROR: Index is None!")
        else:
            print(f"[SEARCH_BY_TEXT] Index has {index.ntotal} vectors, mapping has {len(mapping)} entries")

        raw_results = self.index_manager.search(
            model_name, search_type,
            query_embedding, threshold
        )
        print(f"[SEARCH_BY_TEXT] Raw results from index: {len(raw_results)}")

        # Enrich results with pottery data
        results = []
        for r in raw_results:
            pottery_id = r.get('pottery_id')
            media_id = r.get('media_id')

            result = {
                'pottery_id': pottery_id,
                'media_id': media_id,
                'similarity': r.get('similarity', 0),
                'similarity_percent': r.get('similarity', 0) * 100
            }

            # Get pottery data
            if self.db_manager and pottery_id:
                pottery_data = self.db_manager.get_pottery_data_by_id(pottery_id)
                if pottery_data:
                    result['pottery_data'] = pottery_data

            # Get image path
            if self.db_manager and media_id:
                image_info = self.db_manager.get_image_path_by_media_id(media_id)
                if image_info:
                    relative_path = image_info.get('path_resize')
                    if relative_path:
                        result['image_path'] = self._build_image_path(relative_path)
                        result['relative_path'] = relative_path

            results.append(result)

        print(f"[SEARCH_BY_TEXT] Found {len(results)} results above {threshold*100:.0f}% threshold")

        if return_top_scores:
            # Get top 5 scores regardless of threshold for user feedback
            top_scores = self.index_manager.get_top_scores(model_name, search_type, query_embedding, 5)
            # Convert to percentages
            top_scores_percent = [s * 100 for s in top_scores]
            print(f"[SEARCH_BY_TEXT] Top 5 scores: {[f'{s:.1f}%' for s in top_scores_percent]}")
            return (results, top_scores_percent)

        return results

    def build_index_for_model(self,
                              model_name: str,
                              search_type: str,
                              progress_callback: Optional[Callable[[int, int, str], None]] = None) -> bool:
        """
        Build/rebuild index for specific model and search type.

        Args:
            model_name: Embedding model to use
            search_type: Type of search
            progress_callback: Optional callback(current, total, message)

        Returns:
            True if successful
        """
        if not self.db_manager:
            print("Database manager required for index building")
            return False

        # Get model
        model = self._get_model(model_name)
        if model is None:
            return False

        # Get all pottery with images
        pottery_images = self.db_manager.get_all_pottery_with_images()
        total = len(pottery_images)

        if total == 0:
            if progress_callback:
                progress_callback(0, 0, "No pottery images found")
            return True

        embeddings = []
        errors = 0
        skipped_no_path = 0
        skipped_not_exists = 0

        # Log base path for debugging
        base_path = self._get_thumb_resize_path()

        for i, item in enumerate(pottery_images):
            if progress_callback:
                progress_callback(i, total, f"Processing {item.get('filename', 'image')}...")

            # filepath contains relative path_resize from media_thumb_table
            relative_path = item.get('filepath')
            if not relative_path:
                skipped_no_path += 1
                continue

            # Build full path using config THUMB_RESIZE
            image_path = self._build_image_path(relative_path)
            if not os.path.exists(image_path):
                skipped_not_exists += 1
                if skipped_not_exists <= 3:  # Log first few missing files
                continue

            # Generate embedding
            embedding = model.get_embedding(image_path, search_type)
            if embedding is not None:
                # Compute hash for incremental update support
                image_hash = compute_image_hash(image_path)
                embeddings.append((
                    embedding,
                    item.get('id_rep'),
                    item.get('id_media'),
                    image_hash
                ))
            else:
                errors += 1
                if errors <= 3:


        # Rebuild index with all embeddings
        success = self.index_manager.rebuild_index(model_name, search_type, embeddings)

        if success:
            self.index_manager.save_indexes()

        if progress_callback:
            msg = f"Completed: {len(embeddings)} indexed, {errors} errors"
            progress_callback(total, total, msg)

        return success

    def update_index_incremental(self,
                                 model_name: str,
                                 search_type: str,
                                 progress_callback: Optional[Callable[[int, int, str], None]] = None) -> Dict:
        """
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
        """
        result = {'added': 0, 'updated': 0, 'removed': 0}

        if not self.db_manager:
            return result

        model = self._get_model(model_name)
        if model is None:
            return result

        if progress_callback:
            progress_callback(0, 100, "Analyzing changes...")

        # Get current index state
        indexed_media_ids = self.index_manager.get_indexed_media_ids(model_name, search_type)
        indexed_hashes = self.index_manager.get_indexed_hashes(model_name, search_type)

        # Get all pottery images from DB
        db_images = self.db_manager.get_all_pottery_with_images()
        db_media_ids = {item['id_media'] for item in db_images}
        db_items_by_media = {item['id_media']: item for item in db_images}

        # Find what needs to be done
        new_media_ids = db_media_ids - indexed_media_ids
        deleted_media_ids = indexed_media_ids - db_media_ids
        potential_updated = indexed_media_ids & db_media_ids

        # Check for modified images (hash changed or file missing)
        modified_media_ids = set()
        for media_id in potential_updated:
            item = db_items_by_media.get(media_id)
            if not item:
                continue

            relative_path = item.get('filepath')
            if not relative_path:
                deleted_media_ids.add(media_id)
                continue

            image_path = self._build_image_path(relative_path)
            if not os.path.exists(image_path):
                # File deleted from disk
                deleted_media_ids.add(media_id)
                continue

            # Check hash
            old_hash = indexed_hashes.get(media_id)
            if old_hash:
                new_hash = compute_image_hash(image_path)
                if new_hash and new_hash != old_hash:
                    modified_media_ids.add(media_id)

        total_ops = len(new_media_ids) + len(modified_media_ids) + len(deleted_media_ids)

        if total_ops == 0:
            if progress_callback:
                progress_callback(100, 100, "Index is up to date")
            return result

        current_op = 0

        # Remove deleted
        if progress_callback:
            progress_callback(current_op, total_ops, f"Removing {len(deleted_media_ids)} deleted images...")

        for media_id in deleted_media_ids:
            if self.index_manager.remove_embedding(model_name, search_type, media_id):
                result['removed'] += 1
            current_op += 1

        # Update modified
        for media_id in modified_media_ids:
            if progress_callback:
                progress_callback(current_op, total_ops, f"Updating modified images... ({result['updated'] + 1})")

            item = db_items_by_media.get(media_id)
            if not item:
                continue

            relative_path = item.get('filepath')
            image_path = self._build_image_path(relative_path)

            embedding = model.get_embedding(image_path, search_type)
            if embedding is not None:
                image_hash = compute_image_hash(image_path)
                if self.index_manager.update_embedding(
                    model_name, search_type, embedding,
                    item['id_rep'], media_id, image_hash
                ):
                    result['updated'] += 1

            current_op += 1

        # Add new
        for media_id in new_media_ids:
            if progress_callback:
                progress_callback(current_op, total_ops, f"Adding new images... ({result['added'] + 1})")

            item = db_items_by_media.get(media_id)
            if not item:
                continue

            relative_path = item.get('filepath')
            if not relative_path:
                continue

            image_path = self._build_image_path(relative_path)
            if not os.path.exists(image_path):
                continue

            embedding = model.get_embedding(image_path, search_type)
            if embedding is not None:
                image_hash = compute_image_hash(image_path)
                if self.index_manager.add_embedding(
                    model_name, search_type, embedding,
                    item['id_rep'], media_id, image_hash
                ):
                    result['added'] += 1

            current_op += 1

        # Save updated index
        self.index_manager.save_indexes()

        if progress_callback:
            msg = f"Done: +{result['added']} added, ~{result['updated']} updated, -{result['removed']} removed"
            progress_callback(total_ops, total_ops, msg)

        return result

    def get_indexing_status(self) -> Dict:
        """
        Return status of all indexes.

        Returns:
            Dict with counts, status, and info for each model/search_type
        """
        status = {
            'indexes': self.index_manager.get_index_stats(),
            'models': get_available_models()
        }

        # Add database counts if available
        if self.db_manager:
            try:
                status['total_pottery_with_images'] = len(
                    self.db_manager.get_all_pottery_with_images()
                )
                status['embedding_counts'] = {}
                for model in ['clip', 'dinov2', 'openai']:
                    for search_type in ['general', 'decoration', 'shape']:
                        key = f"{model}_{search_type}"
                        status['embedding_counts'][key] = \
                            self.db_manager.count_pottery_embeddings(model, search_type)
            except Exception as e:
                print(f"Error getting database stats: {e}")

        return status


if HAS_QGIS:
    class PotterySimilarityWorker(QThread):
        """
        Background worker for similarity search and index building.

        Signals:
            search_complete: Emitted when search finishes with results list
            index_progress: Emitted during indexing (current, total, message)
            error_occurred: Emitted on error with message
            operation_complete: Emitted when any operation completes
        """

        search_complete = pyqtSignal(list)
        search_complete_with_meta = pyqtSignal(list, dict)  # results, metadata (top_scores, etc.)
        index_progress = pyqtSignal(int, int, str)
        error_occurred = pyqtSignal(str)
        operation_complete = pyqtSignal(str)

        def __init__(self, search_engine: PotterySimilaritySearchEngine,
                     operation: str, **kwargs):
            """
            Initialize worker.

            Args:
                search_engine: PotterySimilaritySearchEngine instance
                operation: Operation type ('search', 'search_by_id', 'build_index', 'update_index')
                **kwargs: Operation-specific arguments
            """
            super().__init__()
            self.search_engine = search_engine
            self.operation = operation
            self.kwargs = kwargs
            self.cancelled = False
            self.results = []

        def run(self):
            """Execute operation in background"""
            try:
                if self.operation == 'search':
                    search_result = self.search_engine.search_similar(
                        self.kwargs.get('image_path'),
                        self.kwargs.get('model_name', 'clip'),
                        self.kwargs.get('search_type', 'general'),
                        self.kwargs.get('threshold', 0.7),
                        auto_crop=self.kwargs.get('auto_crop', False),
                        edge_preprocessing=self.kwargs.get('edge_preprocessing', False),
                        segment_decoration=self.kwargs.get('segment_decoration', False),
                        remove_background=self.kwargs.get('remove_background', False),
                        custom_prompt=self.kwargs.get('custom_prompt', ''),
                        return_top_scores=True  # Get top scores for feedback
                    )
                    # search_result is now (results, top_scores)
                    if isinstance(search_result, tuple):
                        self.results, top_scores = search_result
                    else:
                        self.results = search_result
                        top_scores = []

                    # Filter out excluded pottery if specified
                    exclude_id = self.kwargs.get('exclude_pottery_id')
                    if exclude_id is not None:
                        self.results = [r for r in self.results if r.get('pottery_id') != exclude_id]

                    # Emit with metadata
                    meta = {'top_scores': top_scores, 'threshold': self.kwargs.get('threshold', 0.7)}
                    self.search_complete_with_meta.emit(self.results, meta)

                elif self.operation == 'search_by_id':
                    self.results = self.search_engine.search_similar_by_pottery_id(
                        self.kwargs.get('pottery_id'),
                        self.kwargs.get('model_name', 'clip'),
                        self.kwargs.get('search_type', 'general'),
                        self.kwargs.get('threshold', 0.7)
                    )
                    self.search_complete.emit(self.results)

                elif self.operation == 'search_by_text':
                    # Text-based semantic search (OpenAI only)
                    search_result = self.search_engine.search_by_text(
                        self.kwargs.get('custom_prompt', ''),
                        self.kwargs.get('model_name', 'openai'),
                        self.kwargs.get('search_type', 'general'),
                        self.kwargs.get('threshold', 0.7),
                        return_top_scores=True  # Get top scores for feedback
                    )
                    # search_result is now (results, top_scores)
                    if isinstance(search_result, tuple):
                        self.results, top_scores = search_result
                        meta = {'top_scores': top_scores, 'threshold': self.kwargs.get('threshold', 0.7)}
                        self.search_complete_with_meta.emit(self.results, meta)
                    else:
                        self.results = search_result
                        self.search_complete.emit(self.results)

                elif self.operation == 'build_index':
                    success = self.search_engine.build_index_for_model(
                        self.kwargs.get('model_name', 'clip'),
                        self.kwargs.get('search_type', 'general'),
                        progress_callback=self._progress_callback
                    )
                    if success:
                        self.operation_complete.emit("Index building completed")
                    else:
                        self.error_occurred.emit("Index building failed")

                elif self.operation == 'update_index':
                    result = self.search_engine.update_index_incremental(
                        self.kwargs.get('model_name', 'clip'),
                        self.kwargs.get('search_type', 'general'),
                        progress_callback=self._progress_callback
                    )
                    msg = f"+{result['added']} added, ~{result['updated']} updated, -{result['removed']} removed"
                    self.operation_complete.emit(msg)

                elif self.operation == 'update_all_indexes':
                    # Update all model/search_type combinations
                    models = self.kwargs.get('models', ['clip', 'dinov2', 'openai'])
                    search_types = self.kwargs.get('search_types', ['decoration', 'general', 'shape'])

                    total_results = {'added': 0, 'updated': 0, 'removed': 0}
                    total_combinations = len(models) * len(search_types)
                    current = 0

                    for model_name in models:
                        for search_type in search_types:
                            current += 1
                            self._progress_callback(
                                current, total_combinations,
                                f"Updating {model_name}/{search_type}..."
                            )

                            # Skip if index doesn't exist yet
                            indexed_count = self.search_engine.index_manager.get_index(model_name, search_type)[0]
                            if indexed_count is None or indexed_count.ntotal == 0:
                                continue

                            result = self.search_engine.update_index_incremental(
                                model_name, search_type,
                                progress_callback=None  # Don't emit progress for each sub-operation
                            )
                            total_results['added'] += result['added']
                            total_results['updated'] += result['updated']
                            total_results['removed'] += result['removed']

                    msg = f"All indexes: +{total_results['added']} added, ~{total_results['updated']} updated, -{total_results['removed']} removed"
                    self.operation_complete.emit(msg)

                else:
                    self.error_occurred.emit(f"Unknown operation: {self.operation}")

            except Exception as e:
                self.error_occurred.emit(str(e))

        def _progress_callback(self, current: int, total: int, message: str):
            """Emit progress signal"""
            if not self.cancelled:
                self.index_progress.emit(current, total, message)

        def cancel(self):
            """Cancel ongoing operation"""
            self.cancelled = True

else:
    # Fallback for non-QGIS environments
    class PotterySimilarityWorker:
        """Placeholder for non-QGIS environments"""

        def __init__(self, *args, **kwargs):
            raise RuntimeError("PotterySimilarityWorker requires QGIS/PyQt")
