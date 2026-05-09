# modules/db/structures_metadata/Pottery_table.py

## Overview

This file contains 3 documented elements.

## Classes

### PotteryTable

*No description available.*
Defines the SQLAlchemy table schema for recording archaeological pottery finds and their associated attributes. The class exposes a single class method, `define_table`, which constructs and returns a `Table` object named `'pottery_table'` bound to the provided `metadata`, comprising columns for site identification, stratigraphic context, physical measurements (`Numeric(7, 3)`), typological classifications, decoration details, and a StratiGraph UUID. A `UniqueConstraint` named `'ID_rep_unico'` enforces uniqueness across the combination of `sito` and `id_number`.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object named `'pottery_table'` bound to the provided `metadata`, representing archaeological pottery finds and their characteristics. The table includes columns for site identification (`sito`, `id_number`, `us`, `area`, `sector`), physical attributes (`fabric`, `material`, `form`, `ware`, `munsell`), measurements (`diametro_max`, `diametro_rim`, `diametro_bottom`, `diametro_height`, `diametro_preserved`), decoration details (`exdeco`, `intdeco`, `decoration_type`, `decoration_motif`, `decoration_position`), and administrative fields (`photo`, `drawing`, `note`, `entity_uuid`). A `UniqueConstraint` named `'ID_rep_unico'` enforces uniqueness on the combination of `sito` and `id_number`, while `id_rep` serves as the primary key.

