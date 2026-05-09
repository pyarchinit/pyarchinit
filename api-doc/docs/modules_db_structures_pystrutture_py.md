# modules/db/structures/pystrutture.py

## Overview

This file contains 2 documented elements.

## Classes

### pystrutture

*No description available.*
Defines the ORM-style table mapping for the `pyarchinit_strutture_ipotesi` database table, which stores hypothetical structural data associated with archaeological sites. The table schema includes columns for site identification (`sito`), structure identifiers (`id_strutt`, `sigla_strut`, `nr_strut`), chronological range fields (`per_iniz`, `per_fin`, `fase_iniz`, `fase_fin`, `dataz_ext`), a textual description, and a polygon geometry column (`the_geom`) managed via GeoAlchemy2. A unique constraint is defined on the primary key column `gid`.

