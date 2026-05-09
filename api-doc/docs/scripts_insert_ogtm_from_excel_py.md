# scripts/insert_ogtm_from_excel.py

## Overview

This file contains 3 documented elements.

## Functions

### insert_ogtm_values(cursor)

Inserisce i valori ogtm dal file Excel.

**Parameters:**
- `cursor`

### main()

*No description available.*
Entry point that connects to a hardcoded SQLite database at a fixed file path and invokes `insert_ogtm_values` to populate the `pyarchinit_thesaurus_sigle` table with `ogtm` typology records. On success, it commits the transaction and prints a verification summary of all inserted rows queried by `sigla`, `sigla_estesa`, and `descrizione`; on `sqlite3.Error`, it rolls back the transaction. Returns `0` on success or `1` if the database file is not found or an error occurs.

