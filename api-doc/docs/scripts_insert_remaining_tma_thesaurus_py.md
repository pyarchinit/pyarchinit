# scripts/insert_remaining_tma_thesaurus.py

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
Entry point that connects to a hardcoded SQLite database at `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite` and inserts remaining TMA thesaurus values for the Italian language (`lingua='it'`) into the `pyarchinit_thesaurus_sigle` table. Before performing any insertions, it verifies that the database file exists and that the target table is present, returning `1` on any failure condition or SQLite error. On success, it commits the transaction, prints a summary of inserted and skipped values, and returns `0`.

