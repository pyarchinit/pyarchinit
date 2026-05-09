# modules/db/structures_metadata/pysezioni.py

## Overview

This file contains 3 documented elements.

## Classes

### pysezioni

*No description available.*
A class representing the vector layer for archaeological sections (`pyarchinit_sezioni`) within a spatial database schema. It provides a `define_table` class method that dynamically constructs the corresponding SQLAlchemy `Table` object based on the active database backend, distinguishing between SQLite/SpatiaLite and PostgreSQL/PostGIS connections. In both cases, the table is defined with a single `gid` integer primary key column as documented in the source.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object for the `pyarchinit_sezioni` table using the supplied `metadata` instance. The method inspects the active database connection string to determine the backend type, branching between SQLite/SpatiaLite and PostgreSQL/PostGIS, though both branches currently produce a table with a single `gid` integer primary key column. This is a class method of `pysezioni`, a vector layer class representing sections in archaeological contexts.

