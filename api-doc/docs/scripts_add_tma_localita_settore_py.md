# scripts/add_tma_localita_settore.py

## Overview

This file contains 3 documented elements.

## Functions

### check_column_exists(cursor, table_name, column_name)

Check if a column exists in a table.

**Parameters:**
- `cursor`
- `table_name`
- `column_name`

### main()

Locates the `pyarchinit_db.sqlite` SQLite database, first at the default QGIS3 plugin profile path and then at a fallback path relative to the current file, returning `1` if the database cannot be found. Connects to the database and conditionally adds the `localita` and `settore` TEXT columns to the `tma_materiali_archeologici` table if either column is absent, committing the changes and verifying the resulting table structure. Returns `0` on success or `1` if the target table does not exist, a migration step fails, or an `sqlite3.Error` is raised, rolling back the transaction in the latter case.

