# scripts/insert_cronologia_from_excel.py

## Overview

This file contains 3 documented elements.

## Functions

### insert_cronologia_values(cursor)

Inserisce i valori cronologia dal file Excel.

**Parameters:**
- `cursor`

### main()

*No description available.*
Connects to a SQLite database located at a hardcoded path (`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`) and invokes `insert_cronologia_values` to populate chronology entries into the `pyarchinit_thesaurus_sigle` table. If the database file does not exist, the function exits early with a return code of `1`; otherwise, it commits the transaction and prints a summary of total inserted values along with counts filtered by "Neolitico" and "Minoico" periods. Returns `0` on success or `1` if the database is not found or a `sqlite3.Error` is raised, in which case the transaction is rolled back.

