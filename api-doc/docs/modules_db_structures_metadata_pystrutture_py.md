# modules/db/structures_metadata/pystrutture.py

## Overview

This file contains 3 documented elements.

## Classes

### pystrutture

*No description available.*
Represents archaeological structures or hypotheses within the PyArchInit system, mapping to the `pyarchinit_strutture_ipotesi` database table. The class provides a `define_table` classmethod that dynamically constructs a SQLAlchemy `Table` definition based on the active database backend, distinguishing between SQLite/SpatiaLite and PostgreSQL/PostGIS connections. In the current implementation, both branches define the table with a single primary key column (`gid` of type `Integer`).

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object representing the `pyarchinit_strutture_ipotesi` database table, which stores structures or hypotheses related to archaeological contexts. The method inspects the active database connection string to determine the backend type (SQLite/SpatiaLite or PostgreSQL/PostGIS), branching accordingly, though both branches currently produce a table with a single `gid` integer primary key column. It is a class method that accepts a SQLAlchemy `metadata` object as its sole parameter.

