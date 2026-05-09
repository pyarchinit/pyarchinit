# modules/db/structures_metadata/pyunitastratigrafiche.py

## Overview

This file contains 3 documented elements.

## Classes

### pyunitastratigrafiche

*No description available.*
A vector layer class representing stratigraphic units in archaeological contexts, backed by a corresponding database table of the same name. The class exposes a single class method, `define_table`, which constructs and returns a SQLAlchemy `Table` object bound to the provided `metadata`, defining columns for unit identification (`gid`, `us_s`), site information (`area_s`, `scavo_s`), stratigraphic classification (`stratigraph_index_us`, `tipo_us_s`, `unita_tipo_s`), survey and record metadata (`rilievo_originale`, `disegnatore`, `data`, `tipo_doc`, `coord`), and a `MULTIPOLYGON` geometry column (`the_geom`) via GeoAlchemy2. A unique constraint named `ID_us_unico_s` is enforced on the `gid` column.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object named `'pyunitastratigrafiche'` bound to the provided `metadata`, representing a vector layer of stratigraphic units in archaeological contexts. The table schema includes columns for a primary key (`gid`), excavation site details (`area_s`, `scavo_s`, `us_s`), stratigraphic classification fields (`stratigraph_index_us`, `tipo_us_s`), survey and record metadata (`rilievo_originale`, `disegnatore`, `data`, `tipo_doc`, `coord`, `unita_tipo_s`), and a `MULTIPOLYGON` geometry column (`the_geom`). A unique constraint named `'ID_us_unico_s'` is applied to the `gid` column.

