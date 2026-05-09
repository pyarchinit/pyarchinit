# scripts/fix_sqlite_geometry_spatialite.py

## Overview

This file contains 4 documented elements.

## Functions

### get_table_name_and_geom_type(content)

Extract table name and geometry type from the file content

**Parameters:**
- `content`

### fix_geometry_in_file(file_path)

Fix geometry handling for SQLite in a structure file

**Parameters:**
- `file_path`

### main()

*No description available.*
Entry point that iterates over a predefined list of Python structure files located in a hardcoded QGIS plugin directory and applies geometry fixes to each by calling `fix_geometry_in_file()`. For each file in the list, it checks whether the file exists on disk, invokes the fix function, and prints a success or failure message to standard output. Execution is guarded by the `if __name__ == "__main__"` block.

