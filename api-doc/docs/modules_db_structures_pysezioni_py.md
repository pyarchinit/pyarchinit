# modules/db/structures/pysezioni.py

## Overview

This file contains 2 documented elements.

## Classes

### pysezioni

*No description available.*
A SQLAlchemy table-mapping class that defines the schema for the `pyarchinit_sezioni` database table, which stores archaeological section (sezione) geometries and their associated metadata. The table schema includes columns for a primary key (`gid`), section identifier (`id_sezione`), site (`sito`), area (`area`), description (`descr`), and a PostGIS `LINESTRING` geometry column (`the_geom`), with a unique constraint enforced on `gid`. Table creation is deferred and not executed at module import time.

