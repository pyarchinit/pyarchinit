"""
Dropbox Storage Backend
=======================

Storage backend for Dropbox using the Dropbox API.

Requirements:
    pip install dropbox

Path format: dropbox://folder/subfolder/filename.jpg

Credentials required:
    - access_token: Dropbox access token (or refresh_token + app_key + app_secret)
    - app_key: Dropbox app key (for refresh tokens)
    - app_secret: Dropbox app secret (for refresh tokens)

Author: PyArchInit Team
License: GPL v2
"""

import io
import os
from typing import List, Optional, Union, BinaryIO

from .base_backend import StorageBackend, StorageType, StorageFile


class DropboxBackend(StorageBackend):
    """
    Dropbox storage backend.

    Uses the Dropbox API v2 for file operations.
    """

    # Chunk size for uploads (150 MB is Dropbox's limit per chunk)
    CHUNK_SIZE = 150 * 1024 * 1024

    @property
    def storage_type(self) -> StorageType:
        return StorageType.DROPBOX

    def __init__(self, base_path: str, credentials: Optional[dict] = None):
        """
        Initialize Dropbox backend.

        Args:
            base_path: Root folder path in Dropbox (e.g., "/PyArchInit")
            credentials: Dict with access_token or refresh_token + app_key + app_secret
        """
        super().__init__(base_path, credentials)
        self._dbx = None

        # Ensure base_path starts with /
        if self.base_path and not self.base_path.startswith('/'):
            self.base_path = '/' + self.base_path

    def connect(self) -> bool:
        """
        Establish connection to Dropbox API.

        Returns:
            True if connection successful
        """
        try:
            import dropbox
            from dropbox.exceptions import AuthError

            access_token = self.credentials.get('access_token')
            refresh_token = self.credentials.get('refresh_token')
            app_key = self.credentials.get('app_key')
            app_secret = self.credentials.get('app_secret')

            if access_token:
                # Use access token directly
                self._dbx = dropbox.Dropbox(access_token)
            elif refresh_token and app_key and app_secret:
                # Use refresh token
                self._dbx = dropbox.Dropbox(
                    oauth2_refresh_token=refresh_token,
                    app_key=app_key,
                    app_secret=app_secret
                )
            else:
                return False

            # Test connection
            self._dbx.users_get_current_account()

            # Ensure base folder exists
            if self.base_path and self.base_path != '/':
                self.ensure_directory('')

            self._connected = True
            return True

        except ImportError:
            # Dropbox library not installed
            return False
        except Exception:
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Close connection to Dropbox"""
        self._dbx = None
        self._connected = False

    def _get_full_dropbox_path(self, filename: str) -> str:
        """
        Get the full Dropbox path for a file.

        Args:
            filename: Path relative to base folder

        Returns:
            Full Dropbox path
        """
        if not filename:
            return self.base_path or ''

        # Normalize path
        if filename.startswith('/'):
            filename = filename[1:]

        if self.base_path:
            if self.base_path.endswith('/'):
                return f"{self.base_path}{filename}"
            return f"{self.base_path}/{filename}"

        return f"/{filename}"

    def read(self, filename: str) -> Optional[bytes]:
        """
        Read a file from Dropbox.

        Args:
            filename: Path to the file relative to base folder

        Returns:
            File contents as bytes, or None
        """
        if not self._dbx:
            return None

        try:
            path = self._get_full_dropbox_path(filename)
            _, response = self._dbx.files_download(path)
            return response.content

        except Exception:
            return None

    def write(self, filename: str, data: Union[bytes, BinaryIO]) -> bool:
        """
        Write a file to Dropbox.

        Args:
            filename: Path to the file relative to base folder
            data: File contents as bytes or file-like object

        Returns:
            True if successful
        """
        if not self._dbx:
            return False

        try:
            import dropbox

            path = self._get_full_dropbox_path(filename)

            # Ensure parent directory exists
            parent_dir = os.path.dirname(path)
            if parent_dir and parent_dir != '/':
                self.ensure_directory(os.path.dirname(filename))

            # Convert to bytes if necessary
            if isinstance(data, bytes):
                file_data = data
            else:
                file_data = data.read()

            # Use upload for small files, upload_session for large files
            if len(file_data) <= self.CHUNK_SIZE:
                self._dbx.files_upload(
                    file_data,
                    path,
                    mode=dropbox.files.WriteMode.overwrite
                )
            else:
                # Chunked upload for large files
                self._chunked_upload(path, file_data)

            return True

        except Exception:
            return False

    def _chunked_upload(self, path: str, data: bytes):
        """
        Upload a large file using upload sessions.

        Args:
            path: Full Dropbox path
            data: File data
        """
        import dropbox

        file_size = len(data)
        cursor = None
        offset = 0

        while offset < file_size:
            chunk = data[offset:offset + self.CHUNK_SIZE]

            if offset == 0:
                # Start session
                result = self._dbx.files_upload_session_start(chunk)
                cursor = dropbox.files.UploadSessionCursor(
                    session_id=result.session_id,
                    offset=len(chunk)
                )
            elif offset + len(chunk) < file_size:
                # Append to session
                self._dbx.files_upload_session_append_v2(chunk, cursor)
                cursor.offset += len(chunk)
            else:
                # Finish session
                commit = dropbox.files.CommitInfo(
                    path=path,
                    mode=dropbox.files.WriteMode.overwrite
                )
                self._dbx.files_upload_session_finish(chunk, cursor, commit)

            offset += len(chunk)

    def exists(self, filename: str) -> bool:
        """
        Check if a file exists in Dropbox.

        Args:
            filename: Path to the file relative to base folder

        Returns:
            True if file exists
        """
        if not self._dbx:
            return False

        try:
            path = self._get_full_dropbox_path(filename)
            self._dbx.files_get_metadata(path)
            return True
        except Exception:
            return False

    def delete(self, filename: str) -> bool:
        """
        Delete a file from Dropbox.

        Args:
            filename: Path to the file relative to base folder

        Returns:
            True if deletion successful
        """
        if not self._dbx:
            return False

        try:
            path = self._get_full_dropbox_path(filename)
            self._dbx.files_delete_v2(path)
            return True
        except Exception:
            return False

    def list(self, path: str = "") -> List[StorageFile]:
        """
        List files in a folder.

        Args:
            path: Path relative to base folder

        Returns:
            List of StorageFile objects
        """
        if not self._dbx:
            return []

        files = []

        try:
            import dropbox

            full_path = self._get_full_dropbox_path(path)
            if full_path == '/':
                full_path = ''

            result = self._dbx.files_list_folder(full_path)

            while True:
                for entry in result.entries:
                    is_folder = isinstance(entry, dropbox.files.FolderMetadata)

                    file_path = entry.path_display
                    if self.base_path:
                        # Make path relative to base
                        file_path = file_path[len(self.base_path):].lstrip('/')

                    size = 0
                    modified = None

                    if isinstance(entry, dropbox.files.FileMetadata):
                        size = entry.size
                        modified = entry.server_modified.isoformat() if entry.server_modified else None

                    files.append(StorageFile(
                        name=entry.name,
                        path=file_path,
                        size=size,
                        modified=modified,
                        is_directory=is_folder,
                        mime_type=None,
                        url=None
                    ))

                if not result.has_more:
                    break

                result = self._dbx.files_list_folder_continue(result.cursor)

        except Exception:
            pass

        return files

    def get_url(self, filename: str) -> Optional[str]:
        """
        Get a temporary download link for the file.

        Args:
            filename: Path to the file relative to base folder

        Returns:
            Temporary download URL (valid for 4 hours)
        """
        if not self._dbx:
            return None

        try:
            path = self._get_full_dropbox_path(filename)
            link = self._dbx.files_get_temporary_link(path)
            return link.link
        except Exception:
            return None

    def ensure_directory(self, path: str) -> bool:
        """
        Ensure a directory exists in Dropbox.

        Args:
            path: Directory path relative to base folder

        Returns:
            True if directory exists or was created
        """
        if not self._dbx:
            return False

        try:
            full_path = self._get_full_dropbox_path(path)
            if not full_path or full_path == '/':
                return True

            # Try to create the folder
            try:
                self._dbx.files_create_folder_v2(full_path)
            except Exception:
                # Folder might already exist
                pass

            return True

        except Exception:
            return False

    def get_shared_link(self, filename: str) -> Optional[str]:
        """
        Get or create a shared link for the file.

        Args:
            filename: Path to the file relative to base folder

        Returns:
            Shared link URL (permanent)
        """
        if not self._dbx:
            return None

        try:
            import dropbox

            path = self._get_full_dropbox_path(filename)

            # Try to get existing shared link
            try:
                links = self._dbx.sharing_list_shared_links(path=path)
                if links.links:
                    return links.links[0].url
            except Exception:
                pass

            # Create new shared link
            settings = dropbox.sharing.SharedLinkSettings(
                requested_visibility=dropbox.sharing.RequestedVisibility.public
            )
            link = self._dbx.sharing_create_shared_link_with_settings(path, settings)
            return link.url

        except Exception:
            return None

    def get_size(self, filename: str) -> int:
        """
        Get the size of a file in bytes.

        Args:
            filename: Path to the file relative to base folder

        Returns:
            File size in bytes, or -1 if file doesn't exist
        """
        if not self._dbx:
            return -1

        try:
            import dropbox

            path = self._get_full_dropbox_path(filename)
            metadata = self._dbx.files_get_metadata(path)

            if isinstance(metadata, dropbox.files.FileMetadata):
                return metadata.size

            return -1

        except Exception:
            return -1
