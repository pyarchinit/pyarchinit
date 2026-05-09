# scripts/recreate_thesaurus_correct_order.py

## Overview

This file contains 3 documented elements.

## Functions

### recreate_thesaurus_table(db_path)

Ricrea la tabella con l'ordine corretto delle colonne.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point for the thesaurus table recreation utility. Verifies the existence of a SQLite database at a hardcoded path (`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`), then invokes `recreate_thesaurus_table()` to rebuild the `thesaurus` table with the correct column order. Returns `0` on success or `1` if the database file is not found or the recreation process fails.

