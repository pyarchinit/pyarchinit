# scripts/fix_thesaurus_duplicates_advanced.py

## Overview

This file contains 4 documented elements.

## Functions

### analyze_and_fix_postgres(host, port, dbname, user, password)

Analizza e rimuove tutti i duplicati da PostgreSQL.

**Parameters:**
- `host`
- `port`
- `dbname`
- `user`
- `password`

### analyze_and_fix_sqlite(db_path)

Analizza e rimuove tutti i duplicati da SQLite.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point for the advanced thesaurus duplicate-cleaning utility. Displays an introductory banner describing the deduplication logic (uniqueness key: `lingua`, `nome_tabella`, `tipologia_sigla`, `sigla_estesa`; lowest ID retained per group), then prompts the user to select a database type — either SQLite (option `1`) or PostgreSQL (option `2`) — and collects the corresponding connection parameters. Delegates execution to `analyze_and_fix_sqlite` or `analyze_and_fix_postgres` based on the selection, returning `0` on success or `1` on failure or invalid input.

