# scripts/fixes/fix_databases_aggressive.py

## Overview

This file contains 9 documented elements.

## Functions

### aggressive_fix_database(db_path)

Correzione aggressiva del database

**Parameters:**
- `db_path`

### table_exists(cursor, table_name)

Verifica se una tabella esiste

**Parameters:**
- `cursor`
- `table_name`

### fix_us_table(cursor)

Corregge us_table forzando area e us a TEXT

**Parameters:**
- `cursor`

### fix_table_fields(cursor, table_name)

Corregge i campi area/us in una tabella

**Parameters:**
- `cursor`
- `table_name`

### create_correct_views(cursor)

Crea le view corrette senza CAST

**Parameters:**
- `cursor`

### fix_views_with_cast(cursor)

Corregge le view che usano CAST

**Parameters:**
- `cursor`

### verify_final_state(cursor)

Verifica lo stato finale

**Parameters:**
- `cursor`

### process_databases()

Processa tutti i database

