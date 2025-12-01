"""
Local Storage Backend
=====================

Storage backend for local filesystem operations.
This provides backward compatibility with existing local path handling.

Author: PyArchInit Team
License: GPL v2
"""

import os
import shutil
from typing import List, Optional, Union, BinaryIO
from datetime import datetime
from urllib.parse import quote

from .base_backend import StorageBackend, StorageType, StorageFile


class LocalBackend(StorageBackend):
    """
    Local filesystem storage backend.

    This is the default backend for PyArchInit, maintaining
    full backward compatibility with existing local path handling.
    """

    @property
    def storage_type(self) -> StorageType:
        return StorageType.LOCAL

    def connect(self) -> bool:
        """
        Verify that the base path exists and is accessible.

        Returns:
            True if path exists and is accessible
        """
        try:
            if os.path.exists(self.base_path):
                self._connected = True
                return True
            # Try to create the directory
            os.makedirs(self.base_path, exist_ok=True)
            self._connected = True
            return True
        except (OSError, PermissionError) as e:
            self._connected = False
            return False

    def disconnect(self) -> None:
        """No action needed for local filesystem"""
        self._connected = False

    def read(self, filename: str) -> Optional[bytes]:
        """
        Read a file from local storage.

        Args:
            filename: Path to the file relative to base_path

        Returns:
            File contents as bytes, or None if file doesn't exist
        """
        full_path = self.get_full_path(filename)
        try:
            with open(full_path, 'rb') as f:
                return f.read()
        except (FileNotFoundError, PermissionError, IOError):
            return None

    def write(self, filename: str, data: Union[bytes, BinaryIO]) -> bool:
        """
        Write data to a file in local storage.

        Args:
            filename: Path to the file relative to base_path
            data: File contents as bytes or file-like object

        Returns:
            True if write successful, False otherwise
        """
        full_path = self.get_full_path(filename)

        # Ensure parent directory exists
        parent_dir = os.path.dirname(full_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        try:
            with open(full_path, 'wb') as f:
                if isinstance(data, bytes):
                    f.write(data)
                else:
                    # It's a file-like object
                    shutil.copyfileobj(data, f)
            return True
        except (PermissionError, IOError, OSError):
            return False

    def exists(self, filename: str) -> bool:
        """
        Check if a file exists in local storage.

        Args:
            filename: Path to the file relative to base_path

        Returns:
            True if file exists, False otherwise
        """
        full_path = self.get_full_path(filename)
        return os.path.exists(full_path)

    def delete(self, filename: str) -> bool:
        """
        Delete a file from local storage.

        Args:
            filename: Path to the file relative to base_path

        Returns:
            True if deletion successful, False otherwise
        """
        full_path = self.get_full_path(filename)
        try:
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)
            return True
        except (FileNotFoundError, PermissionError, OSError):
            return False

    def list(self, path: str = "") -> List[StorageFile]:
        """
        List files in a directory.

        Args:
            path: Path relative to base_path (empty for root)

        Returns:
            List of StorageFile objects
        """
        full_path = self.get_full_path(path) if path else self.base_path
        files = []

        try:
            for entry in os.scandir(full_path):
                stat_info = entry.stat()
                modified = datetime.fromtimestamp(stat_info.st_mtime).isoformat()

                # Determine MIME type for common image formats
                mime_type = None
                ext = os.path.splitext(entry.name)[1].lower()
                mime_types = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.tif': 'image/tiff',
                    '.tiff': 'image/tiff',
                    '.bmp': 'image/bmp',
                    '.webp': 'image/webp',
                    '.pdf': 'application/pdf',
                }
                mime_type = mime_types.get(ext)

                files.append(StorageFile(
                    name=entry.name,
                    path=os.path.join(path, entry.name) if path else entry.name,
                    size=stat_info.st_size if entry.is_file() else 0,
                    modified=modified,
                    is_directory=entry.is_dir(),
                    mime_type=mime_type,
                    url=self.get_url(os.path.join(path, entry.name) if path else entry.name)
                ))
        except (FileNotFoundError, PermissionError, OSError):
            pass

        return files

    def get_url(self, filename: str) -> Optional[str]:
        """
        Get a file:// URL for the file.

        Args:
            filename: Path to the file relative to base_path

        Returns:
            file:// URL string
        """
        full_path = self.get_full_path(filename)
        # Convert to file:// URL with proper encoding
        if os.path.exists(full_path):
            # Use forward slashes and URL encode the path
            url_path = full_path.replace(os.sep, '/')
            return f"file://{quote(url_path)}"
        return None

    def ensure_directory(self, path: str) -> bool:
        """
        Ensure a directory exists in local storage.

        Args:
            path: Directory path relative to base_path

        Returns:
            True if directory exists or was created
        """
        full_path = self.get_full_path(path)
        try:
            os.makedirs(full_path, exist_ok=True)
            return True
        except (PermissionError, OSError):
            return False

    def copy(self, source: str, destination: str) -> bool:
        """
        Copy a file within local storage.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            True if copy successful
        """
        src_path = self.get_full_path(source)
        dst_path = self.get_full_path(destination)

        # Ensure parent directory exists
        parent_dir = os.path.dirname(dst_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        try:
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
            return True
        except (FileNotFoundError, PermissionError, OSError):
            return False

    def move(self, source: str, destination: str) -> bool:
        """
        Move a file within local storage.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            True if move successful
        """
        src_path = self.get_full_path(source)
        dst_path = self.get_full_path(destination)

        # Ensure parent directory exists
        parent_dir = os.path.dirname(dst_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        try:
            shutil.move(src_path, dst_path)
            return True
        except (FileNotFoundError, PermissionError, OSError):
            return False

    def get_size(self, filename: str) -> int:
        """
        Get the size of a file in bytes.

        Args:
            filename: Path to the file relative to base_path

        Returns:
            File size in bytes, or -1 if file doesn't exist
        """
        full_path = self.get_full_path(filename)
        try:
            return os.path.getsize(full_path)
        except (FileNotFoundError, OSError):
            return -1

    def get_modified_time(self, filename: str) -> Optional[datetime]:
        """
        Get the last modified time of a file.

        Args:
            filename: Path to the file relative to base_path

        Returns:
            datetime object or None if file doesn't exist
        """
        full_path = self.get_full_path(filename)
        try:
            mtime = os.path.getmtime(full_path)
            return datetime.fromtimestamp(mtime)
        except (FileNotFoundError, OSError):
            return None
