# scripts/fix_tma_deletion_issue.py

## Overview

This file contains 3 documented elements.

## Functions

### check_foreign_keys(db_path)

Verifica lo stato delle foreign keys.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point of the script that targets a hardcoded SQLite database located at `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`. It prints a header describing the operation ("Fix problema cancellazione materiali TMA") and delegates execution to `check_foreign_keys`, passing the database path. Returns `0` upon completion and is intended to be invoked via `sys.exit(main())` when the module is run directly.

