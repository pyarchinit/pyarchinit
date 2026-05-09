# scripts/insert_macl_from_excel.py

## Overview

This file contains 3 documented elements.

## Functions

### insert_macl_values(cursor)

Inserisce i valori macl dal file Excel.

**Parameters:**
- `cursor`

### main()

*No description available.*
Entry point that connects to a hardcoded SQLite database at `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite` and invokes `insert_macl_values` to populate thesaurus records for the `macl` (Classe) category. After committing the transaction, it queries and prints all inserted rows from `pyarchinit_thesaurus_sigle` where `tipologia_sigla` equals `'10.11'` as a verification step. Returns `0` on success or `1` if the database file is not found or a `sqlite3.Error` is raised, rolling back the transaction in the latter case.

