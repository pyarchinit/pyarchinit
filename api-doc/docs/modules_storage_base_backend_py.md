# modules/storage/base_backend.py

## Overview

This file contains 25 documented elements.

## Classes

### StorageType

Enumeration of supported storage types

**Inherits from**: Enum

### StorageFile

Represents a file in storage

**Decorators**: dataclass

#### Methods

##### __repr__(self)

Returns a string representation of the `StorageFile` instance, formatted as `StorageFile(name='<name>', size=<size>, is_dir=<is_directory>)`. The output includes the file's `name`, `size`, and `is_directory` fields. This method is automatically invoked by `repr()` and in contexts where an unambiguous string representation of the object is required.

### StorageConfig

Configuration for a storage backend

**Decorators**: dataclass

### StorageBackend

Abstract base class for storage backends.

All storage backends must implement these methods to provide
a consistent interface for file operations.

**Inherits from**: ABC

#### Methods

##### __init__(self, base_path, credentials)

Initialize the storage backend.

Args:
    base_path: The base path/URL for this storage
    credentials: Optional credentials dictionary

##### storage_type(self)

Return the type of this storage backend

##### is_remote(self)

Return True if this is a remote storage backend

##### connect(self)

Establish connection to the storage backend.

Returns:
    True if connection successful, False otherwise

##### disconnect(self)

Close connection to the storage backend

##### read(self, filename)

Read a file from storage.

Args:
    filename: Path to the file relative to base_path

Returns:
    File contents as bytes, or None if file doesn't exist

##### write(self, filename, data)

Write data to a file in storage.

Args:
    filename: Path to the file relative to base_path
    data: File contents as bytes or file-like object

Returns:
    True if write successful, False otherwise

##### exists(self, filename)

Check if a file exists in storage.

Args:
    filename: Path to the file relative to base_path

Returns:
    True if file exists, False otherwise

##### delete(self, filename)

Delete a file from storage.

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

Get a URL for accessing the file.

For local files, returns file:// URL.
For remote files, returns public/signed URL if available.

Args:
    filename: Path to the file relative to base_path

Returns:
    URL string or None if not available

##### get_full_path(self, filename)

Get the full path/URL for a file.

Args:
    filename: Path to the file relative to base_path

Returns:
    Full path string

##### ensure_directory(self, path)

Ensure a directory exists in storage.

Args:
    path: Directory path relative to base_path

Returns:
    True if directory exists or was created, False otherwise

##### copy(self, source, destination)

Copy a file within the same storage backend.

Args:
    source: Source file path
    destination: Destination file path

Returns:
    True if copy successful, False otherwise

##### move(self, source, destination)

Move a file within the same storage backend.

Args:
    source: Source file path
    destination: Destination file path

Returns:
    True if move successful, False otherwise

##### get_size(self, filename)

Get the size of a file in bytes.

Args:
    filename: Path to the file relative to base_path

Returns:
    File size in bytes, or -1 if file doesn't exist

##### __enter__(self)

Context manager entry

##### __exit__(self, exc_type, exc_val, exc_tb)

Context manager exit

##### __repr__(self)

*No description available.*
Returns an unambiguous string representation of the object. The returned string follows the format `ClassName(base_path='<value>')`, where `ClassName` is the actual class name and `<value>` is the current `base_path` attribute.

