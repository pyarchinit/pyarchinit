# modules/db/structures_metadata/pyindividui.py

## Overview

This file contains 3 documented elements.

## Classes

### pyindividui

*No description available.*
A SQLAlchemy table definition class representing the `pyarchinit_individui` vector layer for individual records. It exposes a single class method, `define_table`, which inspects the active database connection string to determine the target database backend (SQLite/SpatiaLite or PostgreSQL/PostGIS) and returns the corresponding `Table` object bound to the supplied `metadata`. In both supported backends, the table is defined with a single column, `gid`, serving as the integer primary key.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object for the `pyarchinit_individui` table using the provided `metadata` instance. The method inspects the active database connection string to determine the backend type (SQLite/SpatiaLite or PostgreSQL/PostGIS) and constructs the table definition accordingly. In both cases, the resulting table contains a single `gid` integer column designated as the primary key.

