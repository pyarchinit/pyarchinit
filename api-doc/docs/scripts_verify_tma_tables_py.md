# scripts/verify_tma_tables.py

## Overview

This file contains 3 documented elements.

## Functions

### verify_tables(db_path)

Verifica l'esistenza delle tabelle TMA.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point of the script that verifies the existence of TMA tables in a SQLite database located at the hardcoded path `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`. It prints a header banner and delegates the actual verification logic to `verify_tables()`, passing the database path as argument. Returns `0` upon completion, and is intended to be invoked via `sys.exit()` when the script is run directly.

