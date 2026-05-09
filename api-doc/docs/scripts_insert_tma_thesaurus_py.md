# scripts/insert_tma_thesaurus.py

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
Entry point that connects to a SQLite database at a hardcoded primary path (`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`), falling back to a secondary path relative to the plugin directory if the primary does not exist. It verifies that the `pyarchinit_thesaurus_sigle` table is present, then calls `insert_thesaurus_values` to insert Italian-language thesaurus entries, commits the transaction, and prints a summary of inserted and skipped values. Returns `0` on success or `1` if the database file is not found, the required table is absent, or a `sqlite3.Error` is raised.

