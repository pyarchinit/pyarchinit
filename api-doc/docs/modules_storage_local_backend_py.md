# modules/storage/local_backend.py

## Overview

This file contains 16 documented elements.

## Classes

### LocalBackend

Local filesystem storage backend.

This is the default backend for PyArchInit, maintaining
full backward compatibility with existing local path handling.

**Inherits from**: StorageBackend

#### Methods

##### storage_type(self)

*No description available.*
**Type:** Property  
**Returns:** `StorageType`

A read-only property that returns the storage type associated with this instance. Always returns `StorageType.LOCAL`, identifying this implementation as a local storage backend.

##### connect(self)

Verify that the base path exists and is accessible.

Returns:
    True if path exists and is accessible

##### disconnect(self)

No action needed for local filesystem

##### read(self, filename)

Read a file from local storage.

Args:
    filename: Path to the file relative to base_path

Returns:
    File contents as bytes, or None if file doesn't exist

##### write(self, filename, data)

Write data to a file in local storage.

Args:
    filename: Path to the file relative to base_path
    data: File contents as bytes or file-like object

Returns:
    True if write successful, False otherwise

##### exists(self, filename)

Check if a file exists in local storage.

Args:
    filename: Path to the file relative to base_path

Returns:
    True if file exists, False otherwise

##### delete(self, filename)

Delete a file from local storage.

Args:
    filename: Path to the file relative to base_path

Returns:
    True if deletion successful, False otherwise

##### list(self, path)

List files in a directory.

Args:
    path: Path relative to base_path (empty for root)

Returns:
    List of StorageFile objects

##### get_url(self, filename)

Get a file:// URL for the file.

Args:
    filename: Path to the file relative to base_path

Returns:
    file:// URL string

##### ensure_directory(self, path)

Ensure a directory exists in local storage.

Args:
    path: Directory path relative to base_path

Returns:
    True if directory exists or was created

##### copy(self, source, destination)

Copy a file within local storage.

Args:
    source: Source file path
    destination: Destination file path

Returns:
    True if copy successful

##### move(self, source, destination)

Move a file within local storage.

Args:
    source: Source file path
    destination: Destination file path

Returns:
    True if move successful

##### get_size(self, filename)

Get the size of a file in bytes.

Args:
    filename: Path to the file relative to base_path

Returns:
    File size in bytes, or -1 if file doesn't exist

##### get_modified_time(self, filename)

Get the last modified time of a file.

Args:
    filename: Path to the file relative to base_path

Returns:
    datetime object or None if file doesn't exist

