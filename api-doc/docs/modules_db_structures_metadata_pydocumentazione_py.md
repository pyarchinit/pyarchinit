# modules/db/structures_metadata/pydocumentazione.py

## Overview

This file contains 3 documented elements.

## Classes

### pydocumentazione

*No description available.*
A data model class representing the `pyarchinit_documentazione` vector layer, which stores archaeological documentation records. The `define_table` classmethod dynamically constructs a SQLAlchemy `Table` object bound to the provided `metadata`, adapting its definition based on the active database backend (SQLite/SpatiaLite or PostgreSQL/PostGIS). In both cases, the resulting table includes a single `gid` integer primary key column as the unique identifier for each documentation record.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object for the `pyarchinit_documentazione` table using the provided `metadata` instance. The method inspects the active database connection string to determine the backend type, branching between SQLite/SpatiaLite and PostgreSQL/PostGIS configurations. In both cases, the resulting table includes a single `gid` integer primary key column.

