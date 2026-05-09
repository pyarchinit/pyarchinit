# scripts/clean_source_thesaurus.py

## Overview

This file contains 3 documented elements.

## Functions

### clean_source_database(db_type, conn_params)

Pulisce i duplicati nel database sorgente.

**Parameters:**
- `db_type`
- `conn_params`

### main()

*No description available.*
Entry point for the thesaurus source database cleanup utility. Prompts the user to select a database type (PostgreSQL or SQLite), collects the required connection parameters interactively, and invokes `clean_source_database()` against the specified source database before an export operation. Returns `0` on success or `1` on failure, including invalid input or a failed cleanup.

