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

    # Unibo backend instance (shared)
    _unibo_backend = None
    _unibo_credentials = None

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
    def set_unibo_credentials(cls, credentials: dict):
        """
        Set credentials for Unibo File Manager backend.

        Args:
            credentials: Dict with 'server_url', 'username', 'password'
        """
        cls._unibo_credentials = credentials
        cls._unibo_backend = None  # Reset backend to use new credentials

    # Cache for Unibo backends by project code
    _unibo_backends: Dict[str, object] = {}

    @classmethod
    def _get_unibo_backend(cls, project_code: str):
        """Get or create Unibo File Manager backend for a project."""
        if not cls._unibo_credentials:
            return None

        # Check if we have a cached backend for this project
        if project_code in cls._unibo_backends:
            return cls._unibo_backends[project_code]

        try:
            from ..storage.unibo_filemanager_backend import UniboFileManagerBackend

            # Create backend with just project code (no folder path)
            # This allows us to access any folder in the project via read()
            backend = UniboFileManagerBackend(
                base_path=project_code,
                credentials=cls._unibo_credentials
            )
            if backend.connect():
                cls._unibo_backends[project_code] = backend
                return backend
            else:
                return None
        except ImportError:
            return None
        except Exception:
            return None

    @classmethod
    def _download_from_unibo(cls, unibo_path: str) -> Optional[bytes]:
        """
        Download an image from Unibo File Manager.

        Args:
            unibo_path: Path starting with unibo://

        Returns:
            Image data as bytes, or None if download failed
        """
        if not unibo_path or not cls.is_unibo_path(unibo_path):
            return None

        # Parse unibo:// path
        # Format: unibo://project_code/folder/path/filename.ext
        path_part = unibo_path[len('unibo://'):].strip('/')
        parts = path_part.split('/')

        if len(parts) < 2:
            return None

        # Extract project code and the remaining path (folder + filename)
        project_code = parts[0]
        remaining_path = '/'.join(parts[1:])  # e.g., "KTM2025/photolog/original/image.png"

        try:
            # Try loading credentials if not set
            if not cls._unibo_credentials:
                load_unibo_credentials_from_qgis()

            if not cls._unibo_credentials:
                return None

            # Get or create backend for this project
            backend = cls._get_unibo_backend(project_code)

            if backend is None:
                return None

            # Pass the full remaining path to read()
            # The backend's read() method will resolve folders and find the file
            data = backend.read(remaining_path)
            return data

        except Exception:
            return None

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
        Check if a path is a remote URL (HTTP, HTTPS, Cloudinary, or Unibo).

        Args:
            path: File path or URL

        Returns:
            True if path is a remote URL
        """
        if not path:
            return False
        return path.lower().startswith(('http://', 'https://', 'cloudinary://', 'unibo://'))

    @classmethod
    def is_unibo_path(cls, path: str) -> bool:
        """
        Check if a path is a Unibo File Manager path.

        Args:
            path: File path or URL

        Returns:
            True if path starts with unibo://
        """
        if not path:
            return False
        return path.lower().startswith('unibo://')

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

        Note: Removes '_thumb' from filename as Cloudinary stores files without this suffix.

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

        # Remove '_thumb' from filename (Cloudinary files don't have this suffix)
        # Example: 2446_DSC02076_thumb.png -> 2446_DSC02076.png
        import re
        path_part = re.sub(r'_thumb(\.[^.]+)$', r'\1', path_part)

        # Build full URL
        full_url = f"{CLOUDINARY_BASE_URL}/{path_part}"

        return full_url

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
        Load an image as QPixmap from local path, remote URL, Cloudinary, or Unibo path.

        Args:
            path: Local file path, HTTP/HTTPS URL, cloudinary://, or unibo:// path

        Returns:
            QPixmap (may be null if loading failed)
        """
        if not path:
            return QPixmap()

        # Check cache first
        if path in cls._cache:
            return cls._cache[path]

        pixmap = QPixmap()
        data = None

        # Handle different path types
        if cls.is_unibo_path(path):
            # Download from Unibo File Manager
            data = cls._download_from_unibo(path)
        elif cls.is_cloudinary_path(path):
            # Convert cloudinary:// to HTTPS URL and download
            download_url = cls.cloudinary_to_url(path)
            data = cls._download_image(download_url)
        elif cls.is_remote_url(path):
            # Download from HTTP/HTTPS URL
            data = cls._download_image(path)

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


def is_unibo_path(path: str) -> bool:
    """Check if path is a Unibo File Manager path."""
    return RemoteImageLoader.is_unibo_path(path)


def cloudinary_to_url(cloudinary_path: str) -> str:
    """Convert cloudinary:// path to HTTPS URL."""
    return RemoteImageLoader.cloudinary_to_url(cloudinary_path)


def get_image_path(base_path: str, filename: str) -> str:
    """Construct full image path."""
    return RemoteImageLoader.get_image_path(base_path, filename)


def set_storage_credentials(credentials: dict):
    """Set credentials for remote storage access."""
    RemoteImageLoader.set_storage_credentials(credentials)


def set_unibo_credentials(credentials: dict):
    """Set credentials for Unibo File Manager access."""
    RemoteImageLoader.set_unibo_credentials(credentials)


def load_unibo_credentials_from_qgis():
    """
    Load Unibo File Manager credentials from QGIS settings.

    Call this function once when the plugin initializes to enable
    authenticated access to Unibo File Manager storage.
    """
    try:
        from qgis.core import QgsSettings
        settings = QgsSettings()

        credentials = {}

        # Load Unibo storage credentials
        server_url = settings.value("pyarchinit/storage/unibo/server_url", "")
        username = settings.value("pyarchinit/storage/unibo/username", "")
        password = settings.value("pyarchinit/storage/unibo/password", "")

        if server_url:
            credentials['server_url'] = server_url
        if username:
            credentials['username'] = username
        if password:
            credentials['password'] = password

        if credentials and 'server_url' in credentials and 'username' in credentials:
            RemoteImageLoader.set_unibo_credentials(credentials)
            return True

        return False
    except ImportError:
        return False


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
    load_unibo_credentials_from_qgis()


def join_path(base_path: str, *parts: str) -> str:
    """
    Join path components correctly for both local and remote paths.

    For remote paths (unibo://, http://, https://, cloudinary://),
    uses forward slash. For local paths, uses os.path.join.

    Args:
        base_path: Base path (local or remote URL)
        *parts: Additional path components to join

    Returns:
        Joined path

    Example:
        join_path('unibo://project', 'folder', 'file.jpg')
        # Returns: 'unibo://project/folder/file.jpg'

        join_path('/local/path', 'folder', 'file.jpg')
        # Returns: '/local/path/folder/file.jpg' (OS-appropriate)
    """
    if not base_path:
        return os.path.join('', *parts) if parts else ''

    # Check if it's a remote URL
    if base_path.startswith(('unibo://', 'http://', 'https://', 'cloudinary://')):
        # Use forward slash for URLs
        result = base_path.rstrip('/')
        for part in parts:
            if part:
                result = result + '/' + str(part).lstrip('/')
        return result
    else:
        # Use os.path.join for local paths
        return os.path.join(base_path, *parts)
