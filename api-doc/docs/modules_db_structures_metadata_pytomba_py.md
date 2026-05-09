# modules/db/structures_metadata/pytomba.py

## Overview

This file contains 3 documented elements.

## Classes

### pytomba

*No description available.*
A SQLAlchemy table-definition class representing the `pyarchinit_tafonomia` vector layer, which stores taxonomy records related to archaeological contexts. It exposes a single class method, `define_table`, that accepts a SQLAlchemy `metadata` object and returns a `Table` instance configured for either SQLite/SpatiaLite or PostgreSQL/PostGIS backends, determined by inspecting the active connection string. In both cases, the resulting table contains a single defined column, `gid` (`Integer`, primary key), serving as the unique identifier for each taxonomy record.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object mapped to the `pyarchinit_tafonomia` database table using the provided `metadata` instance. The method inspects the active connection string to determine the database backend, branching between SQLite/SpatiaLite and PostgreSQL/PostGIS configurations. In both cases, the resulting table includes a single `gid` integer primary key column.

