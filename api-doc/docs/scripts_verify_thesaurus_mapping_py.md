# scripts/verify_thesaurus_mapping.py

## Overview

This file contains 3 documented elements.

## Functions

### verify_mapping(db_path)

Verifica la mappatura del thesaurus.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point of the script that verifies the thesaurus TMA mapping against a SQLite database located at a hardcoded path (`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`). It first checks whether the database file exists, printing an error message and returning `1` if it does not, then delegates the actual verification to `verify_mapping()`. Returns `0` on success or `1` on failure, and is intended to be invoked via `sys.exit()` when the module is run directly.

