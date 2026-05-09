# modules/storage/unibo_filemanager_backend.py

## Overview

This file contains 16 documented elements.

## Classes

### UniboFileManagerBackend

Unibo File Manager storage backend.

Connects to the University of Bologna File Manager API for
reading archaeological documentation files.

**Inherits from**: StorageBackend

#### Methods

##### storage_type(self)

*No description available.*
**Type:** `property` → `StorageType`

Returns the storage type associated with this backend instance. This property always returns `StorageType.HTTP`, reflecting that the underlying storage mechanism is HTTP-based. It requires no parameters and has no side effects.

##### __init__(self, base_path, credentials)

Initialize Unibo File Manager backend.

Args:
    base_path: Project path (e.g., "Al-Khutm/KTM2025/photolog/original")
    credentials: Dict with username, password, and optionally server_url

##### connect(self)

Authenticate with the File Manager API.

Returns:
    True if authentication successful

##### disconnect(self)

Close connection

##### read(self, filename)

Read a file from the File Manager.

Args:
    filename: Filename (relative to base folder)

Returns:
    File contents as bytes, or None

##### write(self, filename, data, folder_path)

Upload a file to the File Manager.

Args:
    filename: Filename (can include subfolder path)
    data: File contents as bytes or file-like object
    folder_path: Optional folder path override

Returns:
    True if successful

##### upload_local_file(self, local_path, remote_filename)

Upload a local file to the File Manager.

Args:
    local_path: Path to local file
    remote_filename: Remote filename (defaults to local filename)

Returns:
    True if successful

##### exists(self, filename)

Check if a file exists.

Args:
    filename: Filename

Returns:
    True if file exists

##### delete(self, filename)

Delete a file (not implemented for safety).

Args:
    filename: Filename

Returns:
    False (not implemented)

##### list(self, path)

List files in a directory.

Args:
    path: Subpath (relative to base folder)

Returns:
    List of StorageFile objects

##### get_url(self, filename)

Get the download URL for a file.

Args:
    filename: Filename

Returns:
    Download URL string

##### download_to_file(self, filename, local_path)

Download a file directly to local disk.

Args:
    filename: Remote filename
    local_path: Local file path to save to

Returns:
    True if successful

##### get_thumbnail_url(self, filename, width, height)

Get thumbnail URL.

Args:
    filename: Filename
    width: Thumbnail width
    height: Thumbnail height

Returns:
    Thumbnail URL or full file URL

##### search_files(self, query)

Search for files by name or description.

Args:
    query: Search query

Returns:
    List of matching files

