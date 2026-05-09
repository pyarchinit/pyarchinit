# modules/db/structures_metadata/pyquote_usm.py

## Overview

This file contains 3 documented elements.

## Classes

### pyquote_usm

*No description available.*
A SQLAlchemy model class representing the `pyarchinit_quote_usm` vector layer, which stores quote (elevation measurement) data related to archaeological stratigraphic unit contexts (USM). The class exposes a single `define_table` classmethod that constructs and returns a SQLAlchemy `Table` object bound to the provided metadata, with branching logic to handle either SQLite/SpatiaLite or PostgreSQL/PostGIS connection strings. In both cases, the resulting table defines a single `gid` integer primary key column as the unique identifier for each quote record.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object for the `pyarchinit_quote_usm` table using the provided `metadata` instance. The method inspects the active database connection string to determine the target database backend (SQLite/SpatiaLite or PostgreSQL/PostGIS) and constructs the table definition accordingly. In both cases, the resulting table contains a single `gid` integer column designated as the primary key.

