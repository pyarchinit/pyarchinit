# scripts/safe_sqlite_migration.py

## Overview

This file contains 21 documented elements.

## Functions

### backup_database(db_path)

Create a backup of the database

**Parameters:**
- `db_path`

### verify_table_exists(conn, table_name)

Verify that a table exists and has data

**Parameters:**
- `conn`
- `table_name`

### get_dependent_views(conn)

Get all views that might depend on the tables we're migrating

**Parameters:**
- `conn`

### drop_all_views(conn)

Drop all views to avoid dependency issues

**Parameters:**
- `conn`

### migrate_table_with_validation(conn, table_name, fields_to_migrate)

Migrate table with data validation

**Parameters:**
- `conn`
- `table_name`
- `fields_to_migrate`

### main()

### backup_database(db_path)

Create a backup of the database

**Parameters:**
- `db_path`

### verify_table_exists(conn, table_name)

Verify that a table exists and has data

**Parameters:**
- `conn`
- `table_name`

### get_dependent_views(conn)

Get all views that might depend on the tables we're migrating

**Parameters:**
- `conn`

### drop_all_views(conn)

Drop all views to avoid dependency issues

**Parameters:**
- `conn`

### migrate_table_with_validation(conn, table_name, fields_to_migrate)

Migrate table with data validation

**Parameters:**
- `conn`
- `table_name`
- `fields_to_migrate`

### main()

### backup_database(db_path)

Create a backup of the database

**Parameters:**
- `db_path`

### verify_table_exists(conn, table_name)

Verify that a table exists and has data

**Parameters:**
- `conn`
- `table_name`

### get_dependent_views(conn)

Get all views that might depend on the tables we're migrating

**Parameters:**
- `conn`

### drop_all_views(conn)

Drop all views to avoid dependency issues

**Parameters:**
- `conn`

### migrate_table_with_validation(conn, table_name, fields_to_migrate)

Migrate table with data validation

**Parameters:**
- `conn`
- `table_name`
- `fields_to_migrate`

### main()

