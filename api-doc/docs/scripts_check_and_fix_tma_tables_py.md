# scripts/check_and_fix_tma_tables.py

## Overview

This file contains 4 documented elements.

## Functions

### check_table_exists(cursor, table_name)

Check if table exists

**Parameters:**
- `cursor`
- `table_name`

### get_table_columns(cursor, table_name)

Get columns of a table

**Parameters:**
- `cursor`
- `table_name`

### main()

Verifies and initializes the `tma_materiali_archeologici` and `tma_materiali_ripetibili` tables in the pyarchinit SQLite database located at the user's default QGIS3 profile path. For each table, it creates the table if it does not already exist, reports the column count, and validates foreign key constraints on `tma_materiali_ripetibili`. It then performs a test insert-and-delete cycle on both tables to confirm write operations succeed, committing all changes or rolling back on any `sqlite3.Error`.

