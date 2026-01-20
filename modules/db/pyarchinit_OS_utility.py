#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
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

import os
import sys
import shutil
import subprocess


class pyarchinit_OS_Utility:
    def create_dir(self, d):
        dirname = d

        try:
            os.makedirs(dirname)
            return 1
        except OSError:
            if os.path.exists(dirname):
                # We are nearly safe
                return 0  # la cartella esiste
            else:
                # There was an error on creation, so make sure we know about it
                raise

    def copy_file_img(self, f, d):
        """
        Copy an image file to destination.
        Supports local paths and remote URLs (unibo://, http://, https://, cloudinary://).
        """
        # Check if source is a remote URL
        is_remote = f and f.startswith(('unibo://', 'http://', 'https://', 'cloudinary://'))

        if is_remote:
            # Handle remote files by downloading them first
            try:
                from ..utility.remote_image_loader import (
                    RemoteImageLoader,
                    load_unibo_credentials_from_qgis,
                    is_unibo_path
                )


                # Load credentials if needed
                if is_unibo_path(f):
                    load_unibo_credentials_from_qgis()

                # Download file data
                if f.startswith('unibo://'):
                    data = RemoteImageLoader._download_from_unibo(f)
                elif f.startswith('cloudinary://'):
                    url = RemoteImageLoader.cloudinary_to_url(f)
                    data = RemoteImageLoader._download_image(url)
                else:
                    data = RemoteImageLoader._download_image(f)

                if data:
                    # Get filename from source path
                    filename = f.split('/')[-1]

                    # Determine full destination path
                    if os.path.isdir(d):
                        dest_file = os.path.join(d, filename)
                    else:
                        dest_file = d

                    # Write downloaded data to destination
                    with open(dest_file, 'wb') as out_file:
                        out_file.write(data)

                else:

            except ImportError as e:
            except Exception as e:
        else:
            # Local file - use original method
            file_path = f
            destination = d
            shutil.copy(file_path, destination)

    def copy_file(self, f, d):
        file_path = f
        destination = d
        if os.access(destination, 0):
            return 0  # la cartella esiste
        else:
            try:
                shutil.copy(file_path, destination)
                return 1
            except OSError:
                if os.path.exists(destination):
                    return 0
                else:
                    raise
