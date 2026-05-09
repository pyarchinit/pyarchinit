# scripts/fix_thesaurus_quotes.py

## Overview

This file contains 3 documented elements.

## Functions

### fix_thesaurus_quotes(file_path)

Rimuove le virgolette extra nei parametri del thesaurus.

**Parameters:**
- `file_path`

### main()

*No description available.*
Entry point of the script that orchestrates the removal of extra quotation marks from the thesaurus section of a specific QGIS plugin file (`Tma.py`). It verifies that the target file exists, then delegates the fix operation to `fix_thesaurus_quotes()`, printing a success or failure message based on the result. Returns `0` on success or `1` if the file is not found or the fix operation fails.

