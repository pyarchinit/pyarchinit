# scripts/map_thesaurus_types.py

## Overview

This file contains 3 documented elements.

## Functions

### map_thesaurus_types(db_path)

Mappa i tipi del thesaurus secondo la logica corretta.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point of the script that orchestrates the thesaurus TMA type mapping process against a SQLite database located at a hardcoded path (`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`). It first verifies that the database file exists, then delegates the mapping operation to `map_thesaurus_types()`, printing a success or failure message based on the result. Returns `0` on success or `1` if the database is not found or the mapping process fails.

