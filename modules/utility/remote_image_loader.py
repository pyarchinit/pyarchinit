"""
Remote Image Loader
===================

Utility for loading images from remote URLs into QIcon/QPixmap.
Supports local paths, HTTP/HTTPS URLs, and Cloudinary paths.

Uses the storage backend system for proper authentication (API keys, etc.)

Author: PyArchInit Team
License: GPL v2
"""

import os
import tempfile
from typing import Optional, Dict, Tuple
from urllib.parse import urlparse

from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtCore import QByteArray, QBuffer


# Cloudinary configuration
CLOUDINARY_CLOUD_NAME = "dkioeufik"
CLOUDINARY_BASE_URL = f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/upload"


class RemoteImageLoader:
    """
    Loads images from local paths or remote URLs.

    Caches downloaded images in memory to avoid repeated downloads.
    Uses the storage module for authenticated requests.
    """

    # In-memory cache for downloaded images: path -> QPixmap
    _cache: Dict[str, QPixmap] = {}

    # Maximum cache size (number of images)
    MAX_CACHE_SIZE = 100

    # Storage backend instance (shared)
    _storage_backend = None
    _storage_credentials = None

    @classmethod
    def set_storage_credentials(cls, credentials: dict):
        """
        Set credentials for HTTP storage backend.

        Args:
            credentials: Dict with 'api_key', 'username', 'password', etc.
        """
        cls._storage_credentials = credentials
        cls._storage_backend = None  # Reset backend to use new credentials

    @classmethod
    def _get_storage_backend(cls, base_url: str):
        """Get or create HTTP storage backend for the URL."""
        if cls._storage_backend is None:
            try:
                from ..storage.http_backend import HTTPBackend

                credentials = cls._storage_credentials or {}
                cls._storage_backend = HTTPBackend(base_url, credentials)
                cls._storage_backend.connect()
            except ImportError:
                cls._storage_backend = None

        return cls._storage_backend

    @classmethod
    def is_remote_url(cls, path: str) -> bool:
        """
        Check if a path is a remote URL (HTTP, HTTPS, or Cloudinary).

        Args:
            path: File path or URL

        Returns:
            True if path is a remote URL
        """
        if not path:
            return False
        return path.lower().startswith(('http://', 'https://', 'cloudinary://'))

    @classmethod
    def is_cloudinary_path(cls, path: str) -> bool:
        """
        Check if a path is a Cloudinary path.

        Args:
            path: File path or URL

        Returns:
            True if path starts with cloudinary://
        """
        if not path:
            return False
        return path.lower().startswith('cloudinary://')

    @classmethod
    def cloudinary_to_url(cls, cloudinary_path: str) -> str:
        """
        Convert a cloudinary:// path to a full HTTPS URL.

        Format: cloudinary://folder/subfolder/filename
        Result: https://res.cloudinary.com/{cloud_name}/image/upload/folder/subfolder/filename

        Args:
            cloudinary_path: Path starting with cloudinary://

        Returns:
            Full HTTPS URL to the image on Cloudinary
        """
        if not cloudinary_path or not cls.is_cloudinary_path(cloudinary_path):
            return cloudinary_path

        # Remove cloudinary:// prefix
        path_part = cloudinary_path[len('cloudinary://'):]

        # Clean up path
        path_part = path_part.strip('/')

        # Build full URL
        return f"{CLOUDINARY_BASE_URL}/{path_part}"

    @classmethod
    def clear_cache(cls):
        """Clear the image cache."""
        cls._cache.clear()

    @classmethod
    def _download_image(cls, url: str) -> Optional[bytes]:
        """
        Download an image from a URL.

        Args:
            url: Image URL

        Returns:
            Image data as bytes, or None if download failed
        """
        # Try using storage backend first (has authentication support)
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}/"

            backend = cls._get_storage_backend(base_url)
            if backend:
                # Extract path from URL
                file_path = parsed.path.lstrip('/')
                data = backend.read(file_path)
                if data:
                    return data
        except Exception:
            pass

        # Fallback to direct requests
        try:
            import requests

            headers = {}
            if cls._storage_credentials:
                api_key = cls._storage_credentials.get('api_key')
                if api_key:
                    headers['X-API-Key'] = api_key

            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.content
        except Exception:
            pass

        return None

    @classmethod
    def load_pixmap(cls, path: str) -> QPixmap:
        """
        Load an image as QPixmap from local path, remote URL, or Cloudinary path.

        Args:
            path: Local file path, HTTP/HTTPS URL, or cloudinary:// path

        Returns:
            QPixmap (may be null if loading failed)
        """
        if not path:
            return QPixmap()

        # Check cache first
        if path in cls._cache:
            return cls._cache[path]

        pixmap = QPixmap()

        # Convert cloudinary:// to HTTPS URL
        download_url = path
        if cls.is_cloudinary_path(path):
            download_url = cls.cloudinary_to_url(path)

        if cls.is_remote_url(path):
            # Download from URL (cloudinary paths are converted to HTTPS)
            data = cls._download_image(download_url)
            if data:
                pixmap.loadFromData(QByteArray(data))
        else:
            # Load from local path
            if os.path.exists(path):
                pixmap.load(path)

        # Add to cache if loaded successfully
        if not pixmap.isNull():
            # Manage cache size
            if len(cls._cache) >= cls.MAX_CACHE_SIZE:
                # Remove oldest entries (first 20%)
                keys_to_remove = list(cls._cache.keys())[:cls.MAX_CACHE_SIZE // 5]
                for key in keys_to_remove:
                    del cls._cache[key]

            cls._cache[path] = pixmap

        return pixmap

    @classmethod
    def load_icon(cls, path: str) -> QIcon:
        """
        Load an image as QIcon from local path or remote URL.

        Args:
            path: Local file path or remote URL

        Returns:
            QIcon (may be null if loading failed)
        """
        if not path:
            return QIcon()

        # For local paths, QIcon can load directly (more efficient)
        if not cls.is_remote_url(path):
            if os.path.exists(path):
                return QIcon(path)
            return QIcon()

        # For remote URLs, load as pixmap first
        pixmap = cls.load_pixmap(path)
        if not pixmap.isNull():
            return QIcon(pixmap)

        return QIcon()

    @classmethod
    def load_icon_with_fallback(cls, path: str, fallback_icon: str = None) -> QIcon:
        """
        Load an icon with a fallback if loading fails.

        Args:
            path: Local file path or remote URL
            fallback_icon: Path to fallback icon (optional)

        Returns:
            QIcon
        """
        icon = cls.load_icon(path)

        if icon.isNull() and fallback_icon:
            return QIcon(fallback_icon)

        return icon

    @classmethod
    def get_image_path(cls, base_path: str, filename: str) -> str:
        """
        Construct full image path, handling local, HTTP, and Cloudinary paths.

        Args:
            base_path: Base directory path, URL, or cloudinary:// path
            filename: Filename to append

        Returns:
            Full path or URL
        """
        if not base_path or not filename:
            return ""

        # Clean up paths
        base_path = base_path.rstrip('/\\')
        filename = filename.lstrip('/\\')

        if cls.is_cloudinary_path(base_path) or cls.is_remote_url(base_path):
            # URL or Cloudinary path - use forward slash
            return f"{base_path}/{filename}"
        else:
            # Local path - use os.path.join
            return os.path.join(base_path, filename)


# Convenience functions for easy import
def load_icon(path: str) -> QIcon:
    """Load icon from local path or remote URL."""
    return RemoteImageLoader.load_icon(path)


def load_pixmap(path: str) -> QPixmap:
    """Load pixmap from local path or remote URL."""
    return RemoteImageLoader.load_pixmap(path)


def is_remote_url(path: str) -> bool:
    """Check if path is a remote URL (HTTP, HTTPS, or Cloudinary)."""
    return RemoteImageLoader.is_remote_url(path)


def is_cloudinary_path(path: str) -> bool:
    """Check if path is a Cloudinary path."""
    return RemoteImageLoader.is_cloudinary_path(path)


def cloudinary_to_url(cloudinary_path: str) -> str:
    """Convert cloudinary:// path to HTTPS URL."""
    return RemoteImageLoader.cloudinary_to_url(cloudinary_path)


def get_image_path(base_path: str, filename: str) -> str:
    """Construct full image path."""
    return RemoteImageLoader.get_image_path(base_path, filename)


def set_storage_credentials(credentials: dict):
    """Set credentials for remote storage access."""
    RemoteImageLoader.set_storage_credentials(credentials)


def load_credentials_from_qgis():
    """
    Load storage credentials from QGIS settings.

    Call this function once when the plugin initializes to enable
    authenticated access to remote storage.
    """
    try:
        from qgis.core import QgsSettings
        settings = QgsSettings()

        credentials = {}

        # Load HTTP storage credentials
        api_key = settings.value("pyarchinit/storage/http/api_key", "")
        username = settings.value("pyarchinit/storage/http/username", "")
        password = settings.value("pyarchinit/storage/http/password", "")
        bearer_token = settings.value("pyarchinit/storage/http/bearer_token", "")

        if api_key:
            credentials['api_key'] = api_key
        if username:
            credentials['username'] = username
        if password:
            credentials['password'] = password
        if bearer_token:
            credentials['bearer_token'] = bearer_token

        if credentials:
            RemoteImageLoader.set_storage_credentials(credentials)
            return True

        return False
    except ImportError:
        return False


def initialize():
    """
    Initialize the remote image loader with credentials from QGIS settings.

    This should be called once when the plugin loads.
    """
    load_credentials_from_qgis()
