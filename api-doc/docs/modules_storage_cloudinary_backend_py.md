# modules/storage/cloudinary_backend.py

## Overview

This file contains 25 documented elements.

## Classes

### CloudinaryAIResult

Container for Cloudinary AI analysis results

**Decorators**: dataclass

#### Methods

##### __post_init__(self)

Initializes default values for the `tags`, `objects`, `colors`, and `faces` fields after the dataclass `__init__` method has run. Any field that evaluates to `None` or another falsy value is replaced with an empty list, ensuring these attributes are always list instances rather than `None`. This prevents downstream code from encountering `None` where an iterable is expected.

### CloudinaryBackend

Cloudinary storage backend.

Uses the Cloudinary API for media management with advanced features:
- Image optimization and transformation
- AI-powered auto-tagging
- Object detection
- OCR text extraction
- Background removal
- Content-aware cropping

**Inherits from**: StorageBackend

#### Methods

##### storage_type(self)

*No description available.*
**Signature:** `storage_type -> StorageType` *(property)*

Returns the storage type identifier for this backend. This property always returns `StorageType.CLOUDINARY`, indicating that the implementing class is backed by Cloudinary storage. It provides a consistent way to identify the storage provider at runtime.

##### __init__(self, base_path, credentials)

Initialize Cloudinary backend.

Args:
    base_path: Base folder in Cloudinary (used as prefix for public_id)
    credentials: Dict with cloud_name, api_key, api_secret

##### connect(self)

Establish connection to Cloudinary API.

Returns:
    True if connection successful

##### disconnect(self)

Close connection to Cloudinary

##### read(self, filename)

Read a file from Cloudinary.

Args:
    filename: Path to the file relative to base folder

Returns:
    File contents as bytes, or None

##### write(self, filename, data, auto_tag, categorization)

Write a file to Cloudinary.

Args:
    filename: Path to the file relative to base folder
    data: File contents as bytes or file-like object
    auto_tag: Override auto-tagging setting for this upload
    categorization: List of AI categorization models to use
                  Options: 'google_tagging', 'aws_rek_tagging',
                           'imagga_tagging', 'google_video_tagging'

Returns:
    True if successful

##### write_with_ai(self, filename, data, features)

Write a file to Cloudinary with AI analysis.

Args:
    filename: Path to the file
    data: File contents
    features: List of AI features to enable:
             'auto_tagging', 'object_detection', 'ocr',
             'color_analysis', 'face_detection', 'moderation'

Returns:
    CloudinaryAIResult with AI analysis data, or None on failure

##### exists(self, filename)

Check if a file exists in Cloudinary.

Args:
    filename: Path to the file relative to base folder

Returns:
    True if file exists

##### delete(self, filename)

Delete a file from Cloudinary.

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

##### get_url(self, filename, transformation)

Get a URL for the file, optionally with transformations.

Args:
    filename: Path to the file
    transformation: Optional Cloudinary transformation string

Returns:
    URL string or None

##### get_optimized_url(self, filename, width, height, quality, format)

Get an optimized URL for the file.

Args:
    filename: Path to the file
    width: Target width (optional)
    height: Target height (optional)
    quality: Quality setting ('auto', 'auto:best', 'auto:good', 'auto:eco', 'auto:low', or 1-100)
    format: Output format ('auto', 'webp', 'jpg', 'png', etc.)

Returns:
    Optimized URL string or None

##### get_thumbnail_url(self, filename, width, height)

Get a thumbnail URL for the file.

Args:
    filename: Path to the file
    width: Thumbnail width
    height: Thumbnail height

Returns:
    Thumbnail URL or None

##### get_ai_tags(self, filename)

Get AI-generated tags for an existing image.

Args:
    filename: Path to the file

Returns:
    List of tag strings

##### get_ocr_text(self, filename)

Extract text from an image using OCR.

Args:
    filename: Path to the image file

Returns:
    Extracted text or None

##### remove_background(self, filename, output_filename)

Remove the background from an image.

Args:
    filename: Path to the source image
    output_filename: Path for the output (optional, modifies in place if not provided)

Returns:
    URL of the processed image or None

##### add_tags(self, filename, tags)

Add tags to a file.

Args:
    filename: Path to the file
    tags: List of tags to add

Returns:
    True if successful

##### remove_tags(self, filename, tags)

Remove tags from a file.

Args:
    filename: Path to the file
    tags: List of tags to remove

Returns:
    True if successful

##### search(self, query, max_results)

Search for files using Cloudinary's search API.

Args:
    query: Search query (supports Cloudinary search syntax)
    max_results: Maximum number of results

Returns:
    List of matching StorageFile objects

##### search_by_tags(self, tags, match_all, max_results)

Search for files by tags.

Args:
    tags: List of tags to search for
    match_all: If True, files must have all tags; if False, any tag matches
    max_results: Maximum number of results

Returns:
    List of matching StorageFile objects

##### get_usage_stats(self)

Get Cloudinary account usage statistics.

Returns:
    Dictionary with usage stats or None

