# modules/storage/dropbox_backend.py

## Overview

This file contains 15 documented elements.

## Classes

### DropboxBackend

Dropbox storage backend.

Uses the Dropbox API v2 for file operations.

**Inherits from**: StorageBackend

#### Methods

##### storage_type(self)

*No description available.*
**Signature:** `@property def storage_type(self) -> StorageType`

A read-only property that identifies the storage backend type. Returns `StorageType.DROPBOX`, indicating that this backend implementation is associated with Dropbox. This property provides a consistent interface for querying the storage type across different backend implementations.

##### __init__(self, base_path, credentials)

Initialize Dropbox backend.

Args:
    base_path: Root folder path in Dropbox (e.g., "/PyArchInit")
    credentials: Dict with access_token or refresh_token + app_key + app_secret

##### connect(self)

Establish connection to Dropbox API.

Returns:
    True if connection successful

##### disconnect(self)

Close connection to Dropbox

##### read(self, filename)

Read a file from Dropbox.

Args:
    filename: Path to the file relative to base folder

Returns:
    File contents as bytes, or None

##### write(self, filename, data)

Write a file to Dropbox.

Args:
    filename: Path to the file relative to base folder
    data: File contents as bytes or file-like object

Returns:
    True if successful

##### exists(self, filename)

Check if a file exists in Dropbox.

Args:
    filename: Path to the file relative to base folder

Returns:
    True if file exists

##### delete(self, filename)

Delete a file from Dropbox.

Args:
    filename: Path to the file relative to base folder

Returns:
    True if deletion successful

##### list(self, path)

List files in a folder.

Args:
    path: Path relative to base folder

Returns:
    List of StorageFile objects

##### get_url(self, filename)

Get a temporary download link for the file.

Args:
    filename: Path to the file relative to base folder

Returns:
    Temporary download URL (valid for 4 hours)

##### ensure_directory(self, path)

Ensure a directory exists in Dropbox.

Args:
    path: Directory path relative to base folder

Returns:
    True if directory exists or was created

##### get_shared_link(self, filename)

Get or create a shared link for the file.

Args:
    filename: Path to the file relative to base folder

Returns:
    Shared link URL (permanent)

##### get_size(self, filename)

Get the size of a file in bytes.

Args:
    filename: Path to the file relative to base folder

Returns:
    File size in bytes, or -1 if file doesn't exist

