# modules/utility/remote_image_loader.py

## Overview

This file contains 26 documented elements.

## Classes

### RemoteImageLoader

Loads images from local paths or remote URLs.

Caches downloaded images in memory to avoid repeated downloads.
Uses the storage module for authenticated requests.

#### Methods

##### set_storage_credentials(cls, credentials)

Set credentials for HTTP storage backend.

Args:
    credentials: Dict with 'api_key', 'username', 'password', etc.

##### set_unibo_credentials(cls, credentials)

Set credentials for Unibo File Manager backend.

Args:
    credentials: Dict with 'server_url', 'username', 'password'

##### is_remote_url(cls, path)

Check if a path is a remote URL (HTTP, HTTPS, Cloudinary, or Unibo).

Args:
    path: File path or URL

Returns:
    True if path is a remote URL

##### is_unibo_path(cls, path)

Check if a path is a Unibo File Manager path.

Args:
    path: File path or URL

Returns:
    True if path starts with unibo://

##### is_cloudinary_path(cls, path)

Check if a path is a Cloudinary path.

Args:
    path: File path or URL

Returns:
    True if path starts with cloudinary://

##### cloudinary_to_url(cls, cloudinary_path)

Convert a cloudinary:// path to a full HTTPS URL.

Format: cloudinary://folder/subfolder/filename
Result: https://res.cloudinary.com/{cloud_name}/image/upload/folder/subfolder/filename

Note: Removes '_thumb' from filename as Cloudinary stores files without this suffix.

Args:
    cloudinary_path: Path starting with cloudinary://

Returns:
    Full HTTPS URL to the image on Cloudinary

##### clear_cache(cls)

Clear the image cache.

##### load_pixmap(cls, path)

Load an image as QPixmap from local path, remote URL, Cloudinary, or Unibo path.

Args:
    path: Local file path, HTTP/HTTPS URL, cloudinary://, or unibo:// path

Returns:
    QPixmap (may be null if loading failed)

##### load_icon(cls, path)

Load an image as QIcon from local path or remote URL.

Args:
    path: Local file path or remote URL

Returns:
    QIcon (may be null if loading failed)

##### load_icon_with_fallback(cls, path, fallback_icon)

Load an icon with a fallback if loading fails.

Args:
    path: Local file path or remote URL
    fallback_icon: Path to fallback icon (optional)

Returns:
    QIcon

##### get_image_path(cls, base_path, filename)

Construct full image path, handling local, HTTP, and Cloudinary paths.

Args:
    base_path: Base directory path, URL, or cloudinary:// path
    filename: Filename to append (can also be a full URL)

Returns:
    Full path or URL

## Functions

### load_icon(path)

Load icon from local path or remote URL.

**Parameters:**
- `path: str`

**Returns:** `QIcon`

### load_pixmap(path)

Load pixmap from local path or remote URL.

**Parameters:**
- `path: str`

**Returns:** `QPixmap`

### is_remote_url(path)

Check if path is a remote URL (HTTP, HTTPS, or Cloudinary).

**Parameters:**
- `path: str`

**Returns:** `bool`

### is_cloudinary_path(path)

Check if path is a Cloudinary path.

**Parameters:**
- `path: str`

**Returns:** `bool`

### is_unibo_path(path)

Check if path is a Unibo File Manager path.

**Parameters:**
- `path: str`

**Returns:** `bool`

### cloudinary_to_url(cloudinary_path)

Convert cloudinary:// path to HTTPS URL.

**Parameters:**
- `cloudinary_path: str`

**Returns:** `str`

### get_image_path(base_path, filename)

Construct full image path.

**Parameters:**
- `base_path: str`
- `filename: str`

**Returns:** `str`

### set_storage_credentials(credentials)

Set credentials for remote storage access.

**Parameters:**
- `credentials: dict`

### set_unibo_credentials(credentials)

Set credentials for Unibo File Manager access.

**Parameters:**
- `credentials: dict`

### load_unibo_credentials_from_qgis()

Load Unibo File Manager credentials from QGIS settings.

Call this function once when the plugin initializes to enable
authenticated access to Unibo File Manager storage.

### load_credentials_from_qgis()

Load storage credentials from QGIS settings.

Call this function once when the plugin initializes to enable
authenticated access to remote storage.

### initialize()

Initialize the remote image loader with credentials from QGIS settings.

This should be called once when the plugin loads.

### join_path(base_path)

Join path components correctly for both local and remote paths.

For remote paths (unibo://, http://, https://, cloudinary://),
uses forward slash. For local paths, uses os.path.join.

Args:
    base_path: Base path (local or remote URL)
    *parts: Additional path components to join

Returns:
    Joined path

Example:
    join_path('unibo://project', 'folder', 'file.jpg')
    # Returns: 'unibo://project/folder/file.jpg'

    join_path('/local/path', 'folder', 'file.jpg')
    # Returns: '/local/path/folder/file.jpg' (OS-appropriate)

**Parameters:**
- `base_path: str`

**Returns:** `str`

