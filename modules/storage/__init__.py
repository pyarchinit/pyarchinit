"""
PyArchInit Storage Module
=========================

A flexible storage system that supports both local and remote storage backends.

Supported backends:
- Local filesystem (default)
- Google Drive (gdrive://)
- Dropbox (dropbox://)
- Amazon S3 / Cloudflare R2 (s3://, r2://)
- WebDAV (webdav://)
- HTTP/HTTPS (http://, https://)
- SFTP (sftp://)

Usage:
    from modules.storage import StorageManager

    # Auto-detect backend from path
    storage = StorageManager()
    backend = storage.get_backend('/local/path/to/thumbnails/')
    backend = storage.get_backend('gdrive://MyFolder/thumbnails')

    # Operations
    backend.write('image.jpg', image_bytes)
    data = backend.read('image.jpg')
    exists = backend.exists('image.jpg')
    backend.delete('image.jpg')
    files = backend.list('subfolder/')

    # With credentials manager
    from modules.storage import CredentialsManager
    creds_manager = CredentialsManager()
    storage = StorageManager(credentials_manager=creds_manager)

Author: PyArchInit Team
License: GPL v2
"""

from .storage_manager import StorageManager
from .base_backend import StorageBackend, StorageType, StorageFile, StorageConfig
from .credentials import CredentialsManager, StorageCredentials
from .local_backend import LocalBackend

# Remote backends are imported lazily to avoid dependency issues
# They can be imported directly when needed:
# from modules.storage.gdrive_backend import GDriveBackend
# from modules.storage.dropbox_backend import DropboxBackend
# from modules.storage.s3_backend import S3Backend
# from modules.storage.webdav_backend import WebDAVBackend
# from modules.storage.http_backend import HTTPBackend

__all__ = [
    'StorageManager',
    'StorageBackend',
    'StorageType',
    'StorageFile',
    'StorageConfig',
    'CredentialsManager',
    'StorageCredentials',
    'LocalBackend',
]
__version__ = '1.0.0'
