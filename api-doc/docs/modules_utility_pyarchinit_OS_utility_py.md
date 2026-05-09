# modules/utility/pyarchinit_OS_utility.py

## Overview

This file contains 9 documented elements.

## Classes

### Pyarchinit_OS_Utility

*No description available.*
A utility class providing cross-platform operating system helper methods for file system operations, external tool detection, and platform identification. It exposes methods to create directories, copy generic files, and copy image files from both local paths and remote URLs (`unibo://`, `http://`, `https://`, `cloudinary://`). Static methods are also provided to check for Graphviz and PostgreSQL installations via subprocess, and to identify whether the current platform is Windows or macOS.

**Inherits from**: object

#### Methods

##### create_dir(self, d)

*No description available.*
Attempts to create a directory at the path specified by `d` using `os.makedirs`. Returns `1` if the directory was successfully created, or `0` if the directory already exists. If creation fails for any other reason, the originating `OSError` is re-raised.

##### copy_file_img(self, f, d)

Copy an image file to destination.
Supports local paths and remote URLs (unibo://, http://, https://, cloudinary://).

Args:
    f: Source file path (local or remote URL)
    d: Destination directory or file path

Returns:
    0 on success

##### copy_file(self, f, d)

*No description available.*
Copies a file from the source path `f` to the destination path `d`, normalizing both paths before performing the operation. If the destination already exists (checked via `os.access`), the method returns `0` without copying; otherwise, it attempts the copy using `shutil.copy` and returns `1` on success. If an `OSError` occurs during the copy, the method suppresses the exception and returns `0` if the destination is found to exist, or re-raises the exception if it does not.

##### checkgraphvizinstallation()

*No description available.*
A static method that verifies whether Graphviz is installed and accessible on the system. It attempts to execute `dot -V` as a subprocess with a 5-second timeout, suppressing all output. Returns `True` if the command succeeds, or `False` if a `subprocess.TimeoutExpired`, `FileNotFoundError`, or `OSError` exception is raised.

##### checkpostgresinstallation()

*No description available.*
A static method that verifies whether PostgreSQL client tools are available on the system by attempting to execute `pg_dump -V` as a subprocess with a 5-second timeout. Returns `True` if the command completes successfully, or `False` if a `subprocess.TimeoutExpired`, `FileNotFoundError`, or `OSError` exception is raised.

##### isWindows()

*No description available.*
A static method that determines whether the current operating system is Windows. It evaluates the `os.name` attribute and returns `True` if the value equals `'nt'`, which is the identifier for Windows-based systems, or `False` otherwise.

##### isMac()

*No description available.*
A static method that determines whether the current operating system is macOS. It evaluates the `sys.platform` value against the string `'darwin'`, returning `True` if the platform matches and `False` otherwise.

