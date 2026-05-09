# modules/db/pyarchinit_OS_utility.py

## Overview

This file contains 5 documented elements.

## Classes

### pyarchinit_OS_Utility

*No description available.*
A utility class providing operating system-level file and directory operations for the pyarchinit plugin. It exposes methods to create directories, copy general files to a destination (only if the destination does not already exist), and copy image files from either local paths or remote URLs (`unibo://`, `http://`, `https://`, `cloudinary://`) by downloading remote content before writing it to the destination. Remote image retrieval is handled via `RemoteImageLoader` when available, falling back silently on import or runtime errors.

#### Methods

##### create_dir(self, d)

Creates a directory at the specified path using `os.makedirs`. Returns `1` if the directory was successfully created, or `0` if the directory already exists. If directory creation fails for any other reason, the originating `OSError` is re-raised.

##### copy_file_img(self, f, d)

Copy an image file to destination.
Supports local paths and remote URLs (unibo://, http://, https://, cloudinary://).

##### copy_file(self, f, d)

*No description available.*
Copies a file from the source path `f` to the destination `d` using `shutil.copy`. If the destination already exists (determined via `os.access`), the method returns `0` without performing the copy. On a successful copy it returns `1`; if an `OSError` occurs during the copy, it returns `0` if the destination is found to exist, otherwise re-raises the exception.

