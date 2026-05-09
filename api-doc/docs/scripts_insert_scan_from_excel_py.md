# scripts/insert_scan_from_excel.py

## Overview

This file contains 3 documented elements.

## Functions

### insert_scan_values(cursor)

Inserisce i valori scan dal file Excel.

**Parameters:**
- `cursor`

### main()

*No description available.*
Connects to a SQLite database located at a hardcoded path (`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite`) and invokes `insert_scan_values` to populate the `pyarchinit_thesaurus_sigle` table with excavation denomination values. After committing the transaction, it executes three verification queries to count inserted records associated with the sites Festòs, Haghia Triada (HTR), and Kamilari, then prints a summary breakdown by site. Returns `0` on success or `1` if the database file is not found or a `sqlite3.Error` is raised, rolling back the transaction in the latter case.

