# scripts/trace_tma_deletion.py

## Overview

This file contains 4 documented elements.

## Functions

### add_deletion_traces(file_path)

Aggiunge log per tracciare le cancellazioni.

**Parameters:**
- `file_path`

### check_initialization_flow(file_path)

Controlla il flusso di inizializzazione.

**Parameters:**
- `file_path`

### main()

*No description available.*
Entry point of the script that orchestrates the addition of deletion traces to the TMA plugin file located at a hardcoded path within the QGIS3 user profile directory. It verifies the target file exists, then sequentially calls `add_deletion_traces` and `check_initialization_flow` on that file, printing status messages to indicate success or failure. Returns `0` on success or `1` if the file is not found or `add_deletion_traces` fails, with the return value passed to `sys.exit` when the script is run directly.

