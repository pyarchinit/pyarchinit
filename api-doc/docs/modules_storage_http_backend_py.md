# modules/storage/http_backend.py

## Overview

This file contains 14 documented elements.

## Classes

### HTTPBackend

HTTP/HTTPS storage backend.

Primarily for read operations. Write/delete operations may be supported
if the server implements them (e.g., via PUT/DELETE methods).

**Inherits from**: StorageBackend

#### Methods

##### storage_type(self)

*No description available.*
**Type:** `property`  
**Returns:** `StorageType`

A read-only property that returns the storage type identifier for this backend. Always returns `StorageType.HTTP`, indicating that this instance represents an HTTP-based storage backend.

##### __init__(self, base_path, credentials)

Initialize HTTP backend.

Args:
    base_path: Base URL (e.g., "https://example.com/files/")
    credentials: Dict with username/password or bearer_token

##### connect(self)

Initialize HTTP session.

Returns:
    True if connection successful

##### disconnect(self)

Close HTTP session

##### read(self, filename)

Read a file via HTTP GET.

Args:
    filename: Path to the file relative to base URL

Returns:
    File contents as bytes, or None

##### write(self, filename, data)

Write a file via HTTP PUT (if supported by server).

Args:
    filename: Path to the file relative to base URL
    data: File contents as bytes or file-like object

Returns:
    True if successful

##### exists(self, filename)

Check if a file exists via HTTP HEAD.

Args:
    filename: Path to the file relative to base URL

Returns:
    True if file exists (HTTP 200 or 204)

##### delete(self, filename)

Delete a file via HTTP DELETE (if supported by server).

Args:
    filename: Path to the file relative to base URL

Returns:
    True if deletion successful

##### list(self, path)

List files (limited support - depends on server).

Most HTTP servers don't support directory listing.
This method attempts to parse Apache/Nginx directory index pages.

Args:
    path: Path relative to base URL

Returns:
    List of StorageFile objects (may be empty)

##### get_url(self, filename)

Get the full URL for a file.

Args:
    filename: Path to the file relative to base URL

Returns:
    Full URL string

##### get_size(self, filename)

Get the size of a file via HTTP HEAD Content-Length.

Args:
    filename: Path to the file relative to base URL

Returns:
    File size in bytes, or -1 if not available

##### download_to_file(self, filename, local_path)

Download a file directly to local disk (streaming).

Args:
    filename: Path to the file relative to base URL
    local_path: Local file path to save to

Returns:
    True if successful

