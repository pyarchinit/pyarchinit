# scripts/add_sync_translations.py

## Overview

This file contains 6 documented elements.

## Functions

### generate_context_xml(lang_code)

Generate XML for the pyarchinitConfigDialog context with sync translations.

**Parameters:**
- `lang_code`

### escape_xml(text)

Escape special XML characters.

**Parameters:**
- `text`

### generate_message_xml(source, translation)

Generate XML for a single message.

**Parameters:**
- `source`
- `translation`

### add_translations_to_file(filepath, lang_code)

Add sync translations to a .ts file, merging with existing context.

**Parameters:**
- `filepath`
- `lang_code`

### main()

Main function.

