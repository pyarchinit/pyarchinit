# scripts/fix_tma_thesaurus_codes.py

## Overview

This file contains 3 documented elements.

## Functions

### fix_thesaurus_codes(file_path)

Corregge i codici thesaurus nel file Tma.py.

**Parameters:**
- `file_path`

### main()

*No description available.*
Entry point of the script that orchestrates the correction of `tipologia_sigla` thesaurus codes in the file `Tma.py` located at a hardcoded path within the QGIS3 pyarchinit plugin directory. It verifies the target file exists, invokes `fix_thesaurus_codes()` on it, and prints a success or failure message accordingly. Returns `0` on success or `1` if the file is not found or the fix process fails.

