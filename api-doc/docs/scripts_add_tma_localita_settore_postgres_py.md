# scripts/add_tma_localita_settore_postgres.py

## Overview

This file contains 3 documented elements.

## Functions

### check_column_exists(cursor, table_name, column_name)

Check if a column exists in a PostgreSQL table.

**Parameters:**
- `cursor`
- `table_name`
- `column_name`

### main()

*No description available.*
Connects to a PostgreSQL database and performs a schema migration on the `tma_materiali_archeologici` table by adding the `localita` and `settore` TEXT columns if they do not already exist. Connection parameters default to `localhost`, port `5432`, database `pyarchinit`, and user/password `postgres`, but can be overridden via command-line arguments in the order: host, database name, user, and password. Returns `0` on success or if no migration is needed, and `1` if the target table does not exist, if verification of the added columns fails, or if a database or general exception is raised.

