"""
Unibo File Manager Storage Backend
===================================

Storage backend for University of Bologna File Manager.

This backend connects to the Unibo File Manager API and allows
PyArchInit to read files stored in the remote file manager.

Path format:
    - unibo://project_code/folder/path/to/files/
    - Example: unibo://Al-Khutm/KTM2025/photolog/original/

Credentials:
    - username: Unibo username (e.g., enzo.cocca@unibo.it)
    - password: Unibo password
    - server_url: File Manager server URL (default: https://137.204.128.220)

Author: PyArchInit Team / Enzo Cocca
License: GPL v2
"""

import os
import json
import ssl
from typing import List, Optional, Union, BinaryIO, Dict
from urllib.parse import urljoin, quote, urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from .base_backend import StorageBackend, StorageType, StorageFile


# Create SSL context that doesn't verify certificates (for self-signed certs)
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


class UniboFileManagerBackend(StorageBackend):
    """
    Unibo File Manager storage backend.

    Connects to the University of Bologna File Manager API for
    reading archaeological documentation files.
    """

    # Default timeout for HTTP requests (seconds)
    DEFAULT_TIMEOUT = 30

    # Cache for folder/file ID mappings
    _path_cache: Dict[str, dict] = {}
    _token: Optional[str] = None

    @property
    def storage_type(self) -> StorageType:
        # Use HTTP type since it's HTTP-based
        return StorageType.HTTP

    def __init__(self, base_path: str, credentials: Optional[dict] = None):
        """
        Initialize Unibo File Manager backend.

        Args:
            base_path: Project path (e.g., "Al-Khutm/KTM2025/photolog/original")
            credentials: Dict with username, password, and optionally server_url
        """
        super().__init__(base_path, credentials)

        # Parse server URL from credentials or use default
        self.server_url = self.credentials.get('server_url', 'https://137.204.128.220')
        if not self.server_url.endswith('/'):
            self.server_url = self.server_url + '/'

        self.api_base = f"{self.server_url}api/v1/"

        # Parse project code and folder path from base_path
        # Format: project_code/folder/path
        parts = self.base_path.strip('/').split('/', 1)
        self.project_code = parts[0] if parts else None
        self.folder_path = parts[1] if len(parts) > 1 else ''

        # Cache for project and folder IDs
        self._project_id = None
        self._folder_id = None
        self._token = None

    def _make_request(self, url: str, method: str = 'GET', data: bytes = None,
                      headers: dict = None, timeout: int = None,
                      retry_on_401: bool = True) -> Optional[bytes]:
        """Make an HTTP request using urllib"""
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT

        req_headers = headers or {}
        if self._token:
            req_headers['Authorization'] = f'Bearer {self._token}'

        try:
            request = Request(url, data=data, headers=req_headers, method=method)
            with urlopen(request, context=SSL_CONTEXT, timeout=timeout) as response:
                return response.read()
        except HTTPError as e:
            if e.code == 401 and retry_on_401:
                # Token expired, try to reconnect
                print(f"UniboFileManager: Token expired, reconnecting...")
                if self._reconnect():
                    # Retry request with new token
                    return self._make_request(url, method, data, headers, timeout, retry_on_401=False)
            if e.code != 404:
                print(f"UniboFileManager: HTTP error {e.code}: {e.reason}")
            return None
        except URLError as e:
            print(f"UniboFileManager: URL error: {e.reason}")
            return None
        except Exception as e:
            print(f"UniboFileManager: Request error: {e}")
            return None

    def _reconnect(self) -> bool:
        """Reconnect and refresh the JWT token"""
        self._token = None
        self._connected = False
        return self.connect()

    def _json_request(self, url: str, method: str = 'GET', json_data: dict = None,
                      params: dict = None) -> Optional[dict]:
        """Make a JSON request and return parsed response"""
        if params:
            url = f"{url}?{urlencode(params)}"

        headers = {'Content-Type': 'application/json'}
        data = json.dumps(json_data).encode('utf-8') if json_data else None

        response = self._make_request(url, method=method, data=data, headers=headers)
        if response:
            try:
                return json.loads(response.decode('utf-8'))
            except json.JSONDecodeError:
                return None
        return None

    def connect(self) -> bool:
        """
        Authenticate with the File Manager API.

        Returns:
            True if authentication successful
        """
        try:
            username = self.credentials.get('username')
            password = self.credentials.get('password')

            if not username or not password:
                print("UniboFileManager: Missing username or password")
                self._connected = False
                return False

            # Authenticate to get JWT token
            login_url = f"{self.api_base}auth/login"
            response = self._json_request(login_url, method='POST',
                                          json_data={'username': username, 'password': password})

            if response and 'access_token' in response:
                self._token = response.get('access_token')
                self._connected = True

                # Resolve project and folder IDs
                if self.project_code:
                    self._resolve_project_id()
                    if self._project_id and self.folder_path:
                        self._resolve_folder_id()

                return True
            else:
                print("UniboFileManager: Login failed - no access token received")
                self._connected = False
                return False

        except Exception as e:
            print(f"UniboFileManager: Connection error: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Close connection"""
        self._token = None
        self._connected = False
        self._project_id = None
        self._folder_id = None

    def _resolve_project_id(self) -> Optional[int]:
        """Resolve project code to project ID"""
        if not self.project_code:
            return None

        try:
            # List projects and find by code/name
            url = f"{self.api_base}projects"
            projects = self._json_request(url)

            if projects:
                for project in projects:
                    if project.get('code') == self.project_code or project.get('name') == self.project_code:
                        self._project_id = project.get('id')
                        return self._project_id

            print(f"UniboFileManager: Project '{self.project_code}' not found")
            return None

        except Exception as e:
            print(f"UniboFileManager: Error resolving project: {e}")
            return None

    def _resolve_folder_id(self, folder_path: str = None) -> Optional[int]:
        """Resolve folder path to folder ID"""
        if not self._project_id:
            return None

        path = folder_path or self.folder_path
        if not path:
            return None

        try:
            # Navigate through folder hierarchy
            parts = path.strip('/').split('/')
            current_parent_id = None

            for folder_name in parts:
                if not folder_name:
                    continue

                # List folders at current level
                url = f"{self.api_base}projects/{self._project_id}/folders"
                params = {}
                if current_parent_id:
                    params['parent_id'] = current_parent_id

                folders = self._json_request(url, params=params)

                if folders:
                    found = False
                    for folder in folders:
                        if folder.get('name') == folder_name:
                            current_parent_id = folder.get('id')
                            found = True
                            break

                    if not found:
                        print(f"UniboFileManager: Folder '{folder_name}' not found in path")
                        return None
                else:
                    print(f"UniboFileManager: Error listing folders")
                    return None

            self._folder_id = current_parent_id
            return self._folder_id

        except Exception as e:
            print(f"UniboFileManager: Error resolving folder: {e}")
            return None

    def _get_folder_contents(self, folder_id: int = None) -> dict:
        """Get folder contents (files and subfolders)"""
        if not self._project_id:
            return {'folders': [], 'files': []}

        fid = folder_id or self._folder_id

        try:
            result = {'folders': [], 'files': []}

            # Get subfolders
            url = f"{self.api_base}projects/{self._project_id}/folders"
            params = {}
            if fid:
                params['parent_id'] = fid

            folders = self._json_request(url, params=params)
            if folders:
                result['folders'] = folders

            # Get files
            url = f"{self.api_base}projects/{self._project_id}/files"
            params = {}
            if fid:
                params['folder_id'] = fid

            files = self._json_request(url, params=params)
            if files:
                result['files'] = files

            return result

        except Exception as e:
            print(f"UniboFileManager: Error getting folder contents: {e}")
            return {'folders': [], 'files': []}

    def _find_file_by_name(self, filename: str, folder_id: int = None) -> Optional[dict]:
        """Find a file by name in the specified folder"""
        contents = self._get_folder_contents(folder_id)

        for file_info in contents.get('files', []):
            orig_filename = file_info.get('original_filename', '')

            # Direct match
            if orig_filename == filename:
                return file_info

            # Match by basename only (API may return full path as original_filename)
            if orig_filename.endswith('/' + filename) or os.path.basename(orig_filename) == filename:
                return file_info

        return None

    def read(self, filename: str) -> Optional[bytes]:
        """
        Read a file from the File Manager.

        Args:
            filename: Filename (relative to base folder)

        Returns:
            File contents as bytes, or None
        """
        if not self._project_id:
            print(f"UniboFileManager: No project_id set")
            return None

        try:
            # Handle paths with subdirectories
            if '/' in filename:
                parts = filename.rsplit('/', 1)
                subfolder_path = parts[0]
                actual_filename = parts[1]

                # Resolve subfolder
                full_path = f"{self.folder_path}/{subfolder_path}" if self.folder_path else subfolder_path
                print(f"UniboFileManager DEBUG: Resolving folder path: {full_path}")
                subfolder_id = self._resolve_folder_id(full_path)
                print(f"UniboFileManager DEBUG: Resolved folder_id: {subfolder_id}")

                if subfolder_id is None:
                    print(f"UniboFileManager: Could not resolve folder: {full_path}")
                    return None

                print(f"UniboFileManager DEBUG: Looking for file: {actual_filename} in folder_id: {subfolder_id}")
                file_info = self._find_file_by_name(actual_filename, subfolder_id)

                # Debug: list files in folder if not found
                if not file_info:
                    contents = self._get_folder_contents(subfolder_id)
                    files_list = [f.get('original_filename', 'unknown') for f in contents.get('files', [])[:5]]
                    print(f"UniboFileManager DEBUG: Files in folder (first 5): {files_list}")
            else:
                file_info = self._find_file_by_name(filename, self._folder_id)

            if not file_info:
                print(f"UniboFileManager: File not found: {filename}")
                return None

            # Download file
            file_id = file_info.get('id')
            download_url = f"{self.api_base}files/{file_id}/download"
            print(f"UniboFileManager DEBUG: Downloading from: {download_url}")

            return self._make_request(download_url, timeout=self.DEFAULT_TIMEOUT * 2)

        except Exception as e:
            print(f"UniboFileManager: Error reading file: {e}")
            import traceback
            traceback.print_exc()
            return None

    def write(self, filename: str, data: Union[bytes, BinaryIO]) -> bool:
        """
        Upload a file to the File Manager (not fully implemented).

        Args:
            filename: Filename
            data: File contents

        Returns:
            True if successful
        """
        # Note: File upload requires multipart form data which is complex with urllib
        # For now, return False - this can be implemented if needed
        print("UniboFileManager: Write operation not implemented for urllib backend")
        return False

    def exists(self, filename: str) -> bool:
        """
        Check if a file exists.

        Args:
            filename: Filename

        Returns:
            True if file exists
        """
        if not self._project_id:
            return False

        file_info = self._find_file_by_name(filename, self._folder_id)
        return file_info is not None

    def delete(self, filename: str) -> bool:
        """
        Delete a file (not implemented for safety).

        Args:
            filename: Filename

        Returns:
            False (not implemented)
        """
        print("UniboFileManager: Delete operation not implemented for safety")
        return False

    def list(self, path: str = "") -> List[StorageFile]:
        """
        List files in a directory.

        Args:
            path: Subpath (relative to base folder)

        Returns:
            List of StorageFile objects
        """
        if not self._project_id:
            return []

        files = []

        try:
            # Determine folder ID
            if path:
                full_path = f"{self.folder_path}/{path}" if self.folder_path else path
                folder_id = self._resolve_folder_id(full_path)
            else:
                folder_id = self._folder_id

            contents = self._get_folder_contents(folder_id)

            # Add folders
            for folder in contents.get('folders', []):
                folder_name = folder.get('name', '')
                files.append(StorageFile(
                    name=folder_name,
                    path=f"{path}/{folder_name}" if path else folder_name,
                    size=0,
                    modified=folder.get('created_at'),
                    is_directory=True,
                    mime_type=None,
                    url=None
                ))

            # Add files
            for file_info in contents.get('files', []):
                filename = file_info.get('original_filename', '')
                file_id = file_info.get('id')
                files.append(StorageFile(
                    name=filename,
                    path=f"{path}/{filename}" if path else filename,
                    size=file_info.get('file_size', 0),
                    modified=file_info.get('created_at'),
                    is_directory=False,
                    mime_type=file_info.get('mime_type'),
                    url=f"{self.api_base}files/{file_id}/download"
                ))

        except Exception as e:
            print(f"UniboFileManager: Error listing files: {e}")

        return files

    def get_url(self, filename: str) -> Optional[str]:
        """
        Get the download URL for a file.

        Args:
            filename: Filename

        Returns:
            Download URL string
        """
        if not self._project_id:
            return None

        file_info = self._find_file_by_name(filename, self._folder_id)
        if file_info:
            file_id = file_info.get('id')
            return f"{self.api_base}files/{file_id}/download"

        return None

    def download_to_file(self, filename: str, local_path: str) -> bool:
        """
        Download a file directly to local disk.

        Args:
            filename: Remote filename
            local_path: Local file path to save to

        Returns:
            True if successful
        """
        try:
            data = self.read(filename)
            if data is None:
                return False

            # Ensure parent directory exists
            parent_dir = os.path.dirname(local_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            with open(local_path, 'wb') as f:
                f.write(data)

            return True

        except Exception as e:
            print(f"UniboFileManager: Error downloading file: {e}")
            return False

    def get_thumbnail_url(self, filename: str, width: int = 150, height: int = 150) -> Optional[str]:
        """
        Get thumbnail URL.

        Args:
            filename: Filename
            width: Thumbnail width
            height: Thumbnail height

        Returns:
            Thumbnail URL or full file URL
        """
        return self.get_url(filename)

    def search_files(self, query: str) -> List[StorageFile]:
        """
        Search for files by name or description.

        Args:
            query: Search query

        Returns:
            List of matching files
        """
        if not self._project_id:
            return []

        files = []

        try:
            url = f"{self.api_base}search"
            params = {
                'q': query,
                'project_id': self._project_id
            }

            results = self._json_request(url, params=params)

            if results:
                for file_info in results:
                    files.append(StorageFile(
                        name=file_info.get('original_filename', ''),
                        path=file_info.get('storage_path', ''),
                        size=file_info.get('file_size', 0),
                        modified=file_info.get('created_at'),
                        is_directory=False,
                        mime_type=file_info.get('mime_type'),
                        url=f"{self.api_base}files/{file_info.get('id')}/download"
                    ))

        except Exception as e:
            print(f"UniboFileManager: Error searching files: {e}")

        return files
