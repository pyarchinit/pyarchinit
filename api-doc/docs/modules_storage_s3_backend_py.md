# modules/storage/s3_backend.py

## Overview

This file contains 18 documented elements.

## Classes

### S3Backend

Amazon S3 and Cloudflare R2 storage backend.

Uses boto3 for S3-compatible API operations.
Works with AWS S3, Cloudflare R2, MinIO, and other S3-compatible services.

**Inherits from**: StorageBackend

#### Methods

##### __init__(self, base_path, credentials)

Initialize S3/R2 backend.

Args:
    base_path: Bucket name (e.g., "my-bucket")
    credentials: Dict with access_key, secret_key, region, endpoint, account_id

##### storage_type(self)

*No description available.*
**Type:** `property`  
**Returns:** `StorageType`

Returns the storage type of the current instance as a `StorageType` enum value. Yields `StorageType.R2` if the internal `_is_r2` flag is set to `True`, otherwise yields `StorageType.S3`.

##### connect(self)

Establish connection to S3/R2.

Returns:
    True if connection successful

##### disconnect(self)

Close connection to S3/R2

##### read(self, filename)

Read a file from S3/R2.

Args:
    filename: Key (path) of the file in the bucket

Returns:
    File contents as bytes, or None

##### write(self, filename, data)

Write a file to S3/R2.

Args:
    filename: Key (path) of the file in the bucket
    data: File contents as bytes or file-like object

Returns:
    True if successful

##### exists(self, filename)

Check if a file exists in S3/R2.

Args:
    filename: Key (path) of the file in the bucket

Returns:
    True if file exists

##### delete(self, filename)

Delete a file from S3/R2.

Args:
    filename: Key (path) of the file in the bucket

Returns:
    True if deletion successful

##### list(self, path)

List files in a prefix (folder).

Args:
    path: Prefix (folder path) to list

Returns:
    List of StorageFile objects

##### get_url(self, filename)

Get a pre-signed URL for the file.

Args:
    filename: Key (path) of the file in the bucket

Returns:
    Pre-signed URL (valid for 1 hour)

##### get_public_url(self, filename)

Get the public URL for a file (if bucket is public).

Args:
    filename: Key (path) of the file in the bucket

Returns:
    Public URL (may not work if bucket is private)

##### ensure_directory(self, path)

Ensure a "directory" exists in S3/R2.

Note: S3 doesn't have real directories. This creates a zero-byte
object with a trailing slash to simulate a folder.

Args:
    path: Directory path

Returns:
    True (always succeeds for S3)

##### get_size(self, filename)

Get the size of a file in bytes.

Args:
    filename: Key (path) of the file in the bucket

Returns:
    File size in bytes, or -1 if file doesn't exist

##### copy(self, source, destination)

Copy a file within S3/R2.

Args:
    source: Source key
    destination: Destination key

Returns:
    True if copy successful

##### move(self, source, destination)

Move a file within S3/R2 (copy + delete).

Args:
    source: Source key
    destination: Destination key

Returns:
    True if move successful

##### set_public_read(self, filename)

Make a file publicly readable.

Args:
    filename: Key (path) of the file

Returns:
    True if successful

