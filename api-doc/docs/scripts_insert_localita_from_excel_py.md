# scripts/insert_localita_from_excel.py

## Overview

This file contains 3 documented elements.

## Functions

### insert_localita_values(cursor)

Inserisce i valori località dal file Excel.

**Parameters:**
- `cursor`

### main()

*No description available.*
Connects to a SQLite database at a hardcoded path (`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`), verifies its existence, and invokes `insert_localita_values` to populate locality entries, committing the transaction on success or rolling it back on `sqlite3.Error`. After insertion, it queries the `pyarchinit_thesaurus_sigle` table for all records where `tipologia_sigla` equals `'10.3'` and prints them as a verification step. Returns `0` on success or `1` if the database file is not found or a database error occurs.

