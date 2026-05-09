# modules/db/structures_metadata/pysito_point.py

## Overview

This file contains 3 documented elements.

## Classes

### pysito_point

*No description available.*
A class representing a vector layer of archaeological site points, mapped to the `pyarchinit_siti` database table. It provides a `define_table` class method that constructs a SQLAlchemy `Table` definition with a primary key column (`gid`) using the supplied `metadata` object. The method inspects the active connection string to differentiate between SQLite/SpatiaLite and PostgreSQL/PostGIS backends, though both branches currently produce the same table structure.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object mapped to the `pyarchinit_siti` database table, adapting its definition based on the active database backend. The method inspects the current connection string to determine whether the target database is SQLite/SpatiaLite or PostgreSQL/PostGIS, then constructs the table accordingly. In both cases, the table is defined with a single `gid` integer primary key column using the provided `metadata` object.

