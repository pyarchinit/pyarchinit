# modules/utility/correggere_macc.py

## Overview

This file contains 6 documented elements.

## Functions

### find_db_from_loaded_layer(table_name)

Se la layer è caricata, prova a estrarre il path dal datasource.

**Parameters:**
- `table_name`

### msg(txt, level)

Messaggi su console e (se disponibile) sulla message bar di QGIS.

**Parameters:**
- `txt`
- `level`

### backup_db(path)

Crea un backup del db con timestamp nella stessa cartella.

**Parameters:**
- `path`

### table_info(conn, table)

*No description available.*
Queries the SQLite `PRAGMA table_info` for the specified table using the provided database connection. Returns all rows from the result set as a list of tuples, each describing a column in the table (as returned by the SQLite pragma). This function does not perform any transformation on the raw pragma output.

**Parameters:**
- `conn`
- `table`

### fk_list(conn, table)

*No description available.*
Retrieves the foreign key constraints defined on the specified SQLite table by executing `PRAGMA foreign_key_list({table})` against the provided database connection. Returns all rows fetched from the pragma result as a list of tuples, each representing a foreign key relationship associated with the table.

**Parameters:**
- `conn`
- `table`

