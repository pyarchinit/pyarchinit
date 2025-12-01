"""
Storage Manager
===============

Central manager for storage backends with auto-detection.
Automatically selects the appropriate backend based on path prefix.

Path formats:
- Local: /path/to/files or C:\\path\\to\\files
- Google Drive: gdrive://folder/path
- Dropbox: dropbox://folder/path
- Amazon S3: s3://bucket/path
- Cloudflare R2: r2://bucket/path
- WebDAV: webdav://server/path or http(s)://server/webdav/path
- HTTP: http://server/path or https://server/path
- SFTP: sftp://server/path

Author: PyArchInit Team
License: GPL v2
"""

import os
import re
from typing import Dict, Optional, Type, Union
from urllib.parse import urlparse

from .base_backend import StorageBackend, StorageType, StorageConfig
from .local_backend import LocalBackend


class StorageManager:
    """
    Central manager for storage backends.

    Automatically detects and instantiates the appropriate storage backend
    based on the path prefix. Maintains a cache of backends for reuse.
    """

    # Mapping of URL schemes to storage types
    SCHEME_MAP = {
        'file': StorageType.LOCAL,
        'gdrive': StorageType.GOOGLE_DRIVE,
        'dropbox': StorageType.DROPBOX,
        's3': StorageType.S3,
        'r2': StorageType.R2,
        'webdav': StorageType.WEBDAV,
        'http': StorageType.HTTP,
        'https': StorageType.HTTP,
        'sftp': StorageType.SFTP,
    }

    # Registry of backend classes
    _backend_registry: Dict[StorageType, Type[StorageBackend]] = {}

    def __init__(self, credentials_manager=None):
        """
        Initialize the storage manager.

        Args:
            credentials_manager: Optional credentials manager for remote backends
        """
        self.credentials_manager = credentials_manager
        self._backend_cache: Dict[str, StorageBackend] = {}

        # Register default backends
        self._register_default_backends()

    def _register_default_backends(self):
        """Register the default backend implementations"""
        self.register_backend(StorageType.LOCAL, LocalBackend)

        # Remote backends are registered when their modules are imported
        # This allows for lazy loading and optional dependencies

    @classmethod
    def register_backend(cls, storage_type: StorageType, backend_class: Type[StorageBackend]):
        """
        Register a backend class for a storage type.

        Args:
            storage_type: The storage type to register
            backend_class: The backend class to use
        """
        cls._backend_registry[storage_type] = backend_class

    def detect_storage_type(self, path: str) -> StorageType:
        """
        Detect the storage type from a path.

        Args:
            path: The path or URL to analyze

        Returns:
            The detected StorageType
        """
        if not path:
            return StorageType.LOCAL

        # Check for URL scheme
        parsed = urlparse(path)

        if parsed.scheme and parsed.scheme.lower() in self.SCHEME_MAP:
            return self.SCHEME_MAP[parsed.scheme.lower()]

        # Check for Windows drive letter or Unix path
        if os.path.isabs(path) or path.startswith('/') or path.startswith('\\'):
            return StorageType.LOCAL

        # Check for Windows UNC path
        if path.startswith('\\\\'):
            return StorageType.LOCAL

        # Default to local if no scheme detected
        return StorageType.LOCAL

    def parse_path(self, path: str) -> tuple:
        """
        Parse a storage path into its components.

        Args:
            path: The path or URL to parse

        Returns:
            Tuple of (storage_type, base_path, relative_path)
        """
        storage_type = self.detect_storage_type(path)

        if storage_type == StorageType.LOCAL:
            # For local paths, normalize and return
            normalized = os.path.normpath(path)
            return storage_type, normalized, ""

        # Parse URL for remote backends
        parsed = urlparse(path)

        if storage_type in (StorageType.GOOGLE_DRIVE, StorageType.DROPBOX):
            # Format: gdrive://base_folder/subfolder/file
            base_path = parsed.netloc or ""
            relative_path = parsed.path.lstrip('/')
            return storage_type, base_path, relative_path

        if storage_type in (StorageType.S3, StorageType.R2):
            # Format: s3://bucket/key or r2://bucket/key
            bucket = parsed.netloc
            key = parsed.path.lstrip('/')
            return storage_type, bucket, key

        if storage_type == StorageType.WEBDAV:
            # Format: webdav://server/path
            base_url = f"https://{parsed.netloc}"
            relative_path = parsed.path.lstrip('/')
            return storage_type, base_url, relative_path

        if storage_type == StorageType.HTTP:
            # Format: http(s)://server/path
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            relative_path = parsed.path.lstrip('/')
            return storage_type, base_url, relative_path

        if storage_type == StorageType.SFTP:
            # Format: sftp://user@server/path
            server = parsed.netloc
            relative_path = parsed.path.lstrip('/')
            return storage_type, server, relative_path

        return storage_type, path, ""

    def get_backend(self, path: str, connect: bool = True) -> StorageBackend:
        """
        Get a storage backend for the given path.

        Automatically detects the storage type and returns the appropriate
        backend instance. Backends are cached for reuse.

        Args:
            path: The path or URL to get a backend for
            connect: Whether to connect the backend immediately

        Returns:
            A StorageBackend instance for the path

        Raises:
            ValueError: If no backend is registered for the storage type
        """
        storage_type, base_path, _ = self.parse_path(path)

        # Check cache
        cache_key = f"{storage_type.value}:{base_path}"
        if cache_key in self._backend_cache:
            backend = self._backend_cache[cache_key]
            if connect and not backend._connected:
                backend.connect()
            return backend

        # Get backend class
        if storage_type not in self._backend_registry:
            # Try to load the backend dynamically
            self._load_backend(storage_type)

        if storage_type not in self._backend_registry:
            raise ValueError(
                f"No backend registered for storage type: {storage_type.value}. "
                f"Available backends: {[t.value for t in self._backend_registry.keys()]}"
            )

        backend_class = self._backend_registry[storage_type]

        # Get credentials if available
        credentials = None
        if self.credentials_manager and storage_type != StorageType.LOCAL:
            credentials = self.credentials_manager.get_credentials(storage_type)

        # Create backend instance
        backend = backend_class(base_path, credentials)

        # Connect if requested
        if connect:
            backend.connect()

        # Cache the backend
        self._backend_cache[cache_key] = backend

        return backend

    def _load_backend(self, storage_type: StorageType):
        """
        Dynamically load a backend module.

        Args:
            storage_type: The storage type to load
        """
        try:
            if storage_type == StorageType.GOOGLE_DRIVE:
                from .gdrive_backend import GDriveBackend
                self.register_backend(StorageType.GOOGLE_DRIVE, GDriveBackend)

            elif storage_type == StorageType.DROPBOX:
                from .dropbox_backend import DropboxBackend
                self.register_backend(StorageType.DROPBOX, DropboxBackend)

            elif storage_type in (StorageType.S3, StorageType.R2):
                from .s3_backend import S3Backend
                self.register_backend(StorageType.S3, S3Backend)
                self.register_backend(StorageType.R2, S3Backend)

            elif storage_type == StorageType.WEBDAV:
                from .webdav_backend import WebDAVBackend
                self.register_backend(StorageType.WEBDAV, WebDAVBackend)

            elif storage_type == StorageType.HTTP:
                from .http_backend import HTTPBackend
                self.register_backend(StorageType.HTTP, HTTPBackend)

            elif storage_type == StorageType.SFTP:
                from .sftp_backend import SFTPBackend
                self.register_backend(StorageType.SFTP, SFTPBackend)

        except ImportError as e:
            # Backend not available (missing dependencies)
            pass

    def clear_cache(self):
        """Clear the backend cache and disconnect all backends"""
        for backend in self._backend_cache.values():
            try:
                backend.disconnect()
            except Exception:
                pass
        self._backend_cache.clear()

    def get_available_backends(self) -> list:
        """
        Get a list of available storage types.

        Returns:
            List of StorageType values that have registered backends
        """
        available = list(self._backend_registry.keys())

        # Try to load additional backends
        for storage_type in StorageType:
            if storage_type not in available:
                self._load_backend(storage_type)
                if storage_type in self._backend_registry:
                    available.append(storage_type)

        return available

    # Convenience methods that work directly with paths

    def read(self, path: str) -> Optional[bytes]:
        """
        Read a file from any storage.

        Args:
            path: Full path including storage prefix

        Returns:
            File contents as bytes, or None
        """
        storage_type, base_path, relative_path = self.parse_path(path)
        backend = self.get_backend(path)

        if storage_type == StorageType.LOCAL:
            # For local paths, use the path directly
            return backend.read(os.path.basename(path))
        else:
            return backend.read(relative_path)

    def write(self, path: str, data: Union[bytes, str]) -> bool:
        """
        Write data to any storage.

        Args:
            path: Full path including storage prefix
            data: Data to write (bytes or str)

        Returns:
            True if successful
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        storage_type, base_path, relative_path = self.parse_path(path)
        backend = self.get_backend(path)

        if storage_type == StorageType.LOCAL:
            return backend.write(os.path.basename(path), data)
        else:
            return backend.write(relative_path, data)

    def exists(self, path: str) -> bool:
        """
        Check if a file exists in any storage.

        Args:
            path: Full path including storage prefix

        Returns:
            True if file exists
        """
        storage_type, base_path, relative_path = self.parse_path(path)
        backend = self.get_backend(path)

        if storage_type == StorageType.LOCAL:
            return backend.exists(os.path.basename(path))
        else:
            return backend.exists(relative_path)

    def delete(self, path: str) -> bool:
        """
        Delete a file from any storage.

        Args:
            path: Full path including storage prefix

        Returns:
            True if deletion successful
        """
        storage_type, base_path, relative_path = self.parse_path(path)
        backend = self.get_backend(path)

        if storage_type == StorageType.LOCAL:
            return backend.delete(os.path.basename(path))
        else:
            return backend.delete(relative_path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear_cache()
        return False
