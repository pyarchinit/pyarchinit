# scripts/insert_dtzg_from_excel.py

## Overview

This file contains 3 documented elements.

## Functions

### insert_dtzg_values(cursor)

Inserisce i valori dtzg dal file Excel.

**Parameters:**
- `cursor`

### main()

*No description available.*
Entry point that connects to a hardcoded SQLite database at `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite` and invokes `insert_dtzg_values` to populate chronological range (`dtzg`) entries in the `pyarchinit_thesaurus_sigle` table. After committing the transaction, it executes two verification queries to count inserted records whose `sigla_estesa` field contains `'Neolitico'` or `'Minoico'` respectively, then prints a summary breakdown. Returns `0` on success or `1` if the database file is not found or an `sqlite3.Error` is raised, rolling back the transaction in the latter case.

