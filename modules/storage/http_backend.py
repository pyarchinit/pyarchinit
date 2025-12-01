"""
HTTP/HTTPS Storage Backend
==========================

Storage backend for HTTP/HTTPS URLs (primarily read-only).

This backend is useful for accessing images and files served via HTTP/HTTPS,
such as static file servers, CDNs, or IIIF image servers.

Path format:
    - http://server.com/path/to/files/
    - https://server.com/path/to/files/

Credentials (optional):
    - username: HTTP Basic Auth username
    - password: HTTP Basic Auth password
    - bearer_token: Bearer token for Authorization header
    - api_key: X-API-Key header (for PyArchInit Storage Proxy)

Author: PyArchInit Team
License: GPL v2
"""

import os
from typing import List, Optional, Union, BinaryIO
from urllib.parse import urljoin, urlparse, quote
import requests

from .base_backend import StorageBackend, StorageType, StorageFile


class HTTPBackend(StorageBackend):
    """
    HTTP/HTTPS storage backend.

    Primarily for read operations. Write/delete operations may be supported
    if the server implements them (e.g., via PUT/DELETE methods).
    """

    # Default timeout for HTTP requests (seconds)
    DEFAULT_TIMEOUT = 30

    @property
    def storage_type(self) -> StorageType:
        return StorageType.HTTP

    def __init__(self, base_path: str, credentials: Optional[dict] = None):
        """
        Initialize HTTP backend.

        Args:
            base_path: Base URL (e.g., "https://example.com/files/")
            credentials: Dict with username/password or bearer_token
        """
        super().__init__(base_path, credentials)
        self._session = None

        # Ensure base_path ends with /
        if self.base_path and not self.base_path.endswith('/'):
            self.base_path = self.base_path + '/'

    def connect(self) -> bool:
        """
        Initialize HTTP session.

        Returns:
            True if connection successful
        """
        try:
            self._session = requests.Session()

            # Set up authentication
            username = self.credentials.get('username')
            password = self.credentials.get('password')
            bearer_token = self.credentials.get('bearer_token')
            api_key = self.credentials.get('api_key')

            if username and password:
                self._session.auth = (username, password)
            elif bearer_token:
                self._session.headers['Authorization'] = f'Bearer {bearer_token}'

            # Add API key header (for PyArchInit Storage Proxy)
            if api_key:
                self._session.headers['X-API-Key'] = api_key

            # Test connection with HEAD request
            response = self._session.head(
                self.base_path,
                timeout=self.DEFAULT_TIMEOUT,
                allow_redirects=True
            )

            # Accept any 2xx or 3xx response
            self._connected = response.status_code < 400

            return self._connected

        except Exception:
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Close HTTP session"""
        if self._session:
            self._session.close()
        self._session = None
        self._connected = False

    def _get_url(self, filename: str) -> str:
        """Get full URL for a file"""
        if filename.startswith('/'):
            filename = filename[1:]
        return urljoin(self.base_path, quote(filename, safe='/'))

    def read(self, filename: str) -> Optional[bytes]:
        """
        Read a file via HTTP GET.

        Args:
            filename: Path to the file relative to base URL

        Returns:
            File contents as bytes, or None
        """
        if not self._session:
            return None

        try:
            url = self._get_url(filename)
            response = self._session.get(
                url,
                timeout=self.DEFAULT_TIMEOUT
            )

            if response.status_code == 200:
                return response.content

            return None

        except Exception:
            return None

    def write(self, filename: str, data: Union[bytes, BinaryIO]) -> bool:
        """
        Write a file via HTTP PUT (if supported by server).

        Args:
            filename: Path to the file relative to base URL
            data: File contents as bytes or file-like object

        Returns:
            True if successful
        """
        if not self._session:
            return False

        try:
            url = self._get_url(filename)

            # Prepare data
            if isinstance(data, bytes):
                body = data
            else:
                body = data.read()

            # Detect content type
            content_type = self._detect_content_type(filename)

            response = self._session.put(
                url,
                data=body,
                headers={'Content-Type': content_type},
                timeout=self.DEFAULT_TIMEOUT
            )

            return response.status_code in (200, 201, 204)

        except Exception:
            return False

    def exists(self, filename: str) -> bool:
        """
        Check if a file exists via HTTP HEAD.

        Args:
            filename: Path to the file relative to base URL

        Returns:
            True if file exists (HTTP 200 or 204)
        """
        if not self._session:
            return False

        try:
            url = self._get_url(filename)
            response = self._session.head(
                url,
                timeout=self.DEFAULT_TIMEOUT,
                allow_redirects=True
            )

            return response.status_code in (200, 204)

        except Exception:
            return False

    def delete(self, filename: str) -> bool:
        """
        Delete a file via HTTP DELETE (if supported by server).

        Args:
            filename: Path to the file relative to base URL

        Returns:
            True if deletion successful
        """
        if not self._session:
            return False

        try:
            url = self._get_url(filename)
            response = self._session.delete(
                url,
                timeout=self.DEFAULT_TIMEOUT
            )

            return response.status_code in (200, 204)

        except Exception:
            return False

    def list(self, path: str = "") -> List[StorageFile]:
        """
        List files (limited support - depends on server).

        Most HTTP servers don't support directory listing.
        This method attempts to parse Apache/Nginx directory index pages.

        Args:
            path: Path relative to base URL

        Returns:
            List of StorageFile objects (may be empty)
        """
        if not self._session:
            return []

        files = []

        try:
            url = self._get_url(path)
            if not url.endswith('/'):
                url += '/'

            response = self._session.get(
                url,
                timeout=self.DEFAULT_TIMEOUT
            )

            if response.status_code != 200:
                return []

            # Try to parse HTML directory listing
            content = response.text

            # Parse Apache-style directory listing
            import re

            # Pattern for Apache/Nginx directory listings
            # Matches: <a href="filename">filename</a>
            pattern = r'<a\s+href="([^"]+)"[^>]*>([^<]+)</a>'

            for match in re.finditer(pattern, content, re.IGNORECASE):
                href = match.group(1)
                name = match.group(2).strip()

                # Skip parent directory and absolute URLs
                if href.startswith('/') or href.startswith('?') or href.startswith('http'):
                    continue
                if name in ('..', 'Parent Directory', '../'):
                    continue

                is_dir = href.endswith('/')
                file_path = os.path.join(path, href.rstrip('/')) if path else href.rstrip('/')

                files.append(StorageFile(
                    name=name.rstrip('/'),
                    path=file_path,
                    size=0,  # Size not available from directory listing
                    modified=None,
                    is_directory=is_dir,
                    mime_type=None,
                    url=self._get_url(file_path)
                ))

        except Exception:
            pass

        return files

    def get_url(self, filename: str) -> Optional[str]:
        """
        Get the full URL for a file.

        Args:
            filename: Path to the file relative to base URL

        Returns:
            Full URL string
        """
        return self._get_url(filename)

    def get_size(self, filename: str) -> int:
        """
        Get the size of a file via HTTP HEAD Content-Length.

        Args:
            filename: Path to the file relative to base URL

        Returns:
            File size in bytes, or -1 if not available
        """
        if not self._session:
            return -1

        try:
            url = self._get_url(filename)
            response = self._session.head(
                url,
                timeout=self.DEFAULT_TIMEOUT,
                allow_redirects=True
            )

            if response.status_code == 200:
                content_length = response.headers.get('Content-Length')
                if content_length:
                    return int(content_length)

            return -1

        except Exception:
            return -1

    def _detect_content_type(self, filename: str) -> str:
        """Detect content type from filename"""
        ext = os.path.splitext(filename)[1].lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.tif': 'image/tiff',
            '.tiff': 'image/tiff',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.xml': 'application/xml',
        }
        return content_types.get(ext, 'application/octet-stream')

    def download_to_file(self, filename: str, local_path: str) -> bool:
        """
        Download a file directly to local disk (streaming).

        Args:
            filename: Path to the file relative to base URL
            local_path: Local file path to save to

        Returns:
            True if successful
        """
        if not self._session:
            return False

        try:
            url = self._get_url(filename)

            # Ensure parent directory exists
            parent_dir = os.path.dirname(local_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            # Stream download
            with self._session.get(url, stream=True, timeout=self.DEFAULT_TIMEOUT) as response:
                if response.status_code != 200:
                    return False

                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            return True

        except Exception:
            return False
