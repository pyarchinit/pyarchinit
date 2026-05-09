# scripts/insert_ldct_from_excel.py

## Overview

This file contains 3 documented elements.

## Functions

### insert_ldct_values(cursor)

Inserisce i valori ldct dal file Excel.

**Parameters:**
- `cursor`

### main()

*No description available.*
Connects to a SQLite database at a hardcoded path (`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`) and invokes `insert_ldct_values` to populate thesaurus entries for the `ldct` (Tipologia collocazione) category. If the database file does not exist, the function prints an error message and returns `1` without proceeding. On success, it commits the transaction and prints a verification listing of all inserted records where `tipologia_sigla = '10.2'`; on `sqlite3.Error`, it rolls back the transaction and returns `1`, otherwise returning `0`.

