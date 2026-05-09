# modules/db/structures/pylineeriferimento.py

## Overview

This file contains 2 documented elements.

## Classes

### pylineeriferimento

*No description available.*
A data-access class that defines the ORM table mapping for `pyarchinit_linee_rif`, a spatial database table storing reference lines within the pyArchInit archaeological information system. The class declares a SQLAlchemy `Table` object with columns for a primary key (`gid`), site name (`sito`), definition (`definizion`), description (`descrizion`), and a `LINESTRING` geometry column (`the_geom`), along with a unique constraint on `gid`. Database connection is managed via the `Connection` class from `modules.db.pyarchinit_conn_strings`, and table creation is intentionally deferred from module import time.

