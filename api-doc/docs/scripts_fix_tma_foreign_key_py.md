# scripts/fix_tma_foreign_key.py

## Overview

This file contains 4 documented elements.

## Functions

### fix_foreign_key(file_path)

Corregge la foreign key per puntare alla tabella corretta.

**Parameters:**
- `file_path`

### check_tma_table_name()

Verifica il nome della tabella TMA principale.

### main()

*No description available.*
Verifies and corrects the foreign key reference in the `Tma_materiali_table.py` plugin file by checking whether the actual TMA table name matches the hardcoded reference `'tma_materiali_archeologici'`. If a mismatch is detected, the function creates a backup of the original file (with a `.backup_fk_fix` extension) and replaces the incorrect `ForeignKey('tma_materiali_archeologici.id')` reference with one pointing to the resolved table name. Returns `0` on successful completion or `1` if the target file is not found.

