# scripts/fixes/fix_all_insert_scripts.py

## Overview

This file contains 3 documented elements.

## Functions

### fix_script(filepath)

Corregge un singolo script di insert.

**Parameters:**
- `filepath`

### main()

Iterates over a predefined list of Python script filenames located in a hardcoded QGIS plugin directory and applies corrections to each file by calling `fix_script`. Prints a summary header showing the target directory, the number of scripts to process, the correct field-to-code mapping from `CORRECT_MAPPING`, and the correct table name from `CORRECT_TABLE_NAME`. Upon completion, reports how many scripts were successfully modified out of the total, and notes that original files are preserved with a `.backup` extension.

