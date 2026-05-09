# modules/db/structures_metadata/pyquote.py

## Overview

This file contains 3 documented elements.

## Classes

### pyquote

*No description available.*
A SQLAlchemy table definition class representing the `pyarchinit_quote` vector layer, which stores quote records related to archaeological contexts. The `define_table` class method constructs and returns a `Table` object bound to the provided `metadata`, adapting its definition based on the active database backend (SQLite/SpatiaLite or PostgreSQL/PostGIS). In both cases, the table is defined with a single `gid` integer primary key column as the unique identifier for each quote record.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object for the `pyarchinit_quote` table using the provided `metadata` instance. The method inspects the active database connection string to determine the backend type, branching between SQLite/SpatiaLite and PostgreSQL/PostGIS configurations. In both cases, the resulting table definition includes a single `gid` integer primary key column.

