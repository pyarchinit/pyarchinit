# scripts/insert_macp_from_excel.py

## Overview

This file contains 3 documented elements.

## Functions

### insert_macp_values(cursor)

Inserisce i valori macp dal file Excel.

**Parameters:**
- `cursor`

### main()

*No description available.*
Entry point that connects to a hardcoded SQLite database at a fixed file path and invokes `insert_macp_values` to populate the `pyarchinit_thesaurus_sigle` table with typological precision values (`tipologia_sigla = '10.12'` and `'10.9'`). After committing the transaction, it queries the database to report a breakdown of inserted records by style category (Kamares, Haghios Onouphrios, and other styles). Returns `0` on success or `1` if the database file is not found or a `sqlite3.Error` is raised, rolling back the transaction in the latter case.

