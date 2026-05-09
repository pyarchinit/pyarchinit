# scripts/update_us_view_definition.py

## Overview

This file contains 3 documented elements.

## Functions

### update_view_definition(db_path)

Update the pyarchinit_us_view to ensure proper column selection

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point for the script that resolves the target SQLite database path and invokes the view update operation. It defaults to `~/pyarchinit_DB_folder/pyarchinit_db.sqlite` but accepts an alternative path as the first command-line argument. If the resolved path does not exist, the function prints usage instructions and exits with a non-zero status code; otherwise, it calls `update_view_definition` with the resolved path.

