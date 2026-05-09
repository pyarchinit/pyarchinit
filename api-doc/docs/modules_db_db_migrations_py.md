# modules/db/db_migrations.py

## Overview

This file contains 8 documented elements.

## Classes

### DatabaseMigrations

Handle database migrations for PyArchInit

#### Methods

##### __init__(self, db_manager)

*No description available.*
Initializes a `DatabaseMigrations` instance with the provided database manager. Stores the given `db_manager` as an instance attribute and extracts its `engine`, assigning it to `self.engine` for use by migration operations.

##### check_and_migrate(self)

Run all necessary migrations

##### table_exists(self, table_name)

Check if a table exists in the database

##### migrate_fauna_table(self)

Create fauna_table if it doesn't exist

##### migrate_fauna_thesaurus(self)

Add fauna thesaurus entries if they don't exist

## Functions

### run_migrations(db_manager)

Run all database migrations

**Parameters:**
- `db_manager`

