# modules/db/structures_metadata/pyreperti.py

## Overview

This file contains 3 documented elements.

## Classes

### pyreperti

*No description available.*
A SQLAlchemy table-definition class representing the `pyarchinit_reperti` vector layer, which stores artifacts or finds in archaeological contexts. The class exposes a single `define_table` classmethod that inspects the active database connection string and returns a `Table` object mapped to `pyarchinit_reperti`, with a `gid` integer primary key column, for either SQLite/SpatiaLite or PostgreSQL/PostGIS backends. Both database branches currently define only the `gid` column; additional geometry and attribute columns are not documented in source.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object for the `pyarchinit_reperti` table using the provided `metadata` instance. The method inspects the active database connection string to determine the backend type, branching between SQLite/SpatiaLite and PostgreSQL/PostGIS configurations, though both branches currently produce a table with a single `gid` integer primary key column. This is a class method intended to support schema definition for the `pyreperti` vector layer representing archaeological artifacts or finds.

