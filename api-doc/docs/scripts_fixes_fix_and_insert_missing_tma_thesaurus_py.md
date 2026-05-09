# scripts/fixes/fix_and_insert_missing_tma_thesaurus.py

## Overview

This file contains 4 documented elements.

## Functions

### insert_missing_thesaurus_data(cursor)

Inserisce i dati mancanti del thesaurus TMA.

**Parameters:**
- `cursor`

### verify_all_codes(cursor)

Verifica che tutti i codici necessari siano presenti.

**Parameters:**
- `cursor`

### main()

*No description available.*
Entry point of the script that connects to the pyarchinit SQLite database located at the default QGIS3 profile path (`~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite`). It calls `insert_missing_thesaurus_data` to insert missing TMA thesaurus entries and `verify_all_codes` to validate the results, then commits the transaction on success or rolls it back on `sqlite3.Error`. Returns `0` on success or `1` if the database file is not found or an error occurs.

