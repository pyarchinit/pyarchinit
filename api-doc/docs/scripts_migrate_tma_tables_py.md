# scripts/migrate_tma_tables.py

## Overview

This file contains 2 documented elements.

## Functions

### main()

Performs a schema migration on the `tma_materiali_archeologici` and `tma_materiali_ripetibili` tables within the pyarchinit QGIS plugin SQLite database located at the default macOS profile path. The function connects to the database, reads and reports the count of existing records in both tables, drops them, and recreates them with an updated column structure, committing the changes on success or rolling back on a `sqlite3.Error`. Existing data is not migrated to the new schema; the function only reports record counts before dropping the tables.

