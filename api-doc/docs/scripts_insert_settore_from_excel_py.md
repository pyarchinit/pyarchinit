# scripts/insert_settore_from_excel.py

## Overview

This file contains 3 documented elements.

## Functions

### insert_settore_values(cursor)

Inserisce i valori settore dal file Excel con relazioni alle aree.

**Parameters:**
- `cursor`

### main()

*No description available.*
Entry point of the script that connects to a hardcoded SQLite database located at `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite` and invokes `insert_settore_values` to populate sector values into the database. If the database file does not exist, the function prints an error message and returns `1` without proceeding. Upon successful insertion, it commits the transaction and prints a summary of inserted records grouped by parent area (`tipologia_sigla = '10.15'`), returning `0` on success or `1` on failure.

