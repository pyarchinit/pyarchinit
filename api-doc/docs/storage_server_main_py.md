# storage_server/main.py

## Overview

This file contains 15 documented elements.

## Classes

### FileInfo

File information model

**Inherits from**: BaseModel

## Functions

### get_api_key(x_api_key)

Validate API key if configured

**Parameters:**
- `x_api_key: Optional[str]`

**Returns:** `Optional[str]`

### get_drive_service()

Get or create Google Drive service

### get_root_folder_id()

Get the root folder ID

**Returns:** `str`

### get_or_create_folder(service, folder_name, parent_id)

Get or create a folder in Google Drive

**Parameters:**
- `service`
- `folder_name: str`
- `parent_id: str`

**Returns:** `str`

### get_folder_id_for_path(service, path)

Get folder ID for a path, creating folders as needed

**Parameters:**
- `service`
- `path: str`

**Returns:** `str`

### find_file(service, filename, parent_id)

Find a file by name in a folder

**Parameters:**
- `service`
- `filename: str`
- `parent_id: str`

**Returns:** `Optional[dict]`

### detect_mime_type(filename)

Detect MIME type from filename

**Parameters:**
- `filename: str`

**Returns:** `str`

### root()

Health check endpoint

### read_file(path, api_key)

Read a file from Google Drive.

Usage: GET /files/thumbnails/image.jpg

**Parameters:**
- `path: str`
- `api_key: str`

### write_file(path, file, api_key)

Write a file to Google Drive.

Usage: PUT /files/thumbnails/image.jpg with file in body

**Parameters:**
- `path: str`
- `file: UploadFile`
- `api_key: str`

### delete_file(path, api_key)

Delete a file from Google Drive.

Usage: DELETE /files/thumbnails/image.jpg

**Parameters:**
- `path: str`
- `api_key: str`

### list_files(path, api_key)

List files in a directory.

Usage: GET /list/thumbnails/

**Parameters:**
- `path: str`
- `api_key: str`

**Returns:** `List[FileInfo]`

### check_file(path, api_key)

Check if a file exists.

Usage: HEAD /files/thumbnails/image.jpg

**Parameters:**
- `path: str`
- `api_key: str`

