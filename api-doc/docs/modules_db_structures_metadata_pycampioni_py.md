# modules/db/structures_metadata/pycampioni.py

## Overview

This file contains 3 documented elements.

## Classes

### pycampioni

*No description available.*
Defines the database table structure for archaeological sampling records within the `pyarchinit` system. The class exposes a single class method, `define_table`, which constructs and returns a SQLAlchemy `Table` object named `pyarchinit_campionature` bound to the provided metadata, with a primary key column `gid` of type `Integer`. The method inspects the active connection string to differentiate between SQLite/SpatiaLite and PostgreSQL/PostGIS backends, though both branches produce the same table definition in the current implementation.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object for the `pyarchinit_campionature` table using the provided `metadata` argument. The method inspects the active connection string to determine the database backend, branching between SQLite/Spatialite and PostgreSQL/PostGIS configurations. In both cases, the resulting table includes a single `gid` integer primary key column representing the unique identifier for each sample record.

