# scripts/update_thesaurus_hierarchy.py

## Overview

This file contains 5 documented elements.

## Functions

### add_hierarchy_fields(cursor)

Aggiunge i campi per la gerarchia se non esistono.

**Parameters:**
- `cursor`

### clear_tma_thesaurus(cursor)

Rimuove i dati esistenti del thesaurus TMA per reimportarli con gerarchia.

**Parameters:**
- `cursor`

### insert_hierarchical_data(cursor)

Inserisce i dati con relazioni gerarchiche.

**Parameters:**
- `cursor`

### main()

*No description available.*
Entry point for the thesaurus hierarchy update script. Connects to a SQLite database at a hardcoded path, then sequentially calls `add_hierarchy_fields`, `clear_tma_thesaurus`, and `insert_hierarchical_data` to restructure the thesaurus table so that it supports a three-level locality → area → sector hierarchy. Returns `0` on success or `1` if the database file is not found or an `sqlite3.Error` is raised during execution, rolling back any uncommitted changes in the latter case.

