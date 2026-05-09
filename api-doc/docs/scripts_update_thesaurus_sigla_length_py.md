# scripts/update_thesaurus_sigla_length.py

## Overview

This file contains 4 documented elements.

## Functions

### update_sigla_length_sqlite(db_path)

Aggiorna la lunghezza del campo sigla per SQLite.

**Parameters:**
- `db_path`

### create_postgres_update_script()

Crea script SQL per PostgreSQL.

### main()

*No description available.*
Entry point of the script that orchestrates the update of the `sigla` and `parent_sigla` field lengths in the `pyarchinit_thesaurus_sigle` table from `VARCHAR(3)` to `VARCHAR(100)` within a hardcoded SQLite database located at `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`. If the database file exists, it prints the current table structure for the affected columns, invokes `update_sigla_length_sqlite()` to apply the schema change, then verifies the updated structure and total record count; if the file is not found, it prints a not-found message. Finally, it calls `create_postgres_update_script()` to generate an equivalent SQL script for PostgreSQL environments.

