# scripts/insert_ftap_from_excel.py

## Overview

This file contains 3 documented elements.

## Functions

### insert_ftap_values(cursor)

Inserisce i valori ftap dal file Excel.

**Parameters:**
- `cursor`

### main()

*No description available.*
Connects to a SQLite database at a hardcoded path (`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`), verifies its existence, and invokes `insert_ftap_values` to populate photography-type (`ftap`) entries into the `pyarchinit_thesaurus_sigle` table. On success, it commits the transaction and prints a verification query of all inserted records where `tipologia_sigla = '10.12'`; on failure, it rolls back the transaction and prints the error. Returns `0` on success or `1` if the database is not found or a `sqlite3.Error` is raised.

