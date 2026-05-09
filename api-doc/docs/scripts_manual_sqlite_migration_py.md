# scripts/manual_sqlite_migration.py

## Overview

This file contains 6 documented elements.

## Functions

### backup_database(db_path)

Create a backup of the database

**Parameters:**
- `db_path`

### clean_new_tables(conn)

Remove any leftover _new tables

**Parameters:**
- `conn`

### migrate_table_fields(conn, table_name, fields_to_migrate)

Migrate specific fields in a table to TEXT type

**Parameters:**
- `conn`
- `table_name`
- `fields_to_migrate`

### recreate_views(conn)

Recreate views after migration

**Parameters:**
- `conn`

### main()

*No description available.*
Entry point for the PyArchInit SQLite Migration Tool. Accepts a single command-line argument specifying the path to an existing SQLite database file, creates a backup, then sequentially migrates fields across twelve predefined tables and recreates database views. On failure, the transaction is rolled back and the backup path is reported; on success, a summary of successfully migrated tables is printed.

