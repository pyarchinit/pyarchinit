# modules/db/structures/pyreperti.py

## Overview

This file contains 2 documented elements.

## Classes

### pyreperti

*No description available.*
A data-access class that defines the SQLAlchemy table mapping for the `pyarchinit_reperti` database table, which stores archaeological find (reperto) records with spatial point geometry. The table schema includes columns for a primary key (`gid`), a find identifier (`id_rep`), a site reference (`siti`), a link field (`link`), and a PostGIS `POINT` geometry column (`the_geom`), with a unique constraint on `gid`. Table creation is deferred and not executed at module import time.

