# modules/db/structures/pycampioni.py

## Overview

This file contains 2 documented elements.

## Classes

### pycampioni

*No description available.*
A data-access class that defines the SQLAlchemy table mapping for the `pyarchinit_campionature` database table. The class declares a `Table` object with columns for sampling record data, including `gid` (primary key), `id_campion`, `sito`, `tipo_camp`, `dataz`, `cronologia`, `link_immag`, `sigla_camp`, and a `POINT` geometry column `the_geom`, with a unique constraint on `gid`. Table creation is intentionally deferred and not triggered at module import time.

