# scripts/debug_tma_thesaurus.py

## Overview

This file contains 3 documented elements.

## Functions

### debug_thesaurus(db_path)

Debug completo del thesaurus.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point of the script that verifies the existence of a SQLite database at the hardcoded path `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite` and, if found, invokes `debug_thesaurus()` against it. Prints a header labeled `"Debug completo thesaurus TMA"` followed by a success or failure message depending on the return value of `debug_thesaurus()`. Returns `0` on success or `1` if the database file is not found or if `debug_thesaurus()` fails.

