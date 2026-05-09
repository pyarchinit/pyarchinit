# scripts/insert_saggio_vano_from_excel.py

## Overview

This file contains 4 documented elements.

## Functions

### insert_saggio_values(cursor)

Inserisce valori di esempio per saggio.

**Parameters:**
- `cursor`

### insert_vano_values(cursor)

Inserisce valori di esempio per vano/locus.

**Parameters:**
- `cursor`

### main()

*No description available.*
Connects to a SQLite database at a hardcoded path (`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`) and invokes `insert_saggio_values` and `insert_vano_values` to populate the `pyarchinit_thesaurus_sigle` table, committing the transaction on success or rolling it back on `sqlite3.Error`. After insertion, it executes three verification queries against the same table to report the total counts of records with `tipologia_sigla = '10.2'`, filtered respectively for all entries, those with `sigla LIKE 'VANO%'`, and those with `sigla LIKE 'LOC%'`. Returns `0` on success or `1` if the database file is not found or a database error occurs.

