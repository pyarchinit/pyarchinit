"""
Cloudinary Storage Backend
==========================

Storage backend for Cloudinary cloud media management.
Supports image optimization, transformations, and AI features.

Requirements:
    pip install cloudinary

Path format: cloudinary://folder/filename.jpg

Credentials required:
    - cloud_name: Cloudinary cloud name
    - api_key: Cloudinary API key
    - api_secret: Cloudinary API secret

AI Features:
    - Auto-tagging: Automatic image tagging using AI
    - Object detection: Detect objects in images
    - OCR: Extract text from images
    - Background removal: Remove image backgrounds
    - Content-aware cropping: Smart image cropping

Author: PyArchInit Team
License: GPL v2
"""

import io
import os
import json
from typing import List, Optional, Union, BinaryIO, Dict, Any
from dataclasses import dataclass

from .base_backend import StorageBackend, StorageType, StorageFile


@dataclass
class CloudinaryAIResult:
    """Container for Cloudinary AI analysis results"""
    public_id: str
    tags: List[str] = None
    objects: List[Dict[str, Any]] = None
    ocr_text: str = None
    colors: List[Dict[str, Any]] = None
    faces: List[Dict[str, Any]] = None
    moderation: Dict[str, Any] = None

    def __post_init__(self):
        self.tags = self.tags or []
        self.objects = self.objects or []
        self.colors = self.colors or []
        self.faces = self.faces or []


class CloudinaryBackend(StorageBackend):
    """
    Cloudinary storage backend.

    Uses the Cloudinary API for media management with advanced features:
    - Image optimization and transformation
    - AI-powered auto-tagging
    - Object detection
    - OCR text extraction
    - Background removal
    - Content-aware cropping
    """

    # Cloudinary resource types
    RESOURCE_IMAGE = 'image'
    RESOURCE_VIDEO = 'video'
    RESOURCE_RAW = 'raw'

    @property
    def storage_type(self) -> StorageType:
        return StorageType.CLOUDINARY

    def __init__(self, base_path: str, credentials: Optional[dict] = None):
        """
        Initialize Cloudinary backend.

        Args:
            base_path: Base folder in Cloudinary (used as prefix for public_id)
            credentials: Dict with cloud_name, api_key, api_secret
        """
        super().__init__(base_path, credentials)
        self._cloudinary = None
        self._uploader = None
        self._api = None
        self._auto_tagging = False
        self._auto_tagging_confidence = 0.6

    def connect(self) -> bool:
        """
        Establish connection to Cloudinary API.

        Returns:
            True if connection successful
        """
        try:
            import cloudinary
            import cloudinary.uploader
            import cloudinary.api

            # Get credentials
            cloud_name = self.credentials.get('cloud_name')
            api_key = self.credentials.get('api_key')
            api_secret = self.credentials.get('api_secret')

            if not all([cloud_name, api_key, api_secret]):
                return False

            # Configure Cloudinary
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True
            )

            self._cloudinary = cloudinary
            self._uploader = cloudinary.uploader
            self._api = cloudinary.api

            # Check auto-tagging setting
            auto_tagging = self.credentials.get('auto_tagging', 'false')
            self._auto_tagging = auto_tagging.lower() in ('true', '1', 'yes', 'on')

            self._connected = True
            return True

        except ImportError:
            # Cloudinary library not installed
            return False
        except Exception as e:
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Close connection to Cloudinary"""
        self._cloudinary = None
        self._uploader = None
        self._api = None
        self._connected = False

    def _get_public_id(self, filename: str) -> str:
        """
        Get the full public_id for a file.

        Args:
            filename: Relative path/filename

        Returns:
            Full public_id including base folder
        """
        # Remove file extension for public_id
        name_without_ext = os.path.splitext(filename)[0]

        if self.base_path:
            # Clean base path
            base = self.base_path.strip('/')
            return f"{base}/{name_without_ext}"
        return name_without_ext

    def _get_resource_type(self, filename: str) -> str:
        """
        Determine the Cloudinary resource type from filename.

        Args:
            filename: The filename to check

        Returns:
            Resource type string ('image', 'video', or 'raw')
        """
        ext = os.path.splitext(filename)[1].lower()

        # Image extensions
        if ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.tif', '.svg', '.ico'):
            return self.RESOURCE_IMAGE

        # Video extensions
        if ext in ('.mp4', '.webm', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.m4v', '.3gp'):
            return self.RESOURCE_VIDEO

        # Everything else is raw
        return self.RESOURCE_RAW

    def read(self, filename: str) -> Optional[bytes]:
        """
        Read a file from Cloudinary.

        Args:
            filename: Path to the file relative to base folder

        Returns:
            File contents as bytes, or None
        """
        if not self._cloudinary:
            return None

        try:
            import requests

            public_id = self._get_public_id(filename)
            resource_type = self._get_resource_type(filename)

            # Get resource info to get the URL
            result = self._api.resource(public_id, resource_type=resource_type)
            url = result.get('secure_url') or result.get('url')

            if url:
                response = requests.get(url)
                if response.status_code == 200:
                    return response.content

            return None

        except Exception:
            return None

    def write(self, filename: str, data: Union[bytes, BinaryIO],
              auto_tag: bool = None, categorization: List[str] = None) -> bool:
        """
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
        """
        if not self._uploader:
            return False

        try:
            public_id = self._get_public_id(filename)
            resource_type = self._get_resource_type(filename)

            # Prepare upload options
            upload_options = {
                'public_id': public_id,
                'resource_type': resource_type,
                'overwrite': True,
                'invalidate': True,
            }

            # Add folder if base_path contains one
            if '/' in public_id:
                folder = '/'.join(public_id.split('/')[:-1])
                upload_options['folder'] = folder
                upload_options['public_id'] = public_id.split('/')[-1]

            # Handle auto-tagging
            use_auto_tag = auto_tag if auto_tag is not None else self._auto_tagging
            if use_auto_tag and resource_type == self.RESOURCE_IMAGE:
                # Use Google's auto-tagging (most accurate for archaeological content)
                upload_options['categorization'] = 'google_tagging'
                upload_options['auto_tagging'] = self._auto_tagging_confidence

            # Add custom categorization models
            if categorization:
                upload_options['categorization'] = ','.join(categorization)

            # Prepare data for upload
            if isinstance(data, bytes):
                file_buffer = io.BytesIO(data)
            else:
                file_buffer = data

            # Upload to Cloudinary
            result = self._uploader.upload(file_buffer, **upload_options)

            return result.get('public_id') is not None

        except Exception as e:
            return False

    def write_with_ai(self, filename: str, data: Union[bytes, BinaryIO],
                      features: List[str] = None) -> Optional[CloudinaryAIResult]:
        """
        Write a file to Cloudinary with AI analysis.

        Args:
            filename: Path to the file
            data: File contents
            features: List of AI features to enable:
                     'auto_tagging', 'object_detection', 'ocr',
                     'color_analysis', 'face_detection', 'moderation'

        Returns:
            CloudinaryAIResult with AI analysis data, or None on failure
        """
        if not self._uploader:
            return None

        features = features or ['auto_tagging']

        try:
            public_id = self._get_public_id(filename)
            resource_type = self._get_resource_type(filename)

            upload_options = {
                'public_id': public_id,
                'resource_type': resource_type,
                'overwrite': True,
                'invalidate': True,
            }

            # Add folder if needed
            if '/' in public_id:
                folder = '/'.join(public_id.split('/')[:-1])
                upload_options['folder'] = folder
                upload_options['public_id'] = public_id.split('/')[-1]

            # Configure AI features
            categorization_models = []

            if 'auto_tagging' in features:
                categorization_models.append('google_tagging')
                upload_options['auto_tagging'] = self._auto_tagging_confidence

            if 'object_detection' in features:
                categorization_models.append('google_video_tagging')

            if categorization_models:
                upload_options['categorization'] = ','.join(categorization_models)

            if 'ocr' in features:
                upload_options['ocr'] = 'adv_ocr'

            if 'color_analysis' in features:
                upload_options['colors'] = True

            if 'face_detection' in features:
                upload_options['detection'] = 'adv_face'

            if 'moderation' in features:
                upload_options['moderation'] = 'aws_rek'

            # Prepare data
            if isinstance(data, bytes):
                file_buffer = io.BytesIO(data)
            else:
                file_buffer = data

            # Upload with AI analysis
            result = self._uploader.upload(file_buffer, **upload_options)

            # Parse AI results
            ai_result = CloudinaryAIResult(
                public_id=result.get('public_id', ''),
                tags=result.get('tags', []),
            )

            # Extract categorization results
            info = result.get('info', {})
            if 'categorization' in info:
                cat_data = info['categorization']
                if 'google_tagging' in cat_data:
                    tags_data = cat_data['google_tagging'].get('data', [])
                    ai_result.tags = [t['tag'] for t in tags_data if t.get('confidence', 0) >= self._auto_tagging_confidence]

            # Extract OCR results
            if 'ocr' in info:
                ocr_data = info['ocr'].get('adv_ocr', {})
                text_annotations = ocr_data.get('data', [])
                if text_annotations:
                    # Combine all text annotations
                    texts = []
                    for annotation in text_annotations:
                        if 'textAnnotations' in annotation:
                            for ta in annotation['textAnnotations']:
                                if 'description' in ta:
                                    texts.append(ta['description'])
                    ai_result.ocr_text = '\n'.join(texts)

            # Extract color data
            if 'colors' in result:
                ai_result.colors = result['colors']

            # Extract face detection
            if 'faces' in result:
                ai_result.faces = result['faces']

            # Extract moderation
            if 'moderation' in result:
                ai_result.moderation = result['moderation']

            return ai_result

        except Exception as e:
            return None

    def exists(self, filename: str) -> bool:
        """
        Check if a file exists in Cloudinary.

        Args:
            filename: Path to the file relative to base folder

        Returns:
            True if file exists
        """
        if not self._api:
            return False

        try:
            public_id = self._get_public_id(filename)
            resource_type = self._get_resource_type(filename)
            self._api.resource(public_id, resource_type=resource_type)
            return True
        except Exception:
            return False

    def delete(self, filename: str) -> bool:
        """
        Delete a file from Cloudinary.

        Args:
            filename: Path to the file relative to base folder

        Returns:
            True if deletion successful
        """
        if not self._uploader:
            return False

        try:
            public_id = self._get_public_id(filename)
            resource_type = self._get_resource_type(filename)

            result = self._uploader.destroy(public_id, resource_type=resource_type)
            return result.get('result') == 'ok'

        except Exception:
            return False

    def list(self, path: str = "") -> List[StorageFile]:
        """
        List files in a folder.

        Args:
            path: Path relative to base folder

        Returns:
            List of StorageFile objects
        """
        if not self._api:
            return []

        files = []

        try:
            # Construct the prefix
            if self.base_path:
                prefix = f"{self.base_path.strip('/')}/{path}".strip('/')
            else:
                prefix = path.strip('/')

            # Search for resources with this prefix
            result = self._api.resources(
                type='upload',
                prefix=prefix,
                max_results=500
            )

            for resource in result.get('resources', []):
                public_id = resource['public_id']
                filename = public_id.split('/')[-1]

                # Add extension back
                format_ext = resource.get('format', '')
                if format_ext:
                    filename = f"{filename}.{format_ext}"

                # Calculate relative path
                if prefix:
                    rel_path = public_id[len(prefix):].lstrip('/')
                else:
                    rel_path = public_id

                files.append(StorageFile(
                    name=filename,
                    path=rel_path,
                    size=resource.get('bytes', 0),
                    modified=resource.get('created_at'),
                    is_directory=False,
                    mime_type=f"{resource.get('resource_type', 'image')}/{resource.get('format', '')}",
                    url=resource.get('secure_url')
                ))

        except Exception:
            pass

        return files

    def get_url(self, filename: str, transformation: str = None) -> Optional[str]:
        """
        Get a URL for the file, optionally with transformations.

        Args:
            filename: Path to the file
            transformation: Optional Cloudinary transformation string

        Returns:
            URL string or None
        """
        if not self._cloudinary:
            return None

        try:
            public_id = self._get_public_id(filename)

            # Build URL with optional transformation
            options = {
                'secure': True,
            }

            if transformation:
                options['raw_transformation'] = transformation

            # Get the URL
            url = self._cloudinary.CloudinaryImage(public_id).build_url(**options)
            return url

        except Exception:
            return None

    def get_optimized_url(self, filename: str, width: int = None, height: int = None,
                          quality: str = 'auto', format: str = 'auto') -> Optional[str]:
        """
        Get an optimized URL for the file.

        Args:
            filename: Path to the file
            width: Target width (optional)
            height: Target height (optional)
            quality: Quality setting ('auto', 'auto:best', 'auto:good', 'auto:eco', 'auto:low', or 1-100)
            format: Output format ('auto', 'webp', 'jpg', 'png', etc.)

        Returns:
            Optimized URL string or None
        """
        if not self._cloudinary:
            return None

        try:
            public_id = self._get_public_id(filename)

            transformation = {
                'quality': quality,
                'fetch_format': format,
            }

            if width:
                transformation['width'] = width
                transformation['crop'] = 'scale'

            if height:
                transformation['height'] = height
                if width:
                    transformation['crop'] = 'fill'
                else:
                    transformation['crop'] = 'scale'

            url = self._cloudinary.CloudinaryImage(public_id).build_url(
                transformation=[transformation],
                secure=True
            )
            return url

        except Exception:
            return None

    def get_thumbnail_url(self, filename: str, width: int = 150, height: int = 150) -> Optional[str]:
        """
        Get a thumbnail URL for the file.

        Args:
            filename: Path to the file
            width: Thumbnail width
            height: Thumbnail height

        Returns:
            Thumbnail URL or None
        """
        return self.get_optimized_url(filename, width=width, height=height, quality='auto:good')

    def get_ai_tags(self, filename: str) -> List[str]:
        """
        Get AI-generated tags for an existing image.

        Args:
            filename: Path to the file

        Returns:
            List of tag strings
        """
        if not self._api:
            return []

        try:
            public_id = self._get_public_id(filename)
            resource_type = self._get_resource_type(filename)

            # Request explicit analysis
            result = self._uploader.explicit(
                public_id,
                type='upload',
                resource_type=resource_type,
                categorization='google_tagging',
                auto_tagging=self._auto_tagging_confidence
            )

            # Extract tags
            info = result.get('info', {})
            if 'categorization' in info and 'google_tagging' in info['categorization']:
                tags_data = info['categorization']['google_tagging'].get('data', [])
                return [t['tag'] for t in tags_data if t.get('confidence', 0) >= self._auto_tagging_confidence]

            return result.get('tags', [])

        except Exception:
            return []

    def get_ocr_text(self, filename: str) -> Optional[str]:
        """
        Extract text from an image using OCR.

        Args:
            filename: Path to the image file

        Returns:
            Extracted text or None
        """
        if not self._uploader:
            return None

        try:
            public_id = self._get_public_id(filename)

            # Request OCR analysis
            result = self._uploader.explicit(
                public_id,
                type='upload',
                ocr='adv_ocr'
            )

            # Extract text
            info = result.get('info', {})
            if 'ocr' in info and 'adv_ocr' in info['ocr']:
                ocr_data = info['ocr']['adv_ocr']
                text_annotations = ocr_data.get('data', [])
                if text_annotations:
                    texts = []
                    for annotation in text_annotations:
                        if 'textAnnotations' in annotation:
                            for ta in annotation['textAnnotations']:
                                if 'description' in ta:
                                    texts.append(ta['description'])
                    return '\n'.join(texts)

            return None

        except Exception:
            return None

    def remove_background(self, filename: str, output_filename: str = None) -> Optional[str]:
        """
        Remove the background from an image.

        Args:
            filename: Path to the source image
            output_filename: Path for the output (optional, modifies in place if not provided)

        Returns:
            URL of the processed image or None
        """
        if not self._uploader:
            return None

        try:
            public_id = self._get_public_id(filename)
            output_public_id = self._get_public_id(output_filename) if output_filename else public_id

            # Apply background removal transformation
            result = self._uploader.explicit(
                public_id,
                type='upload',
                eager=[{
                    'effect': 'background_removal',
                }],
                eager_async=False
            )

            # Get the transformed URL
            if 'eager' in result and result['eager']:
                return result['eager'][0].get('secure_url')

            return None

        except Exception:
            return None

    def add_tags(self, filename: str, tags: List[str]) -> bool:
        """
        Add tags to a file.

        Args:
            filename: Path to the file
            tags: List of tags to add

        Returns:
            True if successful
        """
        if not self._uploader:
            return False

        try:
            public_id = self._get_public_id(filename)
            self._uploader.add_tag(tags, [public_id])
            return True
        except Exception:
            return False

    def remove_tags(self, filename: str, tags: List[str]) -> bool:
        """
        Remove tags from a file.

        Args:
            filename: Path to the file
            tags: List of tags to remove

        Returns:
            True if successful
        """
        if not self._uploader:
            return False

        try:
            public_id = self._get_public_id(filename)
            self._uploader.remove_tag(tags, [public_id])
            return True
        except Exception:
            return False

    def search(self, query: str, max_results: int = 30) -> List[StorageFile]:
        """
        Search for files using Cloudinary's search API.

        Args:
            query: Search query (supports Cloudinary search syntax)
            max_results: Maximum number of results

        Returns:
            List of matching StorageFile objects
        """
        if not self._cloudinary:
            return []

        files = []

        try:
            from cloudinary.search import Search

            # Build search with folder prefix if set
            search = Search()

            if self.base_path:
                search.expression(f'folder:{self.base_path}/* AND ({query})')
            else:
                search.expression(query)

            search.max_results(max_results)
            search.with_field('tags')
            search.with_field('context')

            result = search.execute()

            for resource in result.get('resources', []):
                public_id = resource['public_id']
                filename = public_id.split('/')[-1]
                format_ext = resource.get('format', '')
                if format_ext:
                    filename = f"{filename}.{format_ext}"

                files.append(StorageFile(
                    name=filename,
                    path=public_id,
                    size=resource.get('bytes', 0),
                    modified=resource.get('created_at'),
                    is_directory=False,
                    mime_type=f"{resource.get('resource_type', 'image')}/{format_ext}",
                    url=resource.get('secure_url')
                ))

        except Exception:
            pass

        return files

    def search_by_tags(self, tags: List[str], match_all: bool = True, max_results: int = 30) -> List[StorageFile]:
        """
        Search for files by tags.

        Args:
            tags: List of tags to search for
            match_all: If True, files must have all tags; if False, any tag matches
            max_results: Maximum number of results

        Returns:
            List of matching StorageFile objects
        """
        if not tags:
            return []

        if match_all:
            query = ' AND '.join([f'tags={tag}' for tag in tags])
        else:
            query = ' OR '.join([f'tags={tag}' for tag in tags])

        return self.search(query, max_results)

    def get_usage_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get Cloudinary account usage statistics.

        Returns:
            Dictionary with usage stats or None
        """
        if not self._api:
            return None

        try:
            return self._api.usage()
        except Exception:
            return None
