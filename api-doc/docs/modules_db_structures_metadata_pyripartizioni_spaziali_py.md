# modules/db/structures_metadata/pyripartizioni_spaziali.py

## Overview

This file contains 3 documented elements.

## Classes

### pyripartizioni_spaziali

*No description available.*
A SQLAlchemy table-definition class representing the `pyarchinit_ripartizioni_spaziali` vector layer, which stores spatial partition records in archaeological contexts. The class exposes a single `define_table` classmethod that inspects the active database connection string to branch between SQLite/SpatiaLite and PostgreSQL/PostGIS backends, returning the appropriate `Table` object bound to the supplied `metadata`. In both cases the table is defined with a single `gid` integer primary-key column; geometry handling differences between backends are noted in the source but not yet fully implemented.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object representing the `pyarchinit_ripartizioni_spaziali` database table, adapting its definition based on the active database backend. The method inspects the connection string to distinguish between SQLite/SpatiaLite and PostgreSQL/PostGIS environments. In both cases, the resulting table includes a single `gid` integer column designated as the primary key.

