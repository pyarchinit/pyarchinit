# scripts/update_thesaurus_sigla_simple.py

## Overview

This file contains 3 documented elements.

## Functions

### backup_and_recreate(db_path)

Backup dei dati e ricreazione tabella.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point for the database migration script that updates the `sigla` column definition from `VARCHAR(3)` to `VARCHAR(100)` in a hardcoded SQLite database located at `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`. It verifies the database file exists before invoking `backup_and_recreate()` to perform the schema change, printing progress and result messages throughout. Returns `0` on success or `1` if the database file is not found or the migration process fails.

