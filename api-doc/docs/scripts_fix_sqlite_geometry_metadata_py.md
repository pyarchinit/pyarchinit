# scripts/fix_sqlite_geometry_metadata.py

## Overview

This file contains 3 documented elements.

## Functions

### fix_geometry_in_metadata_file(file_path)

Fix geometry handling for SQLite in a structures_metadata file

**Parameters:**
- `file_path`

### main()

*No description available.*
Serves as the entry point for a batch-processing script that fixes SQLite geometry issues across all Python metadata files in the `structures_metadata` plugin directory. It enumerates every `.py` file in the hardcoded directory (excluding `__init__`-style files), then calls `fix_geometry_in_metadata_file()` on each one in sorted order, printing a success or failure message for every file processed.

