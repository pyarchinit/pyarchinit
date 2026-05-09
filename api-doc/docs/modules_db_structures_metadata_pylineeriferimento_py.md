# modules/db/structures_metadata/pylineeriferimento.py

## Overview

This file contains 3 documented elements.

## Classes

### pylineeriferimento

*No description available.*
Defines the SQLAlchemy table structure for the `pyarchinit_linee_rif` reference line vector layer used within the pyarchinit system. The class exposes a single class method, `define_table`, which inspects the active database connection string to determine the target backend (SQLite/SpatiaLite or PostgreSQL/PostGIS) and returns the corresponding `Table` object bound to the provided `metadata`. In both supported backends, the table is defined with a single `gid` integer primary key column.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object representing the `pyarchinit_linee_rif` reference line table, bound to the provided `metadata` instance. The method inspects the active database connection string to determine the underlying database engine (SQLite/SpatiaLite or PostgreSQL/PostGIS) and constructs the table definition accordingly. In both cases, the table is defined with a single `gid` integer primary key column.

