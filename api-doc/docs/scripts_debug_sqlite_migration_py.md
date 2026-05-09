# scripts/debug_sqlite_migration.py

## Overview

This file contains 5 documented elements.

## Functions

### check_table_structure(conn, table_name)

Check the structure of a table

**Parameters:**
- `conn`
- `table_name`

### check_for_new_tables(conn)

Check for any _new tables that might be left over

**Parameters:**
- `conn`

### check_specific_fields(conn)

Check specific fields that should be migrated

**Parameters:**
- `conn`

### main()

*No description available.*
Entry point for the SQLite migration debug script. Validates that a database file path is provided as a command-line argument and that the file exists, then opens a connection to the specified SQLite database and sequentially invokes `check_for_new_tables`, `check_specific_fields`, and `check_table_structure` for the tables `inventario_materiali_table`, `tomba_table`, and `us_table`. The database connection is closed in a `finally` block to ensure cleanup regardless of any errors encountered during inspection.

