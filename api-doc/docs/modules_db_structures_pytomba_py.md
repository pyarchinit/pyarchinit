# modules/db/structures/pytomba.py

## Overview

This file contains 2 documented elements.

## Classes

### pytomba

*No description available.*
A data-access class that defines the SQLAlchemy table mapping for the `pyarchinit_tafonomia` database table, which stores taphonomic (burial/tomb) records within the pyArchInit system. The table schema includes a primary key integer column (`gid`), a site identifier (`sito`), a record number (`nr_scheda`), and a PostGIS `POINT` geometry column (`the_geom`), with a unique constraint enforced on `gid`. Table creation is intentionally deferred from module import time to avoid premature database connection errors.

