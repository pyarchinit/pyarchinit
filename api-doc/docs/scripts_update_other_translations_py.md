# scripts/update_other_translations.py

## Overview

This file contains 4 documented elements.

## Functions

### escape_xml(text)

Escape special XML characters.

**Parameters:**
- `text`

### update_ts_file(lang_code)

Update a single .ts file with translations.

**Parameters:**
- `lang_code`

### main()

*No description available.*
Entry point of the script that orchestrates the update of Sam, Pottery, and Tma translations across all target languages defined in `TARGET_LANGUAGES`. It iterates over each language, invoking `update_ts_file()` for each one and accumulating the total number of updated translation entries. Progress and summary information are printed to standard output, including a final count of all translations updated across all languages.

