# scripts/clean_tma_thesaurus.py

## Overview

This file contains 3 documented elements.

## Functions

### clean_tma_thesaurus(db_path)

Pulisce e corregge il thesaurus TMA.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point for the TMA thesaurus cleaning utility. Verifies the existence of a hardcoded SQLite database file at `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`, then invokes `clean_tma_thesaurus()` against that path, printing a success or failure message based on the result. Returns `0` on success or `1` if the database file is not found or the cleaning process fails.

