# scripts/clean_thesaurus_values.py

## Overview

This file contains 3 documented elements.

## Functions

### clean_thesaurus_values(db_path)

Pulisce i valori None e sistema le tipologie.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point of the script that orchestrates the thesaurus cleaning process against a hardcoded SQLite database located at `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`. It verifies the database file exists before invoking `clean_thesaurus_values()`, printing a success or failure message based on the result. Returns `0` on success or `1` if the database file is not found or the cleaning process fails.

