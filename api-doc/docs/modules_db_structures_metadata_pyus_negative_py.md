# modules/db/structures_metadata/pyus_negative.py

## Overview

This file contains 3 documented elements.

## Classes

### pyus_negative

*No description available.*
A SQLAlchemy model class representing the `pyarchinit_us_negative_doc` database table, which stores vector layer data for negative archaeological units and their associated documentation. The class provides a `define_table` classmethod that dynamically constructs the table definition against the supplied `metadata` object, with branching logic to handle either SQLite/SpatiaLite or PostgreSQL/PostGIS connection strings. In both cases, the resulting table contains a single `gid` integer primary key column as defined in the source.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object representing the `pyarchinit_us_negative_doc` database table, which stores records for negative archaeological units. The method inspects the active database connection string to determine the underlying database engine (SQLite/SpatiaLite or PostgreSQL/PostGIS) and constructs the table definition accordingly. In both cases, the resulting table includes a single `gid` integer primary key column bound to the supplied `metadata` object.

