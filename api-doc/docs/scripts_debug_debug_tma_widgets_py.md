# scripts/debug/debug_tma_widgets.py

## Overview

This file contains 6 documented elements.

## Functions

### check_thesaurus_data(cursor)

Check thesaurus data for correct nome_tabella values

**Parameters:**
- `cursor`

### test_localita_query(cursor)

Test the exact query used in filter_area_by_localita

**Parameters:**
- `cursor`

### check_hierarchy(cursor)

Check if hierarchy is properly set up

**Parameters:**
- `cursor`

### suggest_fixes(cursor)

Suggest SQL fixes if needed

**Parameters:**
- `cursor`

### main()

*No description available.*
Entry point for the TMA widget debugging utility. Connects to the pyarchinit SQLite database located at the default QGIS3 profile path (`~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite`), then sequentially executes `check_thesaurus_data`, `test_localita_query`, `check_hierarchy`, and `suggest_fixes` against the database cursor. Returns `0` on success or `1` if the database file is not found or an `sqlite3.Error` is raised during execution.

