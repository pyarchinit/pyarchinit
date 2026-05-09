# scripts/update_fauna_translations.py

## Overview

This file contains 4 documented elements.

## Functions

### escape_xml(text)

Escape special XML characters.

**Parameters:**
- `text`

### update_ts_file(lang_code)

Update a single .ts file with Fauna translations.

**Parameters:**
- `lang_code`

### main()

*No description available.*
Entry point of the script that orchestrates the update of translation files for all languages defined in `TARGET_LANGUAGES`. It iterates over each target language, calls `update_ts_file()` for each one, and accumulates the total number of updated translations. Upon completion, it prints a summary of the total updates and instructs the user to run `lrelease` to compile the resulting `.qm` files.

