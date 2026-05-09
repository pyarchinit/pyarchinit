# scripts/verify_tma_persistence.py

## Overview

This file contains 4 documented elements.

## Functions

### monitor_tma_data(db_path, interval, duration)

Monitora i dati TMA per vedere se vengono cancellati.

**Parameters:**
- `db_path`
- `interval`
- `duration`

### show_final_state(db_path)

Mostra lo stato finale del database.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point for the TMA data persistence verification utility. It initializes a hardcoded SQLite database path, prints step-by-step instructions for the user to follow in QGIS, then invokes `monitor_tma_data` to poll the database at 1-second intervals for 30 seconds, followed by a call to `show_final_state` to display the final database state. Returns `0` on completion and is intended to be executed directly via `sys.exit(main())`.

