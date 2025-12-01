"""
PyArchInit Storage Proxy Server
================================

A simple FastAPI server that acts as a proxy to Google Drive (Service Account).
Deploy on Railway, Render, or any cloud platform.

Users only need the HTTP URL - no credentials configuration needed!

Environment Variables:
    - GOOGLE_SERVICE_ACCOUNT_JSON: The full JSON content of the service account key
    - API_KEY: Optional API key for authentication
    - GDRIVE_ROOT_FOLDER_ID: Optional root folder ID in Google Drive

Usage in PyArchInit:
    Thumbnail path: https://your-server.railway.app/files/thumbnails/
    Resize path: https://your-server.railway.app/files/resize/

Author: PyArchInit Team
License: GPL v2
"""

import os
import io
import json
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File, Query
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

app = FastAPI(
    title="PyArchInit Storage Proxy",
    description="Proxy server for PyArchInit remote media storage",
    version="1.0.0"
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Drive settings
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'

# Cache for folder IDs
_folder_cache = {}
_drive_service = None


class FileInfo(BaseModel):
    """File information model"""
    name: str
    path: str
    size: int = 0
    modified: Optional[str] = None
    is_directory: bool = False
    mime_type: Optional[str] = None
    url: Optional[str] = None


def get_api_key(x_api_key: Optional[str] = Header(None)) -> Optional[str]:
    """Validate API key if configured"""
    required_key = os.environ.get('API_KEY')
    if required_key:
        if x_api_key != required_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


def get_drive_service():
    """Get or create Google Drive service"""
    global _drive_service

    if _drive_service is not None:
        return _drive_service

    # Get service account JSON from environment
    # Supports both plain JSON and Base64 encoded JSON
    sa_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not sa_json:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_SERVICE_ACCOUNT_JSON environment variable not set"
        )

    try:
        import base64

        # Try to decode as Base64 first
        try:
            decoded = base64.b64decode(sa_json).decode('utf-8')
            sa_info = json.loads(decoded)
        except:
            # Not Base64, try as plain JSON
            # Fix escaped newlines in private key (Railway may escape them)
            sa_json_fixed = sa_json.replace('\\\\n', '\n')

            # Try parsing
            try:
                sa_info = json.loads(sa_json_fixed)
            except:
                # Try replacing \n with actual newlines
                sa_json_fixed = sa_json.replace('\\n', '\n')
                sa_info = json.loads(sa_json_fixed)

        # Ensure private_key has actual newlines
        if 'private_key' in sa_info:
            pk = sa_info['private_key']
            if '\\n' in pk:
                sa_info['private_key'] = pk.replace('\\n', '\n')

        credentials = service_account.Credentials.from_service_account_info(
            sa_info, scopes=SCOPES
        )
        _drive_service = build('drive', 'v3', credentials=credentials)
        return _drive_service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Google Drive: {str(e)}")


def get_root_folder_id() -> str:
    """Get the root folder ID"""
    folder_id = os.environ.get('GDRIVE_ROOT_FOLDER_ID')
    if folder_id:
        return folder_id
    return 'root'


def get_or_create_folder(service, folder_name: str, parent_id: str) -> str:
    """Get or create a folder in Google Drive"""
    cache_key = f"{parent_id}/{folder_name}"

    if cache_key in _folder_cache:
        return _folder_cache[cache_key]

    # Search for existing folder
    query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='{FOLDER_MIME_TYPE}' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = results.get('files', [])

    if files:
        folder_id = files[0]['id']
    else:
        # Create new folder
        file_metadata = {
            'name': folder_name,
            'mimeType': FOLDER_MIME_TYPE,
            'parents': [parent_id]
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        folder_id = folder.get('id')

    _folder_cache[cache_key] = folder_id
    return folder_id


def get_folder_id_for_path(service, path: str) -> str:
    """Get folder ID for a path, creating folders as needed"""
    if not path or path == '/':
        return get_root_folder_id()

    parts = path.strip('/').split('/')
    current_parent = get_root_folder_id()

    for part in parts:
        if part:
            current_parent = get_or_create_folder(service, part, current_parent)

    return current_parent


def find_file(service, filename: str, parent_id: str) -> Optional[dict]:
    """Find a file by name in a folder"""
    query = f"name='{filename}' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, size, mimeType, modifiedTime, webViewLink, webContentLink)'
    ).execute()
    files = results.get('files', [])
    return files[0] if files else None


def detect_mime_type(filename: str) -> str:
    """Detect MIME type from filename"""
    ext = os.path.splitext(filename)[1].lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.tif': 'image/tiff',
        '.tiff': 'image/tiff',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp',
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.json': 'application/json',
        '.xml': 'application/xml',
    }
    return mime_types.get(ext, 'application/octet-stream')


# ============== API Endpoints ==============

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "PyArchInit Storage Proxy",
        "status": "running",
        "version": "1.0.0",
        "backend": "Google Drive (Service Account)"
    }


@app.get("/files/{path:path}")
async def read_file(path: str, api_key: str = Depends(get_api_key)):
    """
    Read a file from Google Drive.

    Usage: GET /files/thumbnails/image.jpg
    """
    service = get_drive_service()

    # Split path into directory and filename
    path = path.strip('/')
    if '/' in path:
        dir_path = '/'.join(path.split('/')[:-1])
        filename = path.split('/')[-1]
    else:
        dir_path = ''
        filename = path

    # Get folder ID
    folder_id = get_folder_id_for_path(service, dir_path)

    # Find the file
    file_info = find_file(service, filename, folder_id)
    if not file_info:
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    # Download the file
    request = service.files().get_media(fileId=file_info['id'])
    file_buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(file_buffer, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    file_buffer.seek(0)

    # Return as streaming response
    return StreamingResponse(
        file_buffer,
        media_type=file_info.get('mimeType', 'application/octet-stream'),
        headers={
            'Content-Disposition': f'inline; filename="{filename}"'
        }
    )


@app.put("/files/{path:path}")
async def write_file(
    path: str,
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    """
    Write a file to Google Drive.

    Usage: PUT /files/thumbnails/image.jpg with file in body
    """
    service = get_drive_service()

    # Split path into directory and filename
    path = path.strip('/')
    if '/' in path:
        dir_path = '/'.join(path.split('/')[:-1])
        filename = path.split('/')[-1]
    else:
        dir_path = ''
        filename = path

    # Get or create folder
    folder_id = get_folder_id_for_path(service, dir_path)

    # Read file content
    content = await file.read()
    file_buffer = io.BytesIO(content)

    # Detect MIME type
    mime_type = file.content_type or detect_mime_type(filename)

    # Check if file exists
    existing_file = find_file(service, filename, folder_id)

    media = MediaIoBaseUpload(file_buffer, mimetype=mime_type, resumable=True)

    if existing_file:
        # Update existing file
        service.files().update(
            fileId=existing_file['id'],
            media_body=media
        ).execute()
    else:
        # Create new file
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

    return {"status": "success", "path": path}


@app.delete("/files/{path:path}")
async def delete_file(path: str, api_key: str = Depends(get_api_key)):
    """
    Delete a file from Google Drive.

    Usage: DELETE /files/thumbnails/image.jpg
    """
    service = get_drive_service()

    # Split path into directory and filename
    path = path.strip('/')
    if '/' in path:
        dir_path = '/'.join(path.split('/')[:-1])
        filename = path.split('/')[-1]
    else:
        dir_path = ''
        filename = path

    # Get folder ID
    folder_id = get_folder_id_for_path(service, dir_path)

    # Find the file
    file_info = find_file(service, filename, folder_id)
    if not file_info:
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    # Move to trash
    service.files().update(
        fileId=file_info['id'],
        body={'trashed': True}
    ).execute()

    return {"status": "success", "path": path}


@app.get("/list/{path:path}")
async def list_files(
    path: str = "",
    api_key: str = Depends(get_api_key)
) -> List[FileInfo]:
    """
    List files in a directory.

    Usage: GET /list/thumbnails/
    """
    service = get_drive_service()

    # Get folder ID
    folder_id = get_folder_id_for_path(service, path.strip('/'))

    # List files
    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, size, mimeType, modifiedTime, webViewLink)',
        orderBy='name'
    ).execute()

    files = []
    for item in results.get('files', []):
        is_folder = item.get('mimeType') == FOLDER_MIME_TYPE
        file_path = f"{path.strip('/')}/{item['name']}" if path else item['name']

        files.append(FileInfo(
            name=item['name'],
            path=file_path,
            size=int(item.get('size', 0)),
            modified=item.get('modifiedTime'),
            is_directory=is_folder,
            mime_type=item.get('mimeType'),
            url=item.get('webViewLink')
        ))

    return files


@app.head("/files/{path:path}")
async def check_file(path: str, api_key: str = Depends(get_api_key)):
    """
    Check if a file exists.

    Usage: HEAD /files/thumbnails/image.jpg
    """
    service = get_drive_service()

    # Split path into directory and filename
    path = path.strip('/')
    if '/' in path:
        dir_path = '/'.join(path.split('/')[:-1])
        filename = path.split('/')[-1]
    else:
        dir_path = ''
        filename = path

    # Get folder ID
    try:
        folder_id = get_folder_id_for_path(service, dir_path)
        file_info = find_file(service, filename, folder_id)

        if file_info:
            return JSONResponse(
                content={},
                headers={
                    'Content-Length': str(file_info.get('size', 0)),
                    'Content-Type': file_info.get('mimeType', 'application/octet-stream')
                }
            )
    except:
        pass

    raise HTTPException(status_code=404, detail="File not found")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
