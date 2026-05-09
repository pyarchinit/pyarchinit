# scripts/insert_missing_ldct.py

## Overview

This file contains 3 documented elements.

## Functions

### insert_ldct_records(db_path)

Inserisce i record LDCT.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point of the script that orchestrates the insertion of missing LDCT records into a SQLite database located at a hardcoded path (`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`). It first verifies that the database file exists, printing an error message and returning `1` if it does not, then delegates the insertion logic to `insert_ldct_records()`. Returns `0` on success or `1` on failure, and is intended to be called via `sys.exit()` when the script is executed directly.

