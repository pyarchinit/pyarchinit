"""
Automatic Embedding Index Updater for Pottery Similarity Search

This module provides hooks for automatically updating FAISS indexes
when pottery images are added, updated, or deleted.

Author: Enzo Cocca <enzo.ccc@gmail.com>
"""

import os
from typing import Optional, List, Dict
from datetime import datetime

try:
    from qgis.PyQt.QtCore import QThread, pyqtSignal, QObject
    from qgis.PyQt.QtWidgets import QApplication
    HAS_QGIS = True
except ImportError:
    HAS_QGIS = False
    QObject = object
    QThread = None
    pyqtSignal = None

import numpy as np

from .embedding_models import get_model_instance
from .index_manager import PotterySimilarityIndexManager, compute_image_hash
from .similarity_search import get_thumb_resize_path, build_full_image_path


class EmbeddingIndexUpdater(QObject if HAS_QGIS else object):
    """
    Manages automatic updates to FAISS indexes when pottery images change.

    This class provides hooks that should be called when:
    - An image is added to a pottery record (on_image_added)
    - An image is removed from a pottery record (on_image_removed)
    - An image file is modified (on_image_modified)

    Updates are performed asynchronously in a background thread to avoid
    blocking the UI.
    """

    # Signals for progress/completion (only available in QGIS)
    if HAS_QGIS:
        embedding_added = pyqtSignal(int, int, str)  # pottery_id, media_id, model
        embedding_removed = pyqtSignal(int, int, str)  # pottery_id, media_id, model
        embedding_error = pyqtSignal(str)  # error message
        update_complete = pyqtSignal(str)  # completion message

    # Models to update (can be configured)
    DEFAULT_MODELS = ['clip']  # Only CLIP by default for speed
    DEFAULT_SEARCH_TYPES = ['general', 'decoration', 'shape']

    def __init__(self, db_manager=None, enabled: bool = True,
                 models: List[str] = None, search_types: List[str] = None):
        """
        Initialize the index updater.

        Args:
            db_manager: PyArchInit database manager
            enabled: Whether auto-update is enabled
            models: List of models to update ('clip', 'dinov2', 'openai')
            search_types: List of search types ('general', 'decoration', 'shape')
        """
        if HAS_QGIS:
            super().__init__()

        self.db_manager = db_manager
        self.enabled = enabled
        self.models = models or self.DEFAULT_MODELS
        self.search_types = search_types or self.DEFAULT_SEARCH_TYPES

        self._index_manager = None
        self._model_instances = {}
        self._thumb_resize_path = None
        self._pending_operations = []  # Queue for batch operations

    def _get_index_manager(self) -> PotterySimilarityIndexManager:
        """Lazy-load index manager"""
        if self._index_manager is None:
            self._index_manager = PotterySimilarityIndexManager(self.db_manager)
        return self._index_manager

    def _get_model(self, model_name: str):
        """Lazy-load embedding model"""
        if model_name not in self._model_instances:
            model = get_model_instance(model_name)
            if model:
                self._model_instances[model_name] = model
        return self._model_instances.get(model_name)

    def _get_thumb_resize_path(self) -> Optional[str]:
        """Get cached THUMB_RESIZE path"""
        if self._thumb_resize_path is None:
            self._thumb_resize_path = get_thumb_resize_path()
        return self._thumb_resize_path

    def _build_image_path(self, relative_path: str) -> str:
        """Build full image path from relative path"""
        return build_full_image_path(relative_path, self._get_thumb_resize_path())

    def set_enabled(self, enabled: bool):
        """Enable or disable automatic index updates"""
        self.enabled = enabled
        print(f"[EmbeddingIndexUpdater] Auto-update {'enabled' if enabled else 'disabled'}")

    def set_models(self, models: List[str]):
        """Set which models to update automatically"""
        self.models = models
        print(f"[EmbeddingIndexUpdater] Models set to: {models}")

    def on_image_added(self, pottery_id: int, media_id: int,
                       image_path: str = None, async_update: bool = True) -> bool:
        """
        Called when an image is linked to a pottery record.

        Args:
            pottery_id: The pottery record ID (id_rep)
            media_id: The media record ID (id_media)
            image_path: Optional full path to image (will be looked up if not provided)
            async_update: If True, update in background thread

        Returns:
            True if update was initiated/completed successfully
        """
        if not self.enabled:
            return True

        print(f"[EmbeddingIndexUpdater] Image added: pottery_id={pottery_id}, media_id={media_id}")

        # Get image path if not provided
        if image_path is None:
            image_path = self._resolve_image_path(media_id)

        if not image_path or not os.path.exists(image_path):
            print(f"[EmbeddingIndexUpdater] Image not found: {image_path}")
            return False

        if async_update and HAS_QGIS:
            # Queue for background processing
            self._pending_operations.append({
                'op': 'add',
                'pottery_id': pottery_id,
                'media_id': media_id,
                'image_path': image_path
            })
            self._process_pending_async()
        else:
            # Synchronous update
            return self._add_embedding_sync(pottery_id, media_id, image_path)

        return True

    def on_image_removed(self, pottery_id: int, media_id: int,
                         async_update: bool = True) -> bool:
        """
        Called when an image is unlinked from a pottery record.

        Args:
            pottery_id: The pottery record ID (id_rep)
            media_id: The media record ID (id_media)
            async_update: If True, update in background thread

        Returns:
            True if update was initiated/completed successfully
        """
        if not self.enabled:
            return True

        print(f"[EmbeddingIndexUpdater] Image removed: pottery_id={pottery_id}, media_id={media_id}")

        if async_update and HAS_QGIS:
            self._pending_operations.append({
                'op': 'remove',
                'pottery_id': pottery_id,
                'media_id': media_id
            })
            self._process_pending_async()
        else:
            return self._remove_embedding_sync(pottery_id, media_id)

        return True

    def on_image_modified(self, pottery_id: int, media_id: int,
                          image_path: str = None, async_update: bool = True) -> bool:
        """
        Called when an image file is modified (re-uploaded/replaced).

        Args:
            pottery_id: The pottery record ID (id_rep)
            media_id: The media record ID (id_media)
            image_path: Optional full path to image
            async_update: If True, update in background thread

        Returns:
            True if update was initiated/completed successfully
        """
        if not self.enabled:
            return True

        print(f"[EmbeddingIndexUpdater] Image modified: pottery_id={pottery_id}, media_id={media_id}")

        if image_path is None:
            image_path = self._resolve_image_path(media_id)

        if not image_path or not os.path.exists(image_path):
            print(f"[EmbeddingIndexUpdater] Image not found: {image_path}")
            return False

        if async_update and HAS_QGIS:
            self._pending_operations.append({
                'op': 'update',
                'pottery_id': pottery_id,
                'media_id': media_id,
                'image_path': image_path
            })
            self._process_pending_async()
        else:
            return self._update_embedding_sync(pottery_id, media_id, image_path)

        return True

    def _resolve_image_path(self, media_id: int) -> Optional[str]:
        """Resolve full image path from media_id using database"""
        if not self.db_manager:
            return None

        try:
            relative_path = self.db_manager.get_image_path_by_media_id(media_id)
            if relative_path:
                return self._build_image_path(relative_path)
        except Exception as e:
            print(f"[EmbeddingIndexUpdater] Error resolving image path: {e}")

        return None

    def _add_embedding_sync(self, pottery_id: int, media_id: int, image_path: str) -> bool:
        """Synchronously add embedding for an image"""
        success = True
        index_manager = self._get_index_manager()

        for model_name in self.models:
            model = self._get_model(model_name)
            if model is None:
                continue

            for search_type in self.search_types:
                try:
                    # Generate embedding
                    embedding = model.get_embedding(image_path, search_type)
                    if embedding is None:
                        print(f"[EmbeddingIndexUpdater] Failed to generate {model_name}/{search_type} embedding")
                        continue

                    # Compute image hash for change detection
                    image_hash = compute_image_hash(image_path)

                    # Add to index
                    if index_manager.add_embedding(
                        model_name, search_type, embedding,
                        pottery_id, media_id, image_hash
                    ):
                        print(f"[EmbeddingIndexUpdater] Added embedding: {model_name}/{search_type} for media {media_id}")
                        if HAS_QGIS:
                            self.embedding_added.emit(pottery_id, media_id, model_name)
                    else:
                        success = False

                except Exception as e:
                    print(f"[EmbeddingIndexUpdater] Error adding embedding: {e}")
                    if HAS_QGIS:
                        self.embedding_error.emit(str(e))
                    success = False

        # Save indexes
        index_manager.save_indexes()

        return success

    def _remove_embedding_sync(self, pottery_id: int, media_id: int) -> bool:
        """Synchronously remove embedding for an image"""
        success = True
        index_manager = self._get_index_manager()

        for model_name in self.models:
            for search_type in self.search_types:
                try:
                    if index_manager.remove_embedding(model_name, search_type, media_id):
                        print(f"[EmbeddingIndexUpdater] Removed embedding: {model_name}/{search_type} for media {media_id}")
                        if HAS_QGIS:
                            self.embedding_removed.emit(pottery_id, media_id, model_name)
                except Exception as e:
                    print(f"[EmbeddingIndexUpdater] Error removing embedding: {e}")
                    if HAS_QGIS:
                        self.embedding_error.emit(str(e))
                    success = False

        # Save indexes
        index_manager.save_indexes()

        return success

    def _update_embedding_sync(self, pottery_id: int, media_id: int, image_path: str) -> bool:
        """Synchronously update embedding for a modified image"""
        success = True
        index_manager = self._get_index_manager()

        for model_name in self.models:
            model = self._get_model(model_name)
            if model is None:
                continue

            for search_type in self.search_types:
                try:
                    # Generate new embedding
                    embedding = model.get_embedding(image_path, search_type)
                    if embedding is None:
                        continue

                    # Compute new hash
                    image_hash = compute_image_hash(image_path)

                    # Update in index (remove old, add new)
                    if index_manager.update_embedding(
                        model_name, search_type, embedding,
                        pottery_id, media_id, image_hash
                    ):
                        print(f"[EmbeddingIndexUpdater] Updated embedding: {model_name}/{search_type} for media {media_id}")
                    else:
                        success = False

                except Exception as e:
                    print(f"[EmbeddingIndexUpdater] Error updating embedding: {e}")
                    success = False

        # Save indexes
        index_manager.save_indexes()

        return success

    def _process_pending_async(self):
        """Process pending operations in background thread"""
        if not HAS_QGIS or not self._pending_operations:
            return

        # Process one operation at a time to avoid overwhelming the system
        if hasattr(self, '_worker') and self._worker is not None and self._worker.isRunning():
            return  # Already processing

        operation = self._pending_operations.pop(0)

        self._worker = EmbeddingUpdateWorker(self, operation)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.start()

    def _on_worker_finished(self):
        """Called when background worker finishes"""
        # Process next pending operation
        if self._pending_operations:
            self._process_pending_async()
        else:
            if HAS_QGIS:
                self.update_complete.emit("Index update complete")

    def get_status(self) -> Dict:
        """Get current status of the updater"""
        return {
            'enabled': self.enabled,
            'models': self.models,
            'search_types': self.search_types,
            'pending_operations': len(self._pending_operations)
        }


if HAS_QGIS:
    class EmbeddingUpdateWorker(QThread):
        """Background worker for embedding updates"""

        def __init__(self, updater: EmbeddingIndexUpdater, operation: Dict):
            super().__init__()
            self.updater = updater
            self.operation = operation

        def run(self):
            """Execute the update operation"""
            op = self.operation.get('op')
            pottery_id = self.operation.get('pottery_id')
            media_id = self.operation.get('media_id')
            image_path = self.operation.get('image_path')

            try:
                if op == 'add':
                    self.updater._add_embedding_sync(pottery_id, media_id, image_path)
                elif op == 'remove':
                    self.updater._remove_embedding_sync(pottery_id, media_id)
                elif op == 'update':
                    self.updater._update_embedding_sync(pottery_id, media_id, image_path)
            except Exception as e:
                print(f"[EmbeddingUpdateWorker] Error: {e}")


# Singleton instance for easy access
_updater_instance: Optional[EmbeddingIndexUpdater] = None


def get_embedding_updater(db_manager=None) -> EmbeddingIndexUpdater:
    """
    Get the singleton EmbeddingIndexUpdater instance.

    Args:
        db_manager: PyArchInit database manager (only needed on first call)

    Returns:
        EmbeddingIndexUpdater instance
    """
    global _updater_instance

    if _updater_instance is None:
        _updater_instance = EmbeddingIndexUpdater(db_manager)
    elif db_manager is not None and _updater_instance.db_manager is None:
        _updater_instance.db_manager = db_manager

    return _updater_instance


def set_auto_update_enabled(enabled: bool):
    """Enable or disable automatic index updates globally"""
    updater = get_embedding_updater()
    updater.set_enabled(enabled)


def set_auto_update_models(models: List[str]):
    """Set which models to update automatically"""
    updater = get_embedding_updater()
    updater.set_models(models)
