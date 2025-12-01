"""
S3/R2 Storage Backend
=====================

Storage backend for Amazon S3 and Cloudflare R2 compatible storage.

Requirements:
    pip install boto3

Path formats:
    - s3://bucket-name/key/path
    - r2://bucket-name/key/path

Credentials required:
    - access_key: AWS/R2 access key ID
    - secret_key: AWS/R2 secret access key
    - region: AWS region (default: us-east-1)
    - endpoint: Custom endpoint URL (required for R2, optional for S3)
    - account_id: Cloudflare account ID (for R2)

Author: PyArchInit Team
License: GPL v2
"""

import io
import os
from typing import List, Optional, Union, BinaryIO

from .base_backend import StorageBackend, StorageType, StorageFile


class S3Backend(StorageBackend):
    """
    Amazon S3 and Cloudflare R2 storage backend.

    Uses boto3 for S3-compatible API operations.
    Works with AWS S3, Cloudflare R2, MinIO, and other S3-compatible services.
    """

    # Default region
    DEFAULT_REGION = 'us-east-1'

    # Multipart upload threshold (5 MB)
    MULTIPART_THRESHOLD = 5 * 1024 * 1024

    # Cloudflare R2 endpoint template
    R2_ENDPOINT_TEMPLATE = 'https://{account_id}.r2.cloudflarestorage.com'

    def __init__(self, base_path: str, credentials: Optional[dict] = None):
        """
        Initialize S3/R2 backend.

        Args:
            base_path: Bucket name (e.g., "my-bucket")
            credentials: Dict with access_key, secret_key, region, endpoint, account_id
        """
        super().__init__(base_path, credentials)
        self._s3_client = None
        self._s3_resource = None
        self._bucket_name = base_path
        self._is_r2 = False

    @property
    def storage_type(self) -> StorageType:
        return StorageType.R2 if self._is_r2 else StorageType.S3

    def connect(self) -> bool:
        """
        Establish connection to S3/R2.

        Returns:
            True if connection successful
        """
        try:
            import boto3
            from botocore.config import Config

            access_key = self.credentials.get('access_key')
            secret_key = self.credentials.get('secret_key')
            region = self.credentials.get('region', self.DEFAULT_REGION)
            endpoint = self.credentials.get('endpoint')
            account_id = self.credentials.get('account_id')

            if not access_key or not secret_key:
                return False

            # Check if this is R2
            if account_id and not endpoint:
                endpoint = self.R2_ENDPOINT_TEMPLATE.format(account_id=account_id)
                self._is_r2 = True
            elif endpoint and 'r2.cloudflarestorage.com' in endpoint:
                self._is_r2 = True

            # Configure boto3
            config = Config(
                signature_version='s3v4',
                s3={'addressing_style': 'path'}
            )

            # Create session and client
            session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )

            client_kwargs = {
                'config': config
            }

            if endpoint:
                client_kwargs['endpoint_url'] = endpoint

            self._s3_client = session.client('s3', **client_kwargs)
            self._s3_resource = session.resource('s3', **client_kwargs)

            # Verify connection by checking bucket exists
            self._s3_client.head_bucket(Bucket=self._bucket_name)

            self._connected = True
            return True

        except ImportError:
            # boto3 not installed
            return False
        except Exception:
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Close connection to S3/R2"""
        self._s3_client = None
        self._s3_resource = None
        self._connected = False

    def read(self, filename: str) -> Optional[bytes]:
        """
        Read a file from S3/R2.

        Args:
            filename: Key (path) of the file in the bucket

        Returns:
            File contents as bytes, or None
        """
        if not self._s3_client:
            return None

        try:
            response = self._s3_client.get_object(
                Bucket=self._bucket_name,
                Key=filename
            )
            return response['Body'].read()

        except Exception:
            return None

    def write(self, filename: str, data: Union[bytes, BinaryIO]) -> bool:
        """
        Write a file to S3/R2.

        Args:
            filename: Key (path) of the file in the bucket
            data: File contents as bytes or file-like object

        Returns:
            True if successful
        """
        if not self._s3_client:
            return False

        try:
            # Determine content type
            content_type = self._detect_content_type(filename)

            # Prepare data
            if isinstance(data, bytes):
                body = data
            else:
                body = data.read()

            # Upload
            extra_args = {
                'ContentType': content_type
            }

            if len(body) > self.MULTIPART_THRESHOLD:
                # Use multipart upload for large files
                self._multipart_upload(filename, body, extra_args)
            else:
                self._s3_client.put_object(
                    Bucket=self._bucket_name,
                    Key=filename,
                    Body=body,
                    **extra_args
                )

            return True

        except Exception:
            return False

    def _multipart_upload(self, key: str, data: bytes, extra_args: dict):
        """
        Upload a large file using multipart upload.

        Args:
            key: S3 key
            data: File data
            extra_args: Extra arguments for upload
        """
        from boto3.s3.transfer import TransferConfig

        config = TransferConfig(
            multipart_threshold=self.MULTIPART_THRESHOLD,
            multipart_chunksize=self.MULTIPART_THRESHOLD,
            use_threads=True
        )

        bucket = self._s3_resource.Bucket(self._bucket_name)
        bucket.upload_fileobj(
            io.BytesIO(data),
            key,
            ExtraArgs=extra_args,
            Config=config
        )

    def exists(self, filename: str) -> bool:
        """
        Check if a file exists in S3/R2.

        Args:
            filename: Key (path) of the file in the bucket

        Returns:
            True if file exists
        """
        if not self._s3_client:
            return False

        try:
            self._s3_client.head_object(
                Bucket=self._bucket_name,
                Key=filename
            )
            return True
        except Exception:
            return False

    def delete(self, filename: str) -> bool:
        """
        Delete a file from S3/R2.

        Args:
            filename: Key (path) of the file in the bucket

        Returns:
            True if deletion successful
        """
        if not self._s3_client:
            return False

        try:
            self._s3_client.delete_object(
                Bucket=self._bucket_name,
                Key=filename
            )
            return True
        except Exception:
            return False

    def list(self, path: str = "") -> List[StorageFile]:
        """
        List files in a prefix (folder).

        Args:
            path: Prefix (folder path) to list

        Returns:
            List of StorageFile objects
        """
        if not self._s3_client:
            return []

        files = []

        try:
            # Ensure path ends with / if not empty
            prefix = path
            if prefix and not prefix.endswith('/'):
                prefix = prefix + '/'

            paginator = self._s3_client.get_paginator('list_objects_v2')

            for page in paginator.paginate(Bucket=self._bucket_name, Prefix=prefix, Delimiter='/'):
                # Add files
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    name = key[len(prefix):] if prefix else key

                    # Skip if this is the prefix itself
                    if not name:
                        continue

                    files.append(StorageFile(
                        name=name,
                        path=key,
                        size=obj['Size'],
                        modified=obj['LastModified'].isoformat(),
                        is_directory=False,
                        mime_type=self._detect_content_type(name),
                        url=self.get_url(key)
                    ))

                # Add "folders" (common prefixes)
                for prefix_info in page.get('CommonPrefixes', []):
                    folder_prefix = prefix_info['Prefix']
                    name = folder_prefix[len(prefix):].rstrip('/')

                    files.append(StorageFile(
                        name=name,
                        path=folder_prefix.rstrip('/'),
                        size=0,
                        modified=None,
                        is_directory=True,
                        mime_type=None,
                        url=None
                    ))

        except Exception:
            pass

        return files

    def get_url(self, filename: str) -> Optional[str]:
        """
        Get a pre-signed URL for the file.

        Args:
            filename: Key (path) of the file in the bucket

        Returns:
            Pre-signed URL (valid for 1 hour)
        """
        if not self._s3_client:
            return None

        try:
            url = self._s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self._bucket_name,
                    'Key': filename
                },
                ExpiresIn=3600  # 1 hour
            )
            return url
        except Exception:
            return None

    def get_public_url(self, filename: str) -> str:
        """
        Get the public URL for a file (if bucket is public).

        Args:
            filename: Key (path) of the file in the bucket

        Returns:
            Public URL (may not work if bucket is private)
        """
        endpoint = self.credentials.get('endpoint', '')
        region = self.credentials.get('region', self.DEFAULT_REGION)

        if endpoint:
            # Custom endpoint (R2 or other S3-compatible)
            return f"{endpoint}/{self._bucket_name}/{filename}"
        else:
            # Standard S3
            return f"https://{self._bucket_name}.s3.{region}.amazonaws.com/{filename}"

    def ensure_directory(self, path: str) -> bool:
        """
        Ensure a "directory" exists in S3/R2.

        Note: S3 doesn't have real directories. This creates a zero-byte
        object with a trailing slash to simulate a folder.

        Args:
            path: Directory path

        Returns:
            True (always succeeds for S3)
        """
        if not path:
            return True

        # S3 doesn't need directories, but we can create a placeholder
        if not path.endswith('/'):
            path = path + '/'

        try:
            if not self.exists(path):
                self._s3_client.put_object(
                    Bucket=self._bucket_name,
                    Key=path,
                    Body=b''
                )
            return True
        except Exception:
            return True  # S3 doesn't really need directories

    def get_size(self, filename: str) -> int:
        """
        Get the size of a file in bytes.

        Args:
            filename: Key (path) of the file in the bucket

        Returns:
            File size in bytes, or -1 if file doesn't exist
        """
        if not self._s3_client:
            return -1

        try:
            response = self._s3_client.head_object(
                Bucket=self._bucket_name,
                Key=filename
            )
            return response['ContentLength']
        except Exception:
            return -1

    def copy(self, source: str, destination: str) -> bool:
        """
        Copy a file within S3/R2.

        Args:
            source: Source key
            destination: Destination key

        Returns:
            True if copy successful
        """
        if not self._s3_client:
            return False

        try:
            self._s3_client.copy_object(
                Bucket=self._bucket_name,
                CopySource={'Bucket': self._bucket_name, 'Key': source},
                Key=destination
            )
            return True
        except Exception:
            return False

    def move(self, source: str, destination: str) -> bool:
        """
        Move a file within S3/R2 (copy + delete).

        Args:
            source: Source key
            destination: Destination key

        Returns:
            True if move successful
        """
        if self.copy(source, destination):
            return self.delete(source)
        return False

    def _detect_content_type(self, filename: str) -> str:
        """Detect content type from filename"""
        ext = os.path.splitext(filename)[1].lower()
        content_types = {
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
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
        }
        return content_types.get(ext, 'application/octet-stream')

    def set_public_read(self, filename: str) -> bool:
        """
        Make a file publicly readable.

        Args:
            filename: Key (path) of the file

        Returns:
            True if successful
        """
        if not self._s3_client:
            return False

        try:
            self._s3_client.put_object_acl(
                Bucket=self._bucket_name,
                Key=filename,
                ACL='public-read'
            )
            return True
        except Exception:
            return False
