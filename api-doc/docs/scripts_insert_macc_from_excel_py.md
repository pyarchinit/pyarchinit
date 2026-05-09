# scripts/insert_macc_from_excel.py

## Overview

This file contains 3 documented elements.

## Functions

### insert_macc_values(cursor)

Inserisce i valori macc dal file Excel.

**Parameters:**
- `cursor`

### main()

*No description available.*
Entry point that connects to a hardcoded SQLite database at a fixed local path and invokes `insert_macc_values` to populate the `pyarchinit_thesaurus_sigle` table with `macc` category values. On success, it commits the transaction and prints a verification query of all rows where `tipologia_sigla` equals `'10.10'`; on `sqlite3.Error`, it rolls back the transaction and returns `1`. Returns `0` on successful completion or `1` if the database file is not found or an error occurs.

