# modules/db/structures_metadata/Tomba_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Tomba_table

*No description available.*
A SQLAlchemy table definition class representing archaeological tomb records. It exposes a single class method, `define_table`, which constructs and returns a `Table` object named `'tomba_table'` bound to the provided `metadata`, containing columns for tomb identification, excavation context, burial characteristics, grave goods, chronological data, and a StratiGraph UUID. A `UniqueConstraint` named `'ID_tomba_unico'` enforces uniqueness across the combination of `sito` (site name) and `nr_scheda_taf` (record sheet number).

#### Methods

##### define_table(cls, metadata)

*No description available.*
A class method that defines and returns a SQLAlchemy `Table` object named `'tomba_table'` bound to the provided `metadata` instance. The table schema represents archaeological tomb records and includes columns for site identification, excavation area, structural references, burial rite details, grave goods, preservation state, chronological periods, and a StratiGraph UUID. A `UniqueConstraint` named `'ID_tomba_unico'` enforces uniqueness on the combination of `sito` and `nr_scheda_taf` columns.

