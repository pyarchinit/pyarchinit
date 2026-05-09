# modules/db/structures/pysito_polygon.py

## Overview

This file contains 2 documented elements.

## Classes

### pysito_polygon

*No description available.*
Maps the `pyarchinit_siti_polygonal` database table using SQLAlchemy's `Table` construct with GeoAlchemy2 geometry support. The table schema defines three columns: `gid` (integer primary key with a unique constraint), `sito_id` (text), and `the_geom` (a `POLYGON` geometry type). Table creation at module import time is explicitly disabled to prevent connection errors.

