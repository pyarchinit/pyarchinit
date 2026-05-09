# modules/utility/debug_config.py

## Overview

This file contains 6 documented elements.

## Functions

### debug_print()

Print debug message if DEBUG is enabled.

Args:
    *args: Arguments to print
    category: Optional category for fine-grained control
    **kwargs: Additional kwargs passed to print

### set_debug(enabled)

Enable or disable global debug output.

**Parameters:**
- `enabled: bool`

### set_debug_category(category, enabled)

Enable or disable a specific debug category.

**Parameters:**
- `category: str`
- `enabled: bool`

### enable_all_debug()

Enable all debug output.

### disable_all_debug()

Disable all debug output.

