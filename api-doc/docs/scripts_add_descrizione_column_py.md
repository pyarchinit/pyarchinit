# scripts/add_descrizione_column.py

## Overview

This file contains 3 documented elements.

## Functions

### add_descrizione_column(db_path)

Aggiunge la colonna descrizione se non esiste.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point of the script that orchestrates the addition of a `descrizione` column to the `pyarchinit_thesaurus_sigle` table in a SQLite database located at a hardcoded path (`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`). It first verifies that the database file exists, printing an error message and returning `1` if it does not, then delegates the column addition to `add_descrizione_column()`. Returns `0` on success or `1` on failure, and is intended to be invoked via `sys.exit()` when the script is run directly.

