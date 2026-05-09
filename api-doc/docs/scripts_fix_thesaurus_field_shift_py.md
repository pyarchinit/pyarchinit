# scripts/fix_thesaurus_field_shift.py

## Overview

This file contains 3 documented elements.

## Functions

### fix_field_shift(db_path)

Corregge lo spostamento dei campi nel thesaurus.

**Parameters:**
- `db_path`

### main()

*No description available.*
Entry point for the thesaurus field-shift correction utility. It verifies the existence of a hardcoded SQLite database at `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`, then invokes `fix_field_shift()` to reassign the column values `tipologia_sigla → descrizione`, `lingua → tipologia_sigla`, and `order_layer → lingua`. Returns `0` on success or `1` if the database is not found or the fix operation fails.

