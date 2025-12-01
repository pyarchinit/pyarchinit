#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>
    email                : mandoluca at gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from __future__ import print_function
import shutil
import io
import os
import tempfile
from PIL import Image

from builtins import str

from ..db.pyarchinit_conn_strings import *

# Import storage module (lazy import to avoid circular dependencies)
_storage_manager = None


def get_storage_manager():
    """Get or create the global StorageManager instance."""
    global _storage_manager
    if _storage_manager is None:
        try:
            from ..storage import StorageManager, CredentialsManager
            creds_manager = CredentialsManager()
            _storage_manager = StorageManager(credentials_manager=creds_manager)
        except ImportError:
            # Fallback: storage module not available
            _storage_manager = None
    return _storage_manager


def is_remote_path(path):
    """Check if a path is a remote storage path."""
    if not path:
        return False
    remote_prefixes = ('gdrive://', 'dropbox://', 's3://', 'r2://',
                       'webdav://', 'http://', 'https://', 'sftp://')
    return any(path.lower().startswith(prefix) for prefix in remote_prefixes)


class Media_utility(object):
    """
    Media utility class for creating thumbnails.
    Supports both local filesystem and remote storage backends.

    Usage:
        m = Media_utility()
        # Local path (backward compatible)
        m.resample_images(1, '/path/to/image.jpg', 'image.jpg', '/path/to/thumbs/', '.jpg')
        # Remote storage
        m.resample_images(1, 'gdrive://images/image.jpg', 'image.jpg', 'gdrive://thumbs/', '.jpg')
    """

    def resample_images(self, mid, ip, i, o, ts):
        """
        Create a thumbnail from an image.

        Args:
            mid: Maximum number ID for output filename
            ip: Input path (local or remote)
            i: Input filename
            o: Output path (local or remote)
            ts: Thumbnail suffix
        """
        self.max_num_id = mid
        self.input_path = ip
        self.infile = i
        self.outpath = o
        self.thumb_suffix = ts

        size = 150, 150
        infile = str(self.input_path)
        outfile = ('%s%s_%s%s') % (
            self.outpath, str(self.max_num_id), os.path.splitext(self.infile)[0], self.thumb_suffix)

        # Check if we're dealing with remote storage
        if is_remote_path(infile) or is_remote_path(outfile):
            self._resample_remote(infile, outfile, size, dpi=(100, 100))
        else:
            # Original local file handling
            im = Image.open(infile)
            im.thumbnail(size, Image.LANCZOS)
            im.save(outfile, dpi=(100, 100))

    def _resample_remote(self, infile, outfile, size, dpi=(100, 100)):
        """
        Handle remote storage resampling.

        Downloads image from remote, creates thumbnail, uploads to destination.
        """
        storage = get_storage_manager()
        if storage is None:
            raise RuntimeError("Storage module not available for remote operations")

        temp_input = None
        temp_output = None

        try:
            # Read input image
            if is_remote_path(infile):
                # Download from remote
                backend = storage.get_backend(infile)
                _, _, relative_path = storage.parse_path(infile)
                image_data = backend.read(relative_path or os.path.basename(infile))
                if image_data is None:
                    raise FileNotFoundError(f"Cannot read remote file: {infile}")
                im = Image.open(io.BytesIO(image_data))
            else:
                # Local file
                im = Image.open(infile)

            # Create thumbnail
            im.thumbnail(size, Image.LANCZOS)

            # Save to output
            if is_remote_path(outfile):
                # Upload to remote
                buffer = io.BytesIO()
                # Determine format from extension
                ext = os.path.splitext(outfile)[1].lower()
                format_map = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG',
                              '.gif': 'GIF', '.bmp': 'BMP', '.tiff': 'TIFF'}
                img_format = format_map.get(ext, 'JPEG')
                im.save(buffer, format=img_format, dpi=dpi)
                buffer.seek(0)

                backend = storage.get_backend(outfile)
                _, _, relative_path = storage.parse_path(outfile)
                backend.write(relative_path or os.path.basename(outfile), buffer.getvalue())
            else:
                # Local file
                # Ensure output directory exists
                os.makedirs(os.path.dirname(outfile), exist_ok=True)
                im.save(outfile, dpi=dpi)

        finally:
            # Cleanup temp files if any
            if temp_input and os.path.exists(temp_input):
                os.remove(temp_input)
            if temp_output and os.path.exists(temp_output):
                os.remove(temp_output)


if __name__ == '__main__':
    m = Media_utility()
    conn = Connection()
    thumb_path = conn.thumb_path()
    thumb_path_str = thumb_path['thumb_path']
    print(thumb_path_str)
    

class Media_utility_resize(object):
    """
    Media utility class for creating resized images (higher resolution).
    Supports both local filesystem and remote storage backends.
    """

    def resample_images(self, mid, ip, i, o, ts):
        """
        Create a resized image (larger than thumbnail).

        Args:
            mid: Maximum number ID for output filename
            ip: Input path (local or remote)
            i: Input filename
            o: Output path (local or remote)
            ts: Thumbnail suffix
        """
        self.max_num_id = mid
        self.input_path = ip
        self.infile = i
        self.outpath = o
        self.thumb_suffix = ts

        size = 2008, 1417
        infile = str(self.input_path)
        outfile = ('%s%s_%s%s') % (
            self.outpath, str(self.max_num_id), os.path.splitext(self.infile)[0], self.thumb_suffix)

        # Check if we're dealing with remote storage
        if is_remote_path(infile) or is_remote_path(outfile):
            self._resample_remote(infile, outfile, size, dpi=(300, 300))
        else:
            # Original local file handling
            im = Image.open(infile)
            im.thumbnail(size, Image.LANCZOS)
            im.save(outfile, dpi=(300, 300))

    def _resample_remote(self, infile, outfile, size, dpi=(300, 300)):
        """
        Handle remote storage resampling.
        """
        storage = get_storage_manager()
        if storage is None:
            raise RuntimeError("Storage module not available for remote operations")

        try:
            # Read input image
            if is_remote_path(infile):
                backend = storage.get_backend(infile)
                _, _, relative_path = storage.parse_path(infile)
                image_data = backend.read(relative_path or os.path.basename(infile))
                if image_data is None:
                    raise FileNotFoundError(f"Cannot read remote file: {infile}")
                im = Image.open(io.BytesIO(image_data))
            else:
                im = Image.open(infile)

            # Create resized image
            im.thumbnail(size, Image.LANCZOS)

            # Save to output
            if is_remote_path(outfile):
                buffer = io.BytesIO()
                ext = os.path.splitext(outfile)[1].lower()
                format_map = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG',
                              '.gif': 'GIF', '.bmp': 'BMP', '.tiff': 'TIFF'}
                img_format = format_map.get(ext, 'JPEG')
                im.save(buffer, format=img_format, dpi=dpi)
                buffer.seek(0)

                backend = storage.get_backend(outfile)
                _, _, relative_path = storage.parse_path(outfile)
                backend.write(relative_path or os.path.basename(outfile), buffer.getvalue())
            else:
                os.makedirs(os.path.dirname(outfile), exist_ok=True)
                im.save(outfile, dpi=dpi)

        except Exception as e:
            raise


if __name__ == '__main__':
    m = Media_utility_resize()
    conn = Connection()
    thumb_resize = conn.thumb_resize()
    thumb_resize_str = thumb_resize['thumb_resize']
    print(thumb_resize_str)
    
class Video_utility(object):
    """
    Video utility class for moving video files.
    Supports both local filesystem and remote storage backends.
    """

    def resample_images(self, mid, ip, i, o, ts):
        """
        Move a video file to the output location.

        Args:
            mid: Maximum number ID for output filename
            ip: Input path (local or remote)
            i: Input filename
            o: Output path (local or remote)
            ts: Suffix
        """
        self.max_num_id = mid
        self.input_path = ip
        self.infile = i
        self.outpath = o
        self.thumb_suffix = ts

        infile = str(self.input_path)
        outfile = ('%s%s_%s%s') % (
            self.outpath, str(self.max_num_id), os.path.splitext(self.infile)[0], self.thumb_suffix)

        # Check if we're dealing with remote storage
        if is_remote_path(infile) or is_remote_path(outfile):
            self._move_remote(infile, outfile)
        else:
            shutil.move(infile, outfile)

    def _move_remote(self, infile, outfile):
        """
        Handle remote storage file move.
        """
        storage = get_storage_manager()
        if storage is None:
            raise RuntimeError("Storage module not available for remote operations")

        try:
            # Read input file
            if is_remote_path(infile):
                backend = storage.get_backend(infile)
                _, _, relative_path = storage.parse_path(infile)
                file_data = backend.read(relative_path or os.path.basename(infile))
                if file_data is None:
                    raise FileNotFoundError(f"Cannot read remote file: {infile}")
            else:
                with open(infile, 'rb') as f:
                    file_data = f.read()

            # Write to output
            if is_remote_path(outfile):
                backend = storage.get_backend(outfile)
                _, _, relative_path = storage.parse_path(outfile)
                backend.write(relative_path or os.path.basename(outfile), file_data)
            else:
                os.makedirs(os.path.dirname(outfile), exist_ok=True)
                with open(outfile, 'wb') as f:
                    f.write(file_data)

            # Delete source (move operation)
            if is_remote_path(infile):
                backend = storage.get_backend(infile)
                _, _, relative_path = storage.parse_path(infile)
                backend.delete(relative_path or os.path.basename(infile))
            else:
                os.remove(infile)

        except Exception as e:
            raise
            

if __name__ == '__main__':
    m = Video_utility()
    conn = Connection()
    thumb_path = conn.thumb_path()
    thumb_path_str = thumb_path['thumb_path']
    print(thumb_path_str)   
    
class Video_utility_resize(object):
    """
    Video utility class for copying video files.
    Supports both local filesystem and remote storage backends.
    """

    def resample_images(self, mid, ip, i, o, ts):
        """
        Copy a video file to the output location.

        Args:
            mid: Maximum number ID for output filename
            ip: Input path (local or remote)
            i: Input filename
            o: Output path (local or remote)
            ts: Suffix
        """
        self.max_num_id = mid
        self.input_path = ip
        self.infile = i
        self.outpath = o
        self.thumb_suffix = ts

        infile = str(self.input_path)
        outfile = ('%s%s_%s%s') % (
            self.outpath, str(self.max_num_id), os.path.splitext(self.infile)[0], self.thumb_suffix)

        # Check if we're dealing with remote storage
        if is_remote_path(infile) or is_remote_path(outfile):
            self._copy_remote(infile, outfile)
        else:
            shutil.copy(infile, outfile)

    def _copy_remote(self, infile, outfile):
        """
        Handle remote storage file copy.
        """
        storage = get_storage_manager()
        if storage is None:
            raise RuntimeError("Storage module not available for remote operations")

        try:
            # Read input file
            if is_remote_path(infile):
                backend = storage.get_backend(infile)
                _, _, relative_path = storage.parse_path(infile)
                file_data = backend.read(relative_path or os.path.basename(infile))
                if file_data is None:
                    raise FileNotFoundError(f"Cannot read remote file: {infile}")
            else:
                with open(infile, 'rb') as f:
                    file_data = f.read()

            # Write to output
            if is_remote_path(outfile):
                backend = storage.get_backend(outfile)
                _, _, relative_path = storage.parse_path(outfile)
                backend.write(relative_path or os.path.basename(outfile), file_data)
            else:
                os.makedirs(os.path.dirname(outfile), exist_ok=True)
                with open(outfile, 'wb') as f:
                    f.write(file_data)

        except Exception as e:
            raise
            

if __name__ == '__main__':
    m = Video_utility_resize()
    conn = Connection()
    thumb_resize = conn.thumb_resize()
    thumb_resize_str = thumb_resize['thumb_resize']
    print(thumb_resize_str)   
