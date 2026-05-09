# scripts/clean_and_insert_real_tma_thesaurus.py

## Overview

This file contains 4 documented elements.

## Functions

### clean_existing_data(cursor)

Rimuove tutti i dati esistenti del thesaurus TMA.

**Parameters:**
- `cursor`

### insert_tma_thesaurus_data(cursor)

Inserisce i dati reali del thesaurus TMA.

**Parameters:**
- `cursor`

### main()

*No description available.*
Entry point that connects to a SQLite database at a hardcoded path and orchestrates the cleaning and reinsertion of TMA thesaurus data. It calls `clean_existing_data` to remove existing records, then `insert_tma_thesaurus_data` to populate the `pyarchinit_thesaurus_sigle` table, and commits the transaction upon success or rolls it back on `sqlite3.Error`. After a successful operation, it prints a summary of inserted records grouped by `tipologia_sigla`, returning `0` on success or `1` on failure.

