# scripts/insert_macd_from_excel.py

## Overview

This file contains 3 documented elements.

## Functions

### insert_macd_values(cursor)

Inserisce i valori macd dal file Excel.

**Parameters:**
- `cursor`

### main()

*No description available.*
Connects to a SQLite database at a hardcoded path (`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`) and invokes `insert_macd_values` to populate the `pyarchinit_thesaurus_sigle` table with MACD definition values. After committing the transaction, it queries the table to produce a summary count broken down into cups/bowls (`coppa`/`tazza`), various vessels (`vaso`), and other types, all filtered by `tipologia_sigla = '10.13'`. Returns `0` on success, `1` if the database file is not found or an `sqlite3.Error` is raised, rolling back the transaction in the latter case.

