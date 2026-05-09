# modules/db/structures_metadata/PDF_administrator_table.py

## Overview

This file contains 2 documented elements.

## Classes

### PDF_administrator_table

*No description available.*
Defines the SQLAlchemy table metadata for the `pdf_administrator_table` database table, which stores PDF layout configuration records. Each record holds a table name, a grid schema (`schema_griglia`), a cell-merge schema (`schema_fusione_celle`), and a model identifier (`modello`), with a composite unique constraint enforced on the `table_name` and `modello` columns. The class uses a module-level `MetaData` instance and relies on `Connection` from `modules.db.pyarchinit_conn_strings`; table creation is intentionally deferred and not performed at import time.

