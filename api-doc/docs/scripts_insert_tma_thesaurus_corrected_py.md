# scripts/insert_tma_thesaurus_corrected.py

## Overview

This file contains 3 documented elements.

## Functions

### insert_thesaurus_values(cursor, nome_tabella, lingua)

Insert thesaurus values into database.

**Parameters:**
- `cursor`
- `nome_tabella`
- `lingua`

### main()

*No description available.*
Locates the PyArchInit SQLite database by checking the default QGIS3 profile path first, then falling back to the plugin directory if the primary path does not exist. It connects to the database, verifies that the `pyarchinit_thesaurus_sigle` table exists, and calls `insert_thesaurus_values` twice to populate thesaurus entries for the `TMA materiali archeologici` and `TMA materiali ripetibili` tables with Italian-language values. Returns `0` on success or `1` if the database is not found, the required table is missing, or an `sqlite3.Error` is raised during insertion.

