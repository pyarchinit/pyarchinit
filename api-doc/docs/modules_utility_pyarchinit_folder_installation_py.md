# modules/utility/pyarchinit_folder_installation.py

## Overview

This file contains 4 documented elements.

## Classes

### pyarchinit_Folder_installation

*No description available.*
Manages the installation of the pyArchInit directory structure and associated resource files within the user's home directory under a `pyarchinit` subdirectory. It creates all required application folders (for databases, exports, reports, matrices, thumbnails, maps, and backups), then copies resource files from the plugin's `resources/dbfiles` directory to their respective destinations using fault-tolerant helper methods that allow installation to continue even when individual files are missing or corrupted. The class also handles extraction of bundled ZIP archives (`profile.zip`, `rscripts.zip`, `cambria.zip`) and installation of configuration files via `installConfigFile`.

**Inherits from**: object

#### Methods

##### install_dir(self)

Install all pyArchInit directories and copy resource files.

Creates directories first, then copies files with error handling
so installation continues even if some files are missing/corrupted.

##### installConfigFile(self, path)

Install config file and extract ZIP archives with error handling.

