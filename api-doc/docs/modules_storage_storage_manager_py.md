# modules/storage/storage_manager.py

## Overview

This file contains 15 documented elements.

## Classes

### StorageManager

Central manager for storage backends.

Automatically detects and instantiates the appropriate storage backend
based on the path prefix. Maintains a cache of backends for reuse.

#### Methods

##### __init__(self, credentials_manager)

Initialize the storage manager.

Args:
    credentials_manager: Optional credentials manager for remote backends

##### register_backend(cls, storage_type, backend_class)

Register a backend class for a storage type.

Args:
    storage_type: The storage type to register
    backend_class: The backend class to use

##### detect_storage_type(self, path)

Detect the storage type from a path.

Args:
    path: The path or URL to analyze

Returns:
    The detected StorageType

##### parse_path(self, path)

Parse a storage path into its components.

Args:
    path: The path or URL to parse

Returns:
    Tuple of (storage_type, base_path, relative_path)

##### get_backend(self, path, connect)

Get a storage backend for the given path.

Automatically detects the storage type and returns the appropriate
backend instance. Backends are cached for reuse.

Args:
    path: The path or URL to get a backend for
    connect: Whether to connect the backend immediately

Returns:
    A StorageBackend instance for the path

Raises:
    ValueError: If no backend is registered for the storage type

##### clear_cache(self)

Clear the backend cache and disconnect all backends

##### get_available_backends(self)

Get a list of available storage types.

Returns:
    List of StorageType values that have registered backends

##### read(self, path)

Read a file from any storage.

Args:
    path: Full path including storage prefix

Returns:
    File contents as bytes, or None

##### write(self, path, data)

Write data to any storage.

Args:
    path: Full path including storage prefix
    data: Data to write (bytes or str)

Returns:
    True if successful

##### exists(self, path)

Check if a file exists in any storage.

Args:
    path: Full path including storage prefix

Returns:
    True if file exists

##### delete(self, path)

Delete a file from any storage.

Args:
    path: Full path including storage prefix

Returns:
    True if deletion successful

##### __enter__(self)

*No description available.*
Implements the context manager protocol entry point for the class. Returns the instance itself (`self`), allowing the object to be used directly within a `with` statement block. No additional setup or resource acquisition is performed upon entry.

##### __exit__(self, exc_type, exc_val, exc_tb)

*No description available.*
Context manager exit method called upon leaving a `with` block. Invokes `self.clear_cache()` unconditionally, regardless of whether an exception occurred. Returns `False`, indicating that any exception raised within the `with` block is not suppressed.

