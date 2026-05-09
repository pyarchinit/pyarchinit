# modules/storage/webdav_backend.py

## Overview

This file contains 16 documented elements.

## Classes

### WebDAVBackend

WebDAV storage backend.

Uses webdavclient3 for WebDAV operations.
Compatible with Nextcloud, ownCloud, and other WebDAV servers.

**Inherits from**: StorageBackend

#### Methods

##### storage_type(self)

*No description available.*
**Type:** `property`  
**Returns:** `StorageType`

Returns the storage type identifier for this backend. This property always returns `StorageType.WEBDAV`, identifying the backend as a WebDAV storage implementation. It provides a consistent way to determine the storage type at runtime without inspecting the class directly.

##### __init__(self, base_path, credentials)

Initialize WebDAV backend.

Args:
    base_path: WebDAV server URL (e.g., "https://cloud.example.com/remote.php/dav/files/user")
    credentials: Dict with username and password

##### connect(self)

Establish connection to WebDAV server.

Returns:
    True if connection successful

##### disconnect(self)

Close connection to WebDAV server

##### read(self, filename)

Read a file from WebDAV server.

Args:
    filename: Path to the file relative to base path

Returns:
    File contents as bytes, or None

##### write(self, filename, data)

Write a file to WebDAV server.

Args:
    filename: Path to the file relative to base path
    data: File contents as bytes or file-like object

Returns:
    True if successful

##### exists(self, filename)

Check if a file exists on WebDAV server.

Args:
    filename: Path to the file relative to base path

Returns:
    True if file exists

##### delete(self, filename)

Delete a file from WebDAV server.

Args:
    filename: Path to the file relative to base path

Returns:
    True if deletion successful

##### list(self, path)

List files in a directory.

Args:
    path: Path relative to base path

Returns:
    List of StorageFile objects

##### get_url(self, filename)

Get the full URL for a file.

Args:
    filename: Path to the file relative to base path

Returns:
    Full URL to the file

##### ensure_directory(self, path)

Ensure a directory exists on WebDAV server.

Args:
    path: Directory path relative to base path

Returns:
    True if directory exists or was created

##### copy(self, source, destination)

Copy a file on WebDAV server.

Args:
    source: Source file path
    destination: Destination file path

Returns:
    True if copy successful

##### move(self, source, destination)

Move a file on WebDAV server.

Args:
    source: Source file path
    destination: Destination file path

Returns:
    True if move successful

##### get_size(self, filename)

Get the size of a file in bytes.

Args:
    filename: Path to the file relative to base path

Returns:
    File size in bytes, or -1 if file doesn't exist

