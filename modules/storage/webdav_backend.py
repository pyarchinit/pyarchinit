"""
WebDAV Storage Backend
======================

Storage backend for WebDAV servers.

Requirements:
    pip install webdavclient3

Path format: webdav://server.com/path/to/folder

Credentials required:
    - username: WebDAV username
    - password: WebDAV password

Author: PyArchInit Team
License: GPL v2
"""

import os
from typing import List, Optional, Union, BinaryIO
from urllib.parse import urljoin, urlparse

from .base_backend import StorageBackend, StorageType, StorageFile


class WebDAVBackend(StorageBackend):
    """
    WebDAV storage backend.

    Uses webdavclient3 for WebDAV operations.
    Compatible with Nextcloud, ownCloud, and other WebDAV servers.
    """

    @property
    def storage_type(self) -> StorageType:
        return StorageType.WEBDAV

    def __init__(self, base_path: str, credentials: Optional[dict] = None):
        """
        Initialize WebDAV backend.

        Args:
            base_path: WebDAV server URL (e.g., "https://cloud.example.com/remote.php/dav/files/user")
            credentials: Dict with username and password
        """
        super().__init__(base_path, credentials)
        self._client = None
        self._webdav_url = base_path

    def connect(self) -> bool:
        """
        Establish connection to WebDAV server.

        Returns:
            True if connection successful
        """
        try:
            from webdav3.client import Client

            username = self.credentials.get('username')
            password = self.credentials.get('password')

            if not username or not password:
                return False

            # Parse URL
            parsed = urlparse(self._webdav_url)

            options = {
                'webdav_hostname': f"{parsed.scheme}://{parsed.netloc}",
                'webdav_login': username,
                'webdav_password': password,
                'webdav_root': parsed.path or '/'
            }

            self._client = Client(options)

            # Test connection
            self._client.check()

            self._connected = True
            return True

        except ImportError:
            # webdavclient3 not installed
            return False
        except Exception:
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Close connection to WebDAV server"""
        self._client = None
        self._connected = False

    def read(self, filename: str) -> Optional[bytes]:
        """
        Read a file from WebDAV server.

        Args:
            filename: Path to the file relative to base path

        Returns:
            File contents as bytes, or None
        """
        if not self._client:
            return None

        try:
            import io
            buffer = io.BytesIO()
            self._client.download_from(buffer, filename)
            return buffer.getvalue()

        except Exception:
            return None

    def write(self, filename: str, data: Union[bytes, BinaryIO]) -> bool:
        """
        Write a file to WebDAV server.

        Args:
            filename: Path to the file relative to base path
            data: File contents as bytes or file-like object

        Returns:
            True if successful
        """
        if not self._client:
            return False

        try:
            import io

            # Ensure parent directory exists
            parent_dir = os.path.dirname(filename)
            if parent_dir:
                self.ensure_directory(parent_dir)

            # Prepare data
            if isinstance(data, bytes):
                buffer = io.BytesIO(data)
            else:
                buffer = data

            self._client.upload_to(buffer, filename)
            return True

        except Exception:
            return False

    def exists(self, filename: str) -> bool:
        """
        Check if a file exists on WebDAV server.

        Args:
            filename: Path to the file relative to base path

        Returns:
            True if file exists
        """
        if not self._client:
            return False

        try:
            return self._client.check(filename)
        except Exception:
            return False

    def delete(self, filename: str) -> bool:
        """
        Delete a file from WebDAV server.

        Args:
            filename: Path to the file relative to base path

        Returns:
            True if deletion successful
        """
        if not self._client:
            return False

        try:
            self._client.clean(filename)
            return True
        except Exception:
            return False

    def list(self, path: str = "") -> List[StorageFile]:
        """
        List files in a directory.

        Args:
            path: Path relative to base path

        Returns:
            List of StorageFile objects
        """
        if not self._client:
            return []

        files = []

        try:
            items = self._client.list(path or '/')

            for item in items:
                # Skip parent directory reference
                if item == '..' or item == '.':
                    continue

                full_path = os.path.join(path, item) if path else item
                is_dir = item.endswith('/')

                # Clean up name
                name = item.rstrip('/')

                # Try to get file info
                size = 0
                modified = None

                try:
                    info = self._client.info(full_path.rstrip('/'))
                    size = int(info.get('size', 0))
                    modified = info.get('modified')
                except Exception:
                    pass

                files.append(StorageFile(
                    name=name,
                    path=full_path.rstrip('/'),
                    size=size,
                    modified=modified,
                    is_directory=is_dir,
                    mime_type=None,
                    url=self.get_url(full_path.rstrip('/'))
                ))

        except Exception:
            pass

        return files

    def get_url(self, filename: str) -> Optional[str]:
        """
        Get the full URL for a file.

        Args:
            filename: Path to the file relative to base path

        Returns:
            Full URL to the file
        """
        if filename.startswith('/'):
            filename = filename[1:]

        return urljoin(self._webdav_url + '/', filename)

    def ensure_directory(self, path: str) -> bool:
        """
        Ensure a directory exists on WebDAV server.

        Args:
            path: Directory path relative to base path

        Returns:
            True if directory exists or was created
        """
        if not self._client:
            return False

        if not path:
            return True

        try:
            # Create all parent directories
            parts = path.strip('/').split('/')
            current_path = ''

            for part in parts:
                current_path = f"{current_path}/{part}" if current_path else part

                if not self._client.check(current_path):
                    self._client.mkdir(current_path)

            return True

        except Exception:
            return False

    def copy(self, source: str, destination: str) -> bool:
        """
        Copy a file on WebDAV server.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            True if copy successful
        """
        if not self._client:
            return False

        try:
            self._client.copy(source, destination)
            return True
        except Exception:
            return False

    def move(self, source: str, destination: str) -> bool:
        """
        Move a file on WebDAV server.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            True if move successful
        """
        if not self._client:
            return False

        try:
            self._client.move(source, destination)
            return True
        except Exception:
            return False

    def get_size(self, filename: str) -> int:
        """
        Get the size of a file in bytes.

        Args:
            filename: Path to the file relative to base path

        Returns:
            File size in bytes, or -1 if file doesn't exist
        """
        if not self._client:
            return -1

        try:
            info = self._client.info(filename)
            return int(info.get('size', -1))
        except Exception:
            return -1
