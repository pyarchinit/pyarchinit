# scripts/check_tma_data.py

## Overview

This file contains 3 documented elements.

## Functions

### check_tma_data(db_path)

Verifica i dati nelle tabelle TMA.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point of the script that initializes a hardcoded SQLite database path (`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`) and invokes `check_tma_data` against it. Prints a header labeled "Verifica dati TMA" before delegating execution to the data-check routine. Returns `0` upon completion, intended to be passed directly to `sys.exit()`.

