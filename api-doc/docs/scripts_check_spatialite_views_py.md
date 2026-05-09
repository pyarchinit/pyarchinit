# scripts/check_spatialite_views.py

## Overview

This file contains 3 documented elements.

## Functions

### check_spatialite_views(db_path)

Check the registration status of SpatiaLite views

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point of the script that resolves the target SQLite database path, either from the first command-line argument or from the default location `~/pyarchinit_DB_folder/pyarchinit_db.sqlite`. If the resolved path does not exist on the filesystem, an error message with correct usage instructions is printed and the process exits with code `1`. Otherwise, `check_spatialite_views` is called with the resolved database path.

