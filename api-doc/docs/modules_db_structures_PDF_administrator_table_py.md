# modules/db/structures/PDF_administrator_table.py

## Overview

This file contains 2 documented elements.

## Classes

### PDF_administrator_table

*No description available.*
Defines the SQLAlchemy table schema for `pdf_administrator_table`, which stores PDF layout configuration records for named database tables. Each record holds a table name, a grid schema (`schema_griglia`), a cell-merge schema (`schema_fusione_celle`), and a model identifier (`modello`), with a composite unique constraint enforced on the combination of `table_name` and `modello`. The class uses SQLAlchemy's `MetaData` and `Table` constructs to declare the schema without creating the table at import time.

