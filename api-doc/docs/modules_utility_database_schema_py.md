# modules/utility/database_schema.py

## Overview

This file contains 6 documented elements.

## Functions

### get_engine()

Get or create the database engine lazily

### get_metadata()

Get or create the metadata lazily

### create_all_tables()

Create all tables in the database - call explicitly when needed

### get_engine_compat()

*No description available.*
A backward-compatibility wrapper that delegates to `get_engine()` and returns its result. This function exists to preserve compatibility with older code that may have referenced a previous interface, while the underlying functionality has since been refactored into `get_engine()`. No additional logic or transformation is applied beyond the direct call to `get_engine()`.

### get_metadata_compat()

*No description available.*
A backward-compatibility wrapper that delegates directly to `get_metadata()`. This function exists to preserve compatibility with older code that relied on a previous interface, ensuring existing call sites continue to function without modification. It returns whatever `get_metadata()` returns; see that function's implementation for full details.

