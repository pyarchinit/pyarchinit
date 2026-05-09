# modules/db/pyarchinit_db_update.py

## Overview

This file contains 14 documented elements.

## Classes

### DB_update

`DB_update` manages schema migrations and structural updates for a pyArchInit archaeological database, supporting both PostgreSQL and SQLite backends. It initializes a SQLAlchemy engine from a provided connection string and exposes methods to add missing columns, convert column types, migrate legacy table structures (including TMA tables and US-related integer-to-text field conversions), recreate dependent views, and repair invalid geometries across all spatial tables. DDL errors for already-existing columns or tables are silently suppressed to ensure idempotent execution across repeated upgrade runs.

**Inherits from**: object

#### Methods

##### __init__(self, conn_str)

Initializes a `DB_update` instance using the provided PostgreSQL connection string. Creates a SQLAlchemy engine (with `echo=False`) and a `MetaData` object, storing all three as instance attributes (`conn_str`, `engine`, and `metadata`).

##### update_table(self)

Performs a comprehensive schema migration and update of the database, adding missing columns, converting column types, and ensuring all required tables conform to the expected structure. It handles both SQLite and PostgreSQL backends, applying database-specific migration paths, and processes tables including `us_table`, `inventario_materiali_table`, `pottery_table`, `site_table`, `tomba_table`, `individui_table`, `ut_table`, and several spatial/geographic tables. The method also triggers TMA table migration, thesaurus structure updates, and appends concurrency columns to all tables, logging each major step to a debug file throughout execution.

##### fix_invalid_geometries(self)

Repair invalid geometries in all geometry tables.
Uses SpatiaLite's MakeValid() or ST_MakeValid() function.
Returns a dict with counts of fixed geometries per table.

##### rebuild_geometry_tables(self)

Rebuild geometry tables with correct column types (TEXT instead of INT).
This fixes JOIN issues with views that expect TEXT columns.

### ResultWrapper

Wrapper to maintain compatibility with old engine.execute() API

#### Methods

##### __init__(self, rows)

Initializes a `ResultWrapper` instance by converting the provided `rows` argument into a list and storing it in `self._rows`; if `rows` is falsy, `self._rows` defaults to an empty list. Also sets `self._index` to `0`.

##### fetchall(self)

*No description available.*
Returns all rows stored in the result set as a list. The returned value is the complete `_rows` collection, regardless of the current cursor position tracked by `_index`. No advancement of the internal index occurs when this method is called.

##### fetchone(self)

*No description available.*
Returns the next row from `_rows` at the current `_index` position, then increments `_index` by one. If `_index` is at or beyond the end of `_rows`, the method returns `None`.

##### __iter__(self)

*No description available.*
Returns an iterator over the internal `_rows` collection. This method enables the object to be used directly in iteration contexts such as `for` loops or any construct that expects an iterable. It delegates iteration to Python's built-in `iter()` function applied to `_rows`.

## Functions

### log_debug(msg)

*No description available.*
A nested helper function defined within `update_table()` that appends a timestamped debug message to a fixed log file located at `/Users/enzo/pyarchinit_debug.log`. Each log entry is formatted as `[YYYY-MM-DD HH:MM:SS.mmm] [DB_UPDATE] <msg>`, with the file opened in append mode using UTF-8 encoding and flushed immediately after writing. All exceptions raised during the logging operation are silently suppressed.

**Parameters:**
- `msg`

### safe_load_table(table_name)

Carica una tabella gestendo errori di encoding UTF-8

**Parameters:**
- `table_name`

### safe_load_table(table_name)

Load a table handling encoding errors

**Parameters:**
- `table_name`

