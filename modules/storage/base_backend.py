"""
Base Storage Backend
====================

Abstract base class for all storage backends.
All backends must implement these methods.

Author: PyArchInit Team
License: GPL v2
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Union, BinaryIO
from dataclasses import dataclass
from enum import Enum
import os


class StorageType(Enum):
    """Enumeration of supported storage types"""
    LOCAL = "local"
    GOOGLE_DRIVE = "gdrive"
    DROPBOX = "dropbox"
    S3 = "s3"
    R2 = "r2"
    WEBDAV = "webdav"
    HTTP = "http"
    SFTP = "sftp"
    CLOUDINARY = "cloudinary"


@dataclass
class StorageFile:
    """Represents a file in storage"""
    name: str
    path: str
    size: int = 0
    modified: Optional[str] = None
    is_directory: bool = False
    mime_type: Optional[str] = None
    url: Optional[str] = None  # Public/preview URL if available

    def __repr__(self):
        return f"StorageFile(name='{self.name}', size={self.size}, is_dir={self.is_directory})"


@dataclass
class StorageConfig:
    """Configuration for a storage backend"""
    storage_type: StorageType
    base_path: str
    credentials: Optional[dict] = None
    options: Optional[dict] = None


class StorageBackend(ABC):
    """
    Abstract base class for storage backends.

    All storage backends must implement these methods to provide
    a consistent interface for file operations.
    """

    def __init__(self, base_path: str, credentials: Optional[dict] = None):
        """
        Initialize the storage backend.

        Args:
            base_path: The base path/URL for this storage
            credentials: Optional credentials dictionary
        """
        self.base_path = base_path
        self.credentials = credentials or {}
        self._connected = False

    @property
    @abstractmethod
    def storage_type(self) -> StorageType:
        """Return the type of this storage backend"""
        pass

    @property
    def is_remote(self) -> bool:
        """Return True if this is a remote storage backend"""
        return self.storage_type != StorageType.LOCAL

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the storage backend.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the storage backend"""
        pass

    @abstractmethod
    def read(self, filename: str) -> Optional[bytes]:
        """
        Read a file from storage.

        Args:
            filename: Path to the file relative to base_path

        Returns:
            File contents as bytes, or None if file doesn't exist
        """
        pass

    @abstractmethod
    def write(self, filename: str, data: Union[bytes, BinaryIO]) -> bool:
        """
        Write data to a file in storage.

        Args:
            filename: Path to the file relative to base_path
            data: File contents as bytes or file-like object

        Returns:
            True if write successful, False otherwise
        """
        pass

    @abstractmethod
    def exists(self, filename: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            filename: Path to the file relative to base_path

        Returns:
            True if file exists, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, filename: str) -> bool:
        """
        Delete a file from storage.

        Args:
            filename: Path to the file relative to base_path

        Returns:
            True if deletion successful, False otherwise
        """
        pass

    @abstractmethod
    def list(self, path: str = "") -> List[StorageFile]:
        """
        List files in a directory.

        Args:
            path: Path relative to base_path (empty for root)

        Returns:
            List of StorageFile objects
        """
        pass

    @abstractmethod
    def get_url(self, filename: str) -> Optional[str]:
        """
        Get a URL for accessing the file.

        For local files, returns file:// URL.
        For remote files, returns public/signed URL if available.

        Args:
            filename: Path to the file relative to base_path

        Returns:
            URL string or None if not available
        """
        pass

    def get_full_path(self, filename: str) -> str:
        """
        Get the full path/URL for a file.

        Args:
            filename: Path to the file relative to base_path

        Returns:
            Full path string
        """
        if self.base_path.endswith('/') or self.base_path.endswith(os.sep):
            return f"{self.base_path}{filename}"
        return f"{self.base_path}/{filename}"

    def ensure_directory(self, path: str) -> bool:
        """
        Ensure a directory exists in storage.

        Args:
            path: Directory path relative to base_path

        Returns:
            True if directory exists or was created, False otherwise
        """
        # Default implementation - subclasses may override
        return True

    def copy(self, source: str, destination: str) -> bool:
        """
        Copy a file within the same storage backend.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            True if copy successful, False otherwise
        """
        # Default implementation using read/write
        data = self.read(source)
        if data is not None:
            return self.write(destination, data)
        return False

    def move(self, source: str, destination: str) -> bool:
        """
        Move a file within the same storage backend.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            True if move successful, False otherwise
        """
        # Default implementation using copy/delete
        if self.copy(source, destination):
            return self.delete(source)
        return False

    def get_size(self, filename: str) -> int:
        """
        Get the size of a file in bytes.

        Args:
            filename: Path to the file relative to base_path

        Returns:
            File size in bytes, or -1 if file doesn't exist
        """
        # Default implementation - subclasses may override for efficiency
        data = self.read(filename)
        if data is not None:
            return len(data)
        return -1

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}(base_path='{self.base_path}')"
