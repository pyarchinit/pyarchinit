# modules/db/structures_metadata/pysito_polygon.py

## Overview

This file contains 3 documented elements.

## Classes

### pysito_polygon

*No description available.*
A SQLAlchemy table-definition class representing the `pyarchinit_siti_polygonal` vector layer, which stores polygonal representations of archaeological sites. It exposes a single class method, `define_table`, that inspects the active database connection string to branch between SQLite/SpatiaLite and PostgreSQL/PostGIS backends, returning the appropriate `Table` object bound to the supplied `metadata`. In both branches the table is defined with a single `gid` integer primary key column; geometry column handling is noted in comments but not implemented in the visible source.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object representing the `pyarchinit_siti_polygonal` database table, which stores polygonal representations of archaeological sites. The method inspects the active database connection string to determine the backend type (SQLite/SpatiaLite or PostgreSQL/PostGIS) and constructs the table definition accordingly. In both cases, the table is defined with a single `gid` integer primary key column.

