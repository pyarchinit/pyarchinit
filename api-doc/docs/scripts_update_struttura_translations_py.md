# scripts/update_struttura_translations.py

## Overview

This file contains 4 documented elements.

## Functions

### escape_xml(text)

Escape special XML characters.

**Parameters:**
- `text`

### update_ts_file(lang_code)

Update a single .ts file with Struttura translations.

**Parameters:**
- `lang_code`

### main()

*No description available.*
Entry point of the script that orchestrates the update of "Struttura" tab translations across all target languages defined in `TARGET_LANGUAGES`. It iterates over each language, invoking `update_ts_file` for each one and accumulating the total number of updated translations. Progress and summary information are printed to standard output before and after processing.

