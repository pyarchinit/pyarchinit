# modules/db/add_uuid_support.py

## Overview

This file contains 8 documented elements.

## Classes

### UUIDSupport

Add entity_uuid support to database tables.

#### Methods

##### __init__(self, engine)

Initializes a `UUIDSupport` instance, configuring the database engine, inspector, and PostgreSQL detection flag. If an `engine` is provided, it is used directly along with an `inspect`-based inspector and a PostgreSQL check against the engine URL string. If no `engine` is provided, a `Connection` instance is created to build the engine via `create_engine` using the connection string, and PostgreSQL is detected by checking whether `'postgres'` appears in the lowercased connection string.

##### get_tables_to_update(self)

Get list of existing tables that need UUID support.

##### add_uuid_column(self, table_name)

Add entity_uuid column to a table if not already present.

##### populate_existing_uuids(self, table_name)

Generate UUIDs for existing records that don't have one.

##### update_all_tables(self)

Add entity_uuid column and populate UUIDs for all tables.

## Functions

### main()

Main function to add UUID support.

