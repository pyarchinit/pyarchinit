# modules/db/structures_metadata/pyunitastratigrafiche_usm.py

## Overview

This file contains 3 documented elements.

## Classes

### pyunitastratigrafiche_usm

*No description available.*
A SQLAlchemy table definition class representing vertical stratigraphic units (USM) in archaeological contexts. The `define_table` classmethod constructs and returns a SQLAlchemy `Table` object named `'pyunitastratigrafiche_usm'`, adapting its definition based on the active database backend — either SQLite/SpatiaLite or PostgreSQL/PostGIS — as determined by the connection string retrieved from `Connection`. In both cases, the table is defined with a single `gid` integer primary key column; any additional geometry or measurement columns are not documented in source.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object for the `pyunitastratigrafiche_usm` table using the provided `metadata` instance. The method inspects the active connection string to determine the database backend (SQLite/SpatiaLite or PostgreSQL/PostGIS) and constructs the table definition accordingly. In both cases, the resulting table contains a single `gid` integer column designated as the primary key.

