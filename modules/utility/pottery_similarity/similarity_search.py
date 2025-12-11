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
                      threshold: float = 0.7) -> List[Dict]:
        """
        Find all images similar to query above threshold.

        Args:
            query_image_path: Path to query image
            model_name: Embedding model to use ('clip', 'dinov2', 'openai')
            search_type: Type of search ('general', 'decoration', 'shape')
            threshold: Minimum similarity (0-1)

        Returns:
            List of dicts with:
            - pottery_id: int
            - media_id: int
            - similarity: float (0-1)
            - similarity_percent: float (0-100)
            - image_path: str (if available)
            - pottery_data: dict (form, decoration, etc.)
        """
        if not os.path.exists(query_image_path):
            print(f"Query image not found: {query_image_path}")
            return []

        # Get embedding model
        model = self._get_model(model_name)
        if model is None:
            print(f"Model not available: {model_name}")
            return []

        # Check if search type is supported by model
        if search_type not in model.supported_search_types:
            print(f"Search type '{search_type}' not supported by {model_name}")
            search_type = 'general'

        # Generate query embedding
        query_embedding = model.get_embedding(query_image_path, search_type)
        if query_embedding is None:
            print("Failed to generate query embedding")
            return []

        # Search index
        raw_results = self.index_manager.search(
            model_name, search_type,
            query_embedding, threshold
        )

        # Enrich results with pottery data
        results = []
        for result in raw_results:
            enriched = {
                'pottery_id': result['pottery_id'],
                'media_id': result['media_id'],
                'similarity': result['similarity'],
                'similarity_percent': model.normalize_similarity(result['similarity'])
            }

            # Get image path and pottery data from database
            if self.db_manager:
                try:
                    image_path = self.db_manager.get_pottery_image_path(result['pottery_id'])
                    enriched['image_path'] = image_path

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

        return results

    def search_similar_by_pottery_id(self,
                                     pottery_id: int,
                                     model_name: str = 'clip',
                                     search_type: str = 'general',
                                     threshold: float = 0.7) -> List[Dict]:
        """
        Find similar pottery starting from existing record.

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

        # Get image path for pottery (relative from media_thumb_table.path_resize)
        relative_path = self.db_manager.get_pottery_image_path(pottery_id)
        if not relative_path:
            print(f"No image found for pottery {pottery_id}")
            return []

        # Build full path using config THUMB_RESIZE
        image_path = self._build_image_path(relative_path)
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return []

        # Search
        results = self.search_similar(image_path, model_name, search_type, threshold)

        # Exclude the query pottery from results
        results = [r for r in results if r['pottery_id'] != pottery_id]

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
        print(f"[DEBUG] THUMB_RESIZE base path: {base_path}")
        print(f"[DEBUG] Total pottery images from DB: {total}")

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
                    print(f"[DEBUG] File not found: {image_path}")
                continue

            # Generate embedding
            embedding = model.get_embedding(image_path, search_type)
            if embedding is not None:
                embeddings.append((
                    embedding,
                    item.get('id_rep'),
                    item.get('id_media')
                ))
            else:
                errors += 1
                if errors <= 3:
                    print(f"[DEBUG] Embedding generation failed for: {image_path}")

        print(f"[DEBUG] Build complete: {len(embeddings)} embeddings, {skipped_no_path} no path, {skipped_not_exists} not exists, {errors} errors")

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
                                 progress_callback: Optional[Callable[[int, int, str], None]] = None) -> int:
        """
        Update index with only new/changed images.

        Args:
            model_name: Embedding model
            search_type: Type of search
            progress_callback: Optional progress callback

        Returns:
            Number of images added
        """
        if not self.db_manager:
            return 0

        model = self._get_model(model_name)
        if model is None:
            return 0

        # Get unindexed images
        unindexed = self.db_manager.get_unindexed_pottery_images(model_name, search_type)
        total = len(unindexed)

        if total == 0:
            if progress_callback:
                progress_callback(0, 0, "Index is up to date")
            return 0

        added = 0
        for i, item in enumerate(unindexed):
            if progress_callback:
                progress_callback(i, total, f"Adding image {i+1}/{total}...")

            image_path = item.get('filepath')
            if not image_path or not os.path.exists(image_path):
                continue

            embedding = model.get_embedding(image_path, search_type)
            if embedding is not None:
                success = self.index_manager.add_embedding(
                    model_name, search_type,
                    embedding,
                    item.get('id_rep'),
                    item.get('id_media')
                )
                if success:
                    added += 1

                    # Save metadata
                    image_hash = compute_image_hash(image_path)
                    if image_hash:
                        metadata = self.db_manager.insert_pottery_embedding_metadata(
                            item.get('id_rep'),
                            item.get('id_media'),
                            image_hash,
                            model_name,
                            search_type
                        )
                        try:
                            session = self.db_manager.Session()
                            session.add(metadata)
                            session.commit()
                            session.close()
                        except Exception as e:
                            print(f"Error saving metadata: {e}")

        # Save updated index
        self.index_manager.save_indexes()

        if progress_callback:
            progress_callback(total, total, f"Added {added} images to index")

        return added

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
                    self.results = self.search_engine.search_similar(
                        self.kwargs.get('image_path'),
                        self.kwargs.get('model_name', 'clip'),
                        self.kwargs.get('search_type', 'general'),
                        self.kwargs.get('threshold', 0.7)
                    )
                    self.search_complete.emit(self.results)

                elif self.operation == 'search_by_id':
                    self.results = self.search_engine.search_similar_by_pottery_id(
                        self.kwargs.get('pottery_id'),
                        self.kwargs.get('model_name', 'clip'),
                        self.kwargs.get('search_type', 'general'),
                        self.kwargs.get('threshold', 0.7)
                    )
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
                    added = self.search_engine.update_index_incremental(
                        self.kwargs.get('model_name', 'clip'),
                        self.kwargs.get('search_type', 'general'),
                        progress_callback=self._progress_callback
                    )
                    self.operation_complete.emit(f"Added {added} images to index")

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
