# modules/utility/pyarchinit_media_utility.py

## Overview

This file contains 23 documented elements.

## Classes

### CloudinarySync

Utility class for syncing media files to Cloudinary CDN.
Supports automatic upload, AI tagging, and URL generation.

#### Methods

##### get_instance(cls)

Get the singleton instance.

##### __init__(self)

Initialize Cloudinary sync.

##### is_enabled(self)

Check if Cloudinary sync is enabled.

##### get_backend(self)

Get the Cloudinary backend instance.

##### sync_file(self, local_path, cloudinary_folder, auto_tag)

Sync a local file to Cloudinary.

Args:
    local_path: Path to the local file
    cloudinary_folder: Optional subfolder in Cloudinary (relative to base folder)
    auto_tag: Override auto-tagging setting (None uses default from settings)

Returns:
    dict with 'success', 'url', and optionally 'tags'

##### sync_thumbnail(self, local_path, entity_type, entity_id)

Sync a thumbnail to Cloudinary with appropriate organization.

Args:
    local_path: Path to the local thumbnail
    entity_type: Type of entity (e.g., 'us', 'pottery', 'media')
    entity_id: Optional entity ID for organization

Returns:
    dict with sync result

##### delete_file(self, remote_path)

Delete a file from Cloudinary.

Args:
    remote_path: Path to the file in Cloudinary (relative to base folder)

Returns:
    bool: True if deletion successful

##### get_optimized_url(self, remote_path, width, height, quality)

Get an optimized URL for a Cloudinary file.

Args:
    remote_path: Path to the file in Cloudinary
    width: Target width (optional)
    height: Target height (optional)
    quality: Quality setting ('auto', 'auto:best', etc.)

Returns:
    Optimized URL string or None

##### get_thumbnail_url(self, remote_path, size)

Get a thumbnail URL for a Cloudinary file.

Args:
    remote_path: Path to the file in Cloudinary
    size: Thumbnail size (default 150)

Returns:
    Thumbnail URL string or None

##### get_ai_tags(self, remote_path)

Get AI-generated tags for an image.

Args:
    remote_path: Path to the image in Cloudinary

Returns:
    List of tag strings or empty list

##### extract_text(self, remote_path)

Extract text from an image using OCR.

Args:
    remote_path: Path to the image in Cloudinary

Returns:
    Extracted text or None

### Media_utility

Media utility class for creating thumbnails.
Supports both local filesystem and remote storage backends.

Usage:
    m = Media_utility()
    # Local path (backward compatible)
    m.resample_images(1, '/path/to/image.jpg', 'image.jpg', '/path/to/thumbs/', '.jpg')
    # Remote storage
    m.resample_images(1, 'gdrive://images/image.jpg', 'image.jpg', 'gdrive://thumbs/', '.jpg')

**Inherits from**: object

#### Methods

##### resample_images(self, mid, ip, i, o, ts)

Create a thumbnail from an image.

Args:
    mid: Maximum number ID for output filename
    ip: Input path (local or remote)
    i: Input filename
    o: Output path (local or remote)
    ts: Thumbnail suffix

### Media_utility_resize

Media utility class for creating resized images (higher resolution).
Supports both local filesystem and remote storage backends.

**Inherits from**: object

#### Methods

##### resample_images(self, mid, ip, i, o, ts)

Create a resized image (larger than thumbnail).

Args:
    mid: Maximum number ID for output filename
    ip: Input path (local or remote)
    i: Input filename
    o: Output path (local or remote)
    ts: Thumbnail suffix

### Video_utility

Video utility class for moving video files.
Supports both local filesystem and remote storage backends.

**Inherits from**: object

#### Methods

##### resample_images(self, mid, ip, i, o, ts)

Move a video file to the output location.

Args:
    mid: Maximum number ID for output filename
    ip: Input path (local or remote)
    i: Input filename
    o: Output path (local or remote)
    ts: Suffix

### Video_utility_resize

Video utility class for copying video files.
Supports both local filesystem and remote storage backends.

**Inherits from**: object

#### Methods

##### resample_images(self, mid, ip, i, o, ts)

Copy a video file to the output location.

Args:
    mid: Maximum number ID for output filename
    ip: Input path (local or remote)
    i: Input filename
    o: Output path (local or remote)
    ts: Suffix

## Functions

### get_storage_manager()

Get or create the global StorageManager instance.

### is_remote_path(path)

Check if a path is a remote storage path.

**Parameters:**
- `path`

