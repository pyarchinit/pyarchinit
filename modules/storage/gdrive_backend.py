"""
Google Drive Storage Backend
============================

Storage backend for Google Drive using the Google Drive API.

Requirements:
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

Path format: gdrive://folder_name/subfolder/filename.jpg

Credentials required:
    - client_id: OAuth2 client ID
    - client_secret: OAuth2 client secret
    - refresh_token: OAuth2 refresh token (obtained after initial auth)

Author: PyArchInit Team
License: GPL v2
"""

import io
import os
from typing import List, Optional, Union, BinaryIO
from datetime import datetime

from .base_backend import StorageBackend, StorageType, StorageFile


class GDriveBackend(StorageBackend):
    """
    Google Drive storage backend.

    Uses the Google Drive API v3 for file operations.
    Supports folder hierarchy and file sharing.
    """

    # Google Drive API scopes
    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    # MIME type for Google Drive folders
    FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'

    @property
    def storage_type(self) -> StorageType:
        return StorageType.GOOGLE_DRIVE

    def __init__(self, base_path: str, credentials: Optional[dict] = None):
        """
        Initialize Google Drive backend.

        Args:
            base_path: Root folder name/ID in Google Drive
            credentials: Dict with client_id, client_secret, refresh_token
        """
        super().__init__(base_path, credentials)
        self._service = None
        self._root_folder_id = None
        self._folder_cache = {}  # Cache folder IDs

    def connect(self) -> bool:
        """
        Establish connection to Google Drive API.

        Returns:
            True if connection successful
        """
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            # Get credentials
            client_id = self.credentials.get('client_id')
            client_secret = self.credentials.get('client_secret')
            refresh_token = self.credentials.get('refresh_token')

            if not all([client_id, client_secret, refresh_token]):
                return False

            # Create credentials object
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=client_id,
                client_secret=client_secret,
                scopes=self.SCOPES
            )

            # Refresh the token
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            # Build the service
            self._service = build('drive', 'v3', credentials=creds)

            # Find or create the root folder
            self._root_folder_id = self._get_or_create_folder(self.base_path, parent_id='root')

            self._connected = True
            return True

        except ImportError:
            # Google API libraries not installed
            return False
        except Exception as e:
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Close connection to Google Drive"""
        self._service = None
        self._root_folder_id = None
        self._folder_cache.clear()
        self._connected = False

    def _get_or_create_folder(self, folder_name: str, parent_id: str = None) -> Optional[str]:
        """
        Get or create a folder in Google Drive.

        Args:
            folder_name: Name of the folder
            parent_id: Parent folder ID (None for root)

        Returns:
            Folder ID or None
        """
        if not self._service:
            return None

        parent_id = parent_id or 'root'
        cache_key = f"{parent_id}/{folder_name}"

        if cache_key in self._folder_cache:
            return self._folder_cache[cache_key]

        try:
            # Search for existing folder
            query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='{self.FOLDER_MIME_TYPE}' and trashed=false"
            results = self._service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            files = results.get('files', [])

            if files:
                folder_id = files[0]['id']
            else:
                # Create new folder
                file_metadata = {
                    'name': folder_name,
                    'mimeType': self.FOLDER_MIME_TYPE,
                    'parents': [parent_id]
                }
                folder = self._service.files().create(
                    body=file_metadata,
                    fields='id'
                ).execute()
                folder_id = folder.get('id')

            self._folder_cache[cache_key] = folder_id
            return folder_id

        except Exception:
            return None

    def _get_folder_id_for_path(self, path: str) -> Optional[str]:
        """
        Get the folder ID for a path, creating folders as needed.

        Args:
            path: Path relative to root (e.g., "subfolder/images")

        Returns:
            Folder ID or None
        """
        if not path:
            return self._root_folder_id

        parts = path.strip('/').split('/')
        current_parent = self._root_folder_id

        for part in parts:
            if part:
                current_parent = self._get_or_create_folder(part, current_parent)
                if not current_parent:
                    return None

        return current_parent

    def _find_file(self, filename: str, parent_id: str = None) -> Optional[dict]:
        """
        Find a file by name in a folder.

        Args:
            filename: Name of the file
            parent_id: Parent folder ID

        Returns:
            File metadata dict or None
        """
        if not self._service:
            return None

        parent_id = parent_id or self._root_folder_id

        try:
            query = f"name='{filename}' and '{parent_id}' in parents and trashed=false"
            results = self._service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, size, mimeType, modifiedTime, webViewLink, webContentLink)'
            ).execute()

            files = results.get('files', [])
            return files[0] if files else None

        except Exception:
            return None

    def read(self, filename: str) -> Optional[bytes]:
        """
        Read a file from Google Drive.

        Args:
            filename: Path to the file relative to base folder

        Returns:
            File contents as bytes, or None
        """
        if not self._service:
            return None

        try:
            from googleapiclient.http import MediaIoBaseDownload

            # Parse path
            dir_path = os.path.dirname(filename)
            file_name = os.path.basename(filename)

            # Get folder ID
            folder_id = self._get_folder_id_for_path(dir_path)
            if not folder_id:
                return None

            # Find the file
            file_info = self._find_file(file_name, folder_id)
            if not file_info:
                return None

            # Download the file
            request = self._service.files().get_media(fileId=file_info['id'])
            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            return file_buffer.getvalue()

        except Exception:
            return None

    def write(self, filename: str, data: Union[bytes, BinaryIO]) -> bool:
        """
        Write a file to Google Drive.

        Args:
            filename: Path to the file relative to base folder
            data: File contents as bytes or file-like object

        Returns:
            True if successful
        """
        if not self._service:
            return False

        try:
            from googleapiclient.http import MediaIoBaseUpload

            # Parse path
            dir_path = os.path.dirname(filename)
            file_name = os.path.basename(filename)

            # Get or create folder
            folder_id = self._get_folder_id_for_path(dir_path)
            if not folder_id:
                return False

            # Prepare data
            if isinstance(data, bytes):
                file_buffer = io.BytesIO(data)
            else:
                file_buffer = data

            # Detect MIME type
            mime_type = self._detect_mime_type(file_name)

            # Check if file exists (for update)
            existing_file = self._find_file(file_name, folder_id)

            media = MediaIoBaseUpload(
                file_buffer,
                mimetype=mime_type,
                resumable=True
            )

            if existing_file:
                # Update existing file
                self._service.files().update(
                    fileId=existing_file['id'],
                    media_body=media
                ).execute()
            else:
                # Create new file
                file_metadata = {
                    'name': file_name,
                    'parents': [folder_id]
                }
                self._service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()

            return True

        except Exception:
            return False

    def exists(self, filename: str) -> bool:
        """
        Check if a file exists in Google Drive.

        Args:
            filename: Path to the file relative to base folder

        Returns:
            True if file exists
        """
        if not self._service:
            return False

        dir_path = os.path.dirname(filename)
        file_name = os.path.basename(filename)

        folder_id = self._get_folder_id_for_path(dir_path)
        if not folder_id:
            return False

        return self._find_file(file_name, folder_id) is not None

    def delete(self, filename: str) -> bool:
        """
        Delete a file from Google Drive (moves to trash).

        Args:
            filename: Path to the file relative to base folder

        Returns:
            True if deletion successful
        """
        if not self._service:
            return False

        try:
            dir_path = os.path.dirname(filename)
            file_name = os.path.basename(filename)

            folder_id = self._get_folder_id_for_path(dir_path)
            if not folder_id:
                return False

            file_info = self._find_file(file_name, folder_id)
            if not file_info:
                return False

            # Move to trash
            self._service.files().update(
                fileId=file_info['id'],
                body={'trashed': True}
            ).execute()

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
        if not self._service:
            return []

        files = []

        try:
            folder_id = self._get_folder_id_for_path(path)
            if not folder_id:
                return []

            query = f"'{folder_id}' in parents and trashed=false"
            results = self._service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, size, mimeType, modifiedTime, webViewLink, webContentLink)',
                orderBy='name'
            ).execute()

            for item in results.get('files', []):
                is_folder = item.get('mimeType') == self.FOLDER_MIME_TYPE
                file_path = os.path.join(path, item['name']) if path else item['name']

                files.append(StorageFile(
                    name=item['name'],
                    path=file_path,
                    size=int(item.get('size', 0)),
                    modified=item.get('modifiedTime'),
                    is_directory=is_folder,
                    mime_type=item.get('mimeType'),
                    url=item.get('webViewLink') or item.get('webContentLink')
                ))

        except Exception:
            pass

        return files

    def get_url(self, filename: str) -> Optional[str]:
        """
        Get a shareable URL for the file.

        Args:
            filename: Path to the file relative to base folder

        Returns:
            Web view URL or None
        """
        if not self._service:
            return None

        dir_path = os.path.dirname(filename)
        file_name = os.path.basename(filename)

        folder_id = self._get_folder_id_for_path(dir_path)
        if not folder_id:
            return None

        file_info = self._find_file(file_name, folder_id)
        if file_info:
            return file_info.get('webViewLink') or file_info.get('webContentLink')

        return None

    def get_direct_url(self, filename: str) -> Optional[str]:
        """
        Get a direct download URL for the file.

        Note: Requires the file to be shared publicly or with anyone with the link.

        Args:
            filename: Path to the file relative to base folder

        Returns:
            Direct download URL or None
        """
        if not self._service:
            return None

        dir_path = os.path.dirname(filename)
        file_name = os.path.basename(filename)

        folder_id = self._get_folder_id_for_path(dir_path)
        if not folder_id:
            return None

        file_info = self._find_file(file_name, folder_id)
        if file_info:
            file_id = file_info['id']
            return f"https://drive.google.com/uc?export=download&id={file_id}"

        return None

    def _detect_mime_type(self, filename: str) -> str:
        """Detect MIME type from filename"""
        ext = os.path.splitext(filename)[1].lower()
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
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.xml': 'application/xml',
        }
        return mime_types.get(ext, 'application/octet-stream')

    def share_file(self, filename: str, anyone_with_link: bool = True) -> Optional[str]:
        """
        Share a file and return the shareable link.

        Args:
            filename: Path to the file
            anyone_with_link: If True, anyone with the link can view

        Returns:
            Shareable URL or None
        """
        if not self._service:
            return None

        try:
            dir_path = os.path.dirname(filename)
            file_name = os.path.basename(filename)

            folder_id = self._get_folder_id_for_path(dir_path)
            if not folder_id:
                return None

            file_info = self._find_file(file_name, folder_id)
            if not file_info:
                return None

            # Create permission
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            self._service.permissions().create(
                fileId=file_info['id'],
                body=permission
            ).execute()

            return self.get_url(filename)

        except Exception:
            return None
