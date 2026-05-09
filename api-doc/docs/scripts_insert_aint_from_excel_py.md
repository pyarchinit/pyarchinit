# scripts/insert_aint_from_excel.py

## Overview

This file contains 3 documented elements.

## Functions

### insert_aint_values(cursor)

Inserisce i valori aint dal file Excel.

**Parameters:**
- `cursor`

### main()

*No description available.*
Entry point that connects to a hardcoded SQLite database at a fixed local path and invokes `insert_aint_values` to populate acquisition-type (`aint`) entries in the `pyarchinit_thesaurus_sigle` table. On success, it commits the transaction and prints a verification listing of all rows where `tipologia_sigla` equals `'10.6'`; on `sqlite3.Error`, it rolls back and returns `1`. Returns `0` on successful completion or `1` if the database file is not found or an error occurs.

