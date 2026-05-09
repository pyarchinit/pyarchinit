# scripts/add_missing_categories.py

## Overview

This file contains 3 documented elements.

## Functions

### add_missing_categories(db_path)

Aggiunge le categorie mancanti.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point of the script that orchestrates the addition of missing TMA categories to a SQLite database located at a hardcoded path (`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`). It first verifies that the database file exists, then delegates the update operation to `add_missing_categories()`, printing a success or failure message based on the result. Returns `0` on success or `1` if the database is not found or the operation fails.

