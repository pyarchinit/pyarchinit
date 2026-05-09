# modules/db/structures/pysito_point.py

## Overview

This file contains 2 documented elements.

## Classes

### pysito_point

*No description available.*
A SQLAlchemy table-mapping class that defines the schema for the `pyarchinit_siti` database table, which stores archaeological site data as point geometries. The class declares a `MetaData` instance and a `Table` object with three columns: `gid` (integer primary key with a unique constraint), `sito_nome` (text site name), and `the_geom` (a GeoAlchemy2 `POINT` geometry column). Table creation is intentionally deferred and not executed at module import time.

