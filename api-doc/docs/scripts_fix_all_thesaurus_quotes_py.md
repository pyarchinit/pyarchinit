# scripts/fix_all_thesaurus_quotes.py

## Overview

This file contains 3 documented elements.

## Functions

### fix_all_quotes(file_path)

Rimuove tutte le virgolette extra.

**Parameters:**
- `file_path`

### main()

*No description available.*
Entry point of the script that targets a hardcoded file path within the QGIS `pyarchinit` plugin directory (`Tma.py`). It verifies the file exists, then invokes `fix_all_quotes()` to remove all extra quotation marks from the file, printing progress and result messages to standard output. Returns `0` on success or `1` if the file is not found or the fix operation fails, with the return value passed to `sys.exit()` when the script is run directly.

