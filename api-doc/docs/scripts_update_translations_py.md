# scripts/update_translations.py

## Overview

This file contains 6 documented elements.

## Functions

### find_files(patterns, base_dir)

Trova tutti i file che corrispondono ai pattern.

**Parameters:**
- `patterns`
- `base_dir`

### update_with_pylupdate5()

Usa pylupdate5 con il file .pro (metodo tradizionale).

### update_with_pylupdate6()

Usa pylupdate6 con sintassi nuova (Qt6).

### compile_translations()

Compila i file .ts in .qm usando lrelease.

### main()

*No description available.*
Entry point for the PyArchInit translation update script. Parses the `--qt6` command-line argument to determine whether to invoke `update_with_pylupdate6()` or `update_with_pylupdate5()` for updating `.ts` translation source files, then calls `compile_translations()` to compile the resulting `.qm` files. Returns `0` on success or `1` if the translation update step fails.

