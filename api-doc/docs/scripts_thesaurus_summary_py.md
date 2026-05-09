# scripts/thesaurus_summary.py

## Overview

This file contains 3 documented elements.

## Functions

### generate_summary(db_path)

Genera un riepilogo del thesaurus.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point of the script that verifies the existence of a SQLite database at a hardcoded path (`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`) and, if found, invokes `generate_summary()` to produce a Thesaurus TMA report. Prints a header and a success or failure message depending on the outcome of `generate_summary()`. Returns `0` on success or `1` if the database file is not found or if summary generation fails.

