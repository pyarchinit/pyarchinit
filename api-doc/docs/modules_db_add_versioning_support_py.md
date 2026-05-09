# modules/db/add_versioning_support.py

## Overview

This file contains 7 documented elements.

## Classes

### VersioningSupport

Add versioning support to database tables

#### Methods

##### __init__(self)

Initializes a new `VersioningSupport` instance by establishing a database connection and configuring the SQLAlchemy components required for versioning operations. Sets up a `Connection` object, creates a SQLAlchemy engine using the connection string with echo disabled, and initializes a `MetaData` instance along with a database inspector bound to the engine.

##### get_all_tables(self)

Get all tables that need versioning support

##### add_versioning_columns(self, table_name)

Add versioning columns to a table

##### update_all_tables(self)

Update all tables with versioning support

## Functions

### main()

Main function to add versioning support

