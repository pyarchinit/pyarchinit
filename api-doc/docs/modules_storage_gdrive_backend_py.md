# modules/storage/gdrive_backend.py

## Overview

This file contains 14 documented elements.

## Classes

### GDriveBackend

Google Drive storage backend.

Uses the Google Drive API v3 for file operations.
Supports folder hierarchy and file sharing.

**Inherits from**: StorageBackend

#### Methods

##### storage_type(self)

*No description available.*
**Type:** `property`  
**Returns:** `StorageType`

A read-only property that identifies the storage backend type. Returns `StorageType.GOOGLE_DRIVE`, indicating that this backend implementation is backed by Google Drive.

##### __init__(self, base_path, credentials)

Initialize Google Drive backend.

Args:
    base_path: Root folder name/ID in Google Drive
    credentials: Dict with client_id, client_secret, refresh_token

##### connect(self)

Establish connection to Google Drive API.

Returns:
    True if connection successful

##### disconnect(self)

Close connection to Google Drive

##### read(self, filename)

Read a file from Google Drive.

Args:
    filename: Path to the file relative to base folder

Returns:
    File contents as bytes, or None

##### write(self, filename, data)

Write a file to Google Drive.

Args:
    filename: Path to the file relative to base folder
    data: File contents as bytes or file-like object

Returns:
    True if successful

##### exists(self, filename)

Check if a file exists in Google Drive.

Args:
    filename: Path to the file relative to base folder

Returns:
    True if file exists

##### delete(self, filename)

Delete a file from Google Drive (moves to trash).

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

Get a shareable URL for the file.

Args:
    filename: Path to the file relative to base folder

Returns:
    Web view URL or None

##### get_direct_url(self, filename)

Get a direct download URL for the file.

Note: Requires the file to be shared publicly or with anyone with the link.

Args:
    filename: Path to the file relative to base folder

Returns:
    Direct download URL or None

##### share_file(self, filename, anyone_with_link)

Share a file and return the shareable link.

Args:
    filename: Path to the file
    anyone_with_link: If True, anyone with the link can view

Returns:
    Shareable URL or None

