# scripts/fix_spatialite_view_registration.py

## Overview

This file contains 3 documented elements.

## Functions

### fix_view_registration(db_path)

Fix the registration of pyarchinit_us_view in SpatiaLite metadata tables

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point of the script that resolves the target SQLite database path, defaulting to `~/pyarchinit_DB_folder/pyarchinit_db.sqlite` if no command-line argument is provided. If the resolved path does not exist, the function prints an error message with usage instructions and exits with code `1`. Otherwise, it delegates execution to `fix_view_registration()`, passing the confirmed database path.

