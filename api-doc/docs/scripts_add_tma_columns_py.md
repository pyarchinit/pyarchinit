# scripts/add_tma_columns.py

## Overview

This file contains 3 documented elements.

## Functions

### add_columns(db_path)

Aggiunge le colonne created_by e updated_by.

**Parameters:**
- `db_path`

### main()

Serves as the entry point for the script, orchestrating the addition of missing TMA columns to a SQLite database located at the hardcoded path `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`. It invokes `add_columns` with that path and prints a success or failure message based on the result. Returns `0` on success or `1` on failure, with the return value passed to `sys.exit` when the script is run directly.

